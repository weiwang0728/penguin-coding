"""Tests for LLM compact functionality in compact.py"""

import pytest

from src.compact import (
    COLLAPSE_SYSTEM_PROMPT,
    COMPACT_SYSTEM_PROMPT,
    MAX_TOOL_RESULT_TOKENS,
    _compact_oversized_blocks,
    _context_collapse,
    _head_tail_truncate,
    _serialize_messages,
    _strip_old_thinking,
    _verify_tokens_within_budget,
    estimate_messages_tokens,
    estimate_tokens,
    llm_compact_messages,
    trim_messages,
)


# --- estimate_tokens ---


class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_pure_ascii(self):
        # "hello world" = 11 chars → 11/4 ≈ 2.75 → 2
        assert estimate_tokens("hello world") == 2

    def test_pure_cjk(self):
        # 10 CJK chars → 10 * 1.5 = 15
        assert estimate_tokens("你好世界代码编写测试") == 15

    def test_mixed_cjk_and_ascii(self):
        # "你好hello" = 2 CJK + 5 ASCII
        # CJK: 2 * 1.5 = 3, ASCII: 5/4 = 1.25 → total ≈ 4
        assert estimate_tokens("你好hello") == 4

    def test_cjk_higher_than_old_method(self):
        """CJK text should estimate more tokens than len//4."""
        text = "这是一段中文文本"
        assert estimate_tokens(text) > len(text) // 4


# --- _verify_tokens_within_budget ---


class FakeCountTokensClient:
    """Mock client with count_tokens support."""
    def __init__(self, token_count: int):
        self._token_count = token_count
        self.messages = self._Messages(self._token_count)

    class _Messages:
        def __init__(self, token_count: int):
            self._token_count = token_count

        def count_tokens(self, **kwargs):
            return type("Resp", (), {"input_tokens": self._token_count})()


class FailingCountTokensClient:
    """Mock client where count_tokens raises."""
    def __init__(self):
        self.messages = self._Messages()

    class _Messages:
        def count_tokens(self, **kwargs):
            raise RuntimeError("API unavailable")


class TestVerifyTokensWithinBudget:
    def test_within_budget(self):
        client = FakeCountTokensClient(5000)
        assert _verify_tokens_within_budget([], client, "model", 10000) is True

    def test_over_budget(self):
        client = FakeCountTokensClient(15000)
        assert _verify_tokens_within_budget([], client, "model", 10000) is False

    def test_api_failure_trusts_estimate(self):
        client = FailingCountTokensClient()
        # Should return True (trust the estimate) when API fails
        assert _verify_tokens_within_budget([], client, "model", 10000) is True


# --- _head_tail_truncate ---


class TestHeadTailTruncate:
    def test_short_text_unchanged(self):
        assert _head_tail_truncate("hello", 100) == "hello"

    def test_truncation_preserves_head_and_tail(self):
        text = "A" * 4000 + "B" * 4000
        result = _head_tail_truncate(text, 4000)
        assert result.startswith("A" * 2000)
        assert result.endswith("B" * 2000)
        assert "Truncated" in result
        assert "8000 chars total" in result

    def test_exact_length_not_truncated(self):
        text = "x" * 4000
        assert _head_tail_truncate(text, 4000) == text


# --- _compact_oversized_blocks ---


class TestCompactOversizedBlocks:
    def test_tool_result_head_tail_truncation(self):
        """tool_result should use head+tail truncation."""
        long_content = "A" * 10000 + "Z" * 10000
        msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": long_content},
            ],
        }
        result = _compact_oversized_blocks(msg)
        result_content = result["content"][0]["content"]
        assert "A" in result_content[:100]
        assert "Z" in result_content[-100:]
        assert "Truncated" in result_content

    def test_tool_result_nested_text_head_tail(self):
        """Nested text blocks in tool_result should use head+tail."""
        long_text = "H" * 10000 + "T" * 10000
        msg = {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "t1",
                    "content": [{"type": "text", "text": long_text}],
                },
            ],
        }
        result = _compact_oversized_blocks(msg)
        text_block = result["content"][0]["content"][0]["text"]
        assert "H" in text_block[:100]
        assert "T" in text_block[-100:]
        assert "Truncated" in text_block

    def test_text_block_not_truncated(self):
        """text blocks should NOT be truncated regardless of size."""
        long_text = "x" * 50000
        msg = {
            "role": "assistant",
            "content": [{"type": "text", "text": long_text}],
        }
        result = _compact_oversized_blocks(msg)
        assert result == msg

    def test_tool_use_not_truncated(self):
        """tool_use blocks should never be modified."""
        msg = {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "x" * 10000}},
            ],
        }
        result = _compact_oversized_blocks(msg)
        assert result == msg

    def test_thinking_not_truncated(self):
        """thinking blocks should NOT be truncated here (handled by _strip_old_thinking)."""
        long_thinking = "think" * 10000
        msg = {
            "role": "assistant",
            "content": [{"type": "thinking", "thinking": long_thinking}],
        }
        result = _compact_oversized_blocks(msg)
        assert result == msg

    def test_image_replaced_with_placeholder(self):
        """image blocks in tool_result should be replaced."""
        msg = {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "t1",
                    "content": [{"type": "image", "source": {"data": "big"}}],
                },
            ],
        }
        result = _compact_oversized_blocks(msg)
        sub_blocks = result["content"][0]["content"]
        assert any("[Image removed due to size]" in b.get("text", "") for b in sub_blocks)

    def test_small_tool_result_unchanged(self):
        """tool_result under threshold should not be modified."""
        msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "small"},
            ],
        }
        assert _compact_oversized_blocks(msg) == msg

    def test_string_content_not_truncated(self):
        """Plain string content is not a tool_result block, should not be truncated."""
        long_content = "A" * 50000
        msg = {"role": "user", "content": long_content}
        assert _compact_oversized_blocks(msg) == msg


# --- _strip_old_thinking ---


class TestStripOldThinking:
    def test_old_thinking_removed(self):
        """Non-recent thinking blocks should be fully removed."""
        messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "old thought"},
                {"type": "text", "text": "reply"},
            ]},
            {"role": "user", "content": "more"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "recent thought"},
                {"type": "text", "text": "recent reply"},
            ]},
        ]
        result = _strip_old_thinking(messages)
        # First assistant should have thinking removed
        assert not any(b.get("type") == "thinking" for b in result[1]["content"])
        # Last assistant should keep thinking intact
        assert any(b.get("type") == "thinking" for b in result[3]["content"])
        thinking_block = [b for b in result[3]["content"] if b.get("type") == "thinking"][0]
        assert thinking_block["thinking"] == "recent thought"

    def test_keep_recent_default_is_one(self):
        """By default, only the most recent assistant thinking is preserved."""
        messages = [
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "t1"},
                {"type": "text", "text": "a1"},
            ]},
            {"role": "user", "content": "q2"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "t2"},
                {"type": "text", "text": "a2"},
            ]},
        ]
        result = _strip_old_thinking(messages)
        thinking_blocks = [
            b for m in result if m.get("role") == "assistant"
            for b in m.get("content", [])
            if isinstance(b, dict) and b.get("type") == "thinking"
        ]
        assert len(thinking_blocks) == 1
        assert thinking_blocks[0]["thinking"] == "t2"

    def test_no_assistant_messages(self):
        """Should handle messages with no assistant turns."""
        messages = [{"role": "user", "content": "hello"}]
        assert _strip_old_thinking(messages) == messages


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


# --- _context_collapse ---


class FakeCollapseClient:
    """Mock client that returns a structured collapse log."""
    def __init__(self, collapse_text: str):
        self._collapse_text = collapse_text
        self.messages = self._Messages(self._collapse_text)

    class _Messages:
        def __init__(self, collapse_text: str):
            self._collapse_text = collapse_text
            self.last_call = None

        def create(self, **kwargs):
            self.last_call = kwargs
            return type("Resp", (), {
                "content": [type("Block", (), {"type": "text", "text": self._collapse_text})()]
            })()

        def count_tokens(self, **kwargs):
            return type("Resp", (), {"input_tokens": 500})()


class TestContextCollapse:
    def test_collapses_to_structured_log(self):
        messages = [{"role": "user", "content": "Start"}]
        for i in range(20):
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"t{i}", "name": "read_file", "input": {"path": f"f{i}.py"}},
            ]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": "data" * 500},
            ]})

        collapse_text = (
            "Turn 1-10: Read multiple files\n"
            "Turn 11-20: Made changes\n"
            "Files modified: f0.py, f10.py\n"
            "Current state: In progress"
        )
        client = FakeCollapseClient(collapse_text)

        result = _context_collapse(messages, client, "model-id", max_tokens=10000)

        # Result should be collapse_msg + ack_msg (2 messages)
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert "Context collapsed" in result[0]["content"]
        assert "20 turns" in result[0]["content"]
        assert collapse_text in result[0]["content"]
        assert result[1]["role"] == "assistant"
        assert "Context collapsed" in result[1]["content"]

    def test_receives_collapse_system_prompt(self):
        messages = [{"role": "user", "content": "q"}, {"role": "assistant", "content": "a"}]
        client = FakeCollapseClient("Turn 1: did stuff")

        _context_collapse(messages, client, "model-id", max_tokens=10000)

        call_kwargs = client.messages.last_call
        assert call_kwargs is not None
        assert call_kwargs["system"] == COLLAPSE_SYSTEM_PROMPT

    def test_api_failure_returns_original(self):
        client = FailingClient()
        messages = [{"role": "user", "content": "q"}, {"role": "assistant", "content": "a"}]
        result = _context_collapse(messages, client, "model-id", max_tokens=10000)
        assert result == messages

    def test_single_message_returns_as_is(self):
        messages = [{"role": "user", "content": "hello"}]
        client = FakeCollapseClient("no collapse needed")
        result = _context_collapse(messages, client, "model-id", max_tokens=10000)
        assert result == messages


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

        # First message is original user message, second is standalone summary
        assert result[0]["role"] == "user"
        assert "Start" in result[0].get("content", "")
        assert result[1]["role"] == "user"
        assert "Conversation Summary" in result[1]["content"]
        assert fake_summary in result[1]["content"]

        # Recent messages should be preserved intact
        assert len(result) < len(messages)

    def test_llm_summary_is_standalone_message(self):
        """Summary should be a standalone user message, not merged into first message."""
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

        # First message should be unchanged original
        assert isinstance(result[0]["content"], list)
        # Summary is a separate message
        assert result[1]["role"] == "user"
        assert "Conversation Summary" in result[1]["content"]

    def test_fallback_on_api_failure_returns_preprocessed(self):
        """When LLM call fails, should return preprocessed messages (no rule-based fallback)."""
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
        # Should return preprocessed result — may be over budget but tool_results truncated
        assert len(result) > 0
        assert result[0]["role"] == "user"

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

    def test_llm_result_over_budget_returns_preprocessed(self):
        """If LLM summary + recent messages still exceed budget, returns preprocessed result."""
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
        # Should return preprocessed messages — may be over budget
        assert len(result) > 0


# --- trim_messages (preprocessing-only) ---


class TestTrimMessages:
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

    def test_over_budget_returns_preprocessed(self):
        """When over budget, trim_messages returns preprocessed result
        (it does not do LLM compaction or rule-based trimming)."""
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
                            "content": "x" * 20000,
                        }
                    ],
                }
            )

        result = trim_messages(messages, max_tokens=3000)
        # Should return preprocessed result even if over budget
        assert len(result) > 0
        # Large tool_results should have been truncated via head+tail
        for msg in result:
            if isinstance(msg.get("content"), list):
                for block in msg["content"]:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        rc = block.get("content", "")
                        assert "Truncated" in rc
