"""Tests for LLM compact functionality in compact.py"""

import pytest

from compact import (
    COMPACT_SYSTEM_PROMPT,
    _serialize_messages,
    estimate_messages_tokens,
    llm_compact_messages,
    trim_messages,
)


# --- _serialize_messages ---


class TestSerializeMessages:
    def test_string_content(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi there"},
        ]
        text = _serialize_messages(messages)
        assert "[user]: hello" in text
        assert "[assistant]: hi there" in text

    def test_list_content_text(self):
        messages = [
            {"role": "assistant", "content": [{"type": "text", "text": "response"}]},
        ]
        text = _serialize_messages(messages)
        assert "[assistant]: response" in text

    def test_list_content_tool_use(self):
        messages = [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "t1",
                        "name": "read_file",
                        "input": {"path": "main.py"},
                    }
                ],
            }
        ]
        text = _serialize_messages(messages)
        assert "read_file" in text
        assert "main.py" in text

    def test_list_content_tool_result_string(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "file content here"},
                ],
            }
        ]
        text = _serialize_messages(messages)
        assert "file content here" in text

    def test_list_content_tool_result_list(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "t1",
                        "content": [{"type": "text", "text": "nested result"}],
                    },
                ],
            }
        ]
        text = _serialize_messages(messages)
        assert "nested result" in text

    def test_empty_messages(self):
        assert _serialize_messages([]) == ""

    def test_non_dict_blocks_ignored(self):
        messages = [{"role": "user", "content": ["not a dict", 42]}]
        text = _serialize_messages(messages)
        assert text == ""

    def test_long_tool_result_truncated(self):
        long_content = "x" * 2000
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": long_content},
                ],
            }
        ]
        text = _serialize_messages(messages)
        assert len(text) < len(long_content)


# --- Mock client for LLM compact tests ---


class FakeMessage:
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class FakeResponse:
    def __init__(self, summary: str):
        self.content = [FakeMessage(summary)]


class FakeClient:
    """Mock anthropic client that returns a canned summary."""

    def __init__(self, summary: str = "Summary of conversation."):
        self.messages = self._Messages(summary)

    class _Messages:
        def __init__(self, summary: str):
            self._summary = summary
            self.last_call = None

        def create(self, **kwargs):
            self.last_call = kwargs
            return FakeResponse(self._summary)


class FailingClient:
    """Mock client that raises on API call."""

    class _Messages:
        def create(self, **kwargs):
            raise RuntimeError("API unavailable")

    def __init__(self):
        self.messages = self._Messages()


# --- llm_compact_messages ---


class TestLlmCompactMessages:
    def test_empty_messages(self):
        result = llm_compact_messages([], FakeClient(), "model-id")
        assert result == []

    def test_within_budget_no_compaction(self):
        messages = [
            {"role": "user", "content": "short"},
            {"role": "assistant", "content": "reply"},
        ]
        result = llm_compact_messages(messages, FakeClient(), "model-id", max_tokens=100000)
        # No compaction needed, should pass through preprocessing only
        assert len(result) >= 2

    def test_llm_summary_replaces_old_messages(self):
        """When over budget, old messages should be replaced by a summary."""
        fake_summary = "- User asked to read main.py\n- Assistant read the file successfully"
        client = FakeClient(summary=fake_summary)

        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "read_file",
                            "input": {"path": f"file{i}.py"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "x" * 5000,
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=3000, keep_recent=4)

        # First message should contain the summary
        first_content = result[0]["content"]
        assert "Conversation Summary" in first_content
        assert fake_summary in first_content

        # Recent messages should be preserved intact
        assert len(result) < len(messages)

    def test_llm_summary_in_list_content(self):
        """When first message has list content, summary should be appended as a text block."""
        fake_summary = "Summary here"
        client = FakeClient(summary=fake_summary)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Initial prompt"},
                ],
            }
        ]
        for i in range(8):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "read_file",
                            "input": {"path": f"f{i}.py"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "y" * 5000,
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=3000, keep_recent=4)

        first_content = result[0]["content"]
        assert isinstance(first_content, list)
        text_blocks = [b for b in first_content if isinstance(b, dict) and b.get("type") == "text"]
        combined = " ".join(b.get("text", "") for b in text_blocks)
        assert "Conversation Summary" in combined

    def test_fallback_on_api_failure(self):
        """When LLM call fails, should fall back to rule-based trimming."""
        client = FailingClient()

        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "read_file",
                            "input": {"path": f"file{i}.py"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "x" * 5000,
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=3000)
        total = estimate_messages_tokens(result)
        assert total <= 3500  # Should be within budget (with small overhead)

    def test_maintains_alternation(self):
        """Result messages should have proper user/assistant alternation."""
        fake_summary = "Summary"
        client = FakeClient(summary=fake_summary)

        messages = [{"role": "user", "content": "Start"}]
        for i in range(8):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "write_file",
                            "input": {"path": f"f{i}.py", "content": "code"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "OK",
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=3000, keep_recent=4)

        for j in range(len(result)):
            expected = "user" if j % 2 == 0 else "assistant"
            assert result[j]["role"] == expected, (
                f"Message {j}: expected {expected}, got {result[j]['role']}"
            )

    def test_recent_messages_preserved(self):
        """Recent messages should be kept intact with original structure."""
        fake_summary = "Summary of old conversation"
        client = FakeClient(summary=fake_summary)

        messages = [{"role": "user", "content": "Start"}]
        for i in range(8):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": f"Step {i}"},
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "read_file",
                            "input": {"path": f"file{i}.py"},
                        },
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": f"content_{i} " * 500,
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=5000, keep_recent=4)

        # Last assistant should have original list structure
        last_assistant = [m for m in result if m["role"] == "assistant"][-1]
        assert isinstance(last_assistant["content"], list)
        assert any(b.get("type") == "tool_use" for b in last_assistant["content"])

    def test_llm_client_receives_correct_prompt(self):
        """Verify the LLM client gets the right system prompt and user message."""
        fake_summary = "Summary"
        client = FakeClient(summary=fake_summary)

        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "read_file",
                            "input": {"path": f"f{i}.py"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "data" * 500,
                        }
                    ],
                }
            )

        llm_compact_messages(messages, client, "test-model", max_tokens=3000, keep_recent=4)

        call_kwargs = client.messages.last_call
        assert call_kwargs is not None
        assert call_kwargs["model"] == "test-model"
        assert call_kwargs["system"] == COMPACT_SYSTEM_PROMPT
        # The user message should contain the serialized old conversation
        user_msg = call_kwargs["messages"][0]
        assert user_msg["role"] == "user"
        assert "Summarize this conversation" in user_msg["content"]

    def test_preserves_first_message(self):
        """First message should always be preserved."""
        fake_summary = "Summary"
        client = FakeClient(summary=fake_summary)

        messages = [{"role": "user", "content": "Important start"}]
        for i in range(8):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "run_command",
                            "input": {"command": f"echo {i}"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "x" * 5000,
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=3000)
        first = result[0]
        assert first["role"] == "user"
        assert "Important start" in first.get("content", "")

    def test_llm_result_over_budget_falls_back(self):
        """If LLM summary + recent messages still exceed budget, fall back to rule-based."""
        # Use a very long summary that itself exceeds budget
        huge_summary = "x" * 100000
        client = FakeClient(summary=huge_summary)

        messages = [{"role": "user", "content": "Start"}]
        for i in range(8):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "read_file",
                            "input": {"path": f"f{i}.py"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "data",
                        }
                    ],
                }
            )

        result = llm_compact_messages(messages, client, "model-id", max_tokens=3000)
        total = estimate_messages_tokens(result)
        # Should have fallen back to rule-based and be within budget
        assert total <= 3500


# --- Existing trim_messages still works ---


class TestTrimMessagesStillWorks:
    def test_no_trimming_needed(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        assert trim_messages(messages) == messages

    def test_preserves_first_message(self):
        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append(
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": f"t{i}",
                            "name": "run_command",
                            "input": {"command": f"echo {i}"},
                        }
                    ],
                }
            )
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": f"t{i}",
                            "content": "x" * 5000,
                        }
                    ],
                }
            )

        result = trim_messages(messages, max_tokens=3000)
        assert result[0] == messages[0]
