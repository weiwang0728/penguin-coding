"""Unit tests for agent_loop.py and compact.py"""

import pytest

import src.agent_loop as agent_loop_module
from src.compact import (
    _compact_oversized_blocks,
    _strip_old_thinking,
    estimate_messages_tokens,
    estimate_tokens,
    trim_messages,
)
from src.agent_loop import _repair_json


# --- estimate_tokens ---

class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_short_string(self):
        assert estimate_tokens("hello world") == 2  # 11 // 4

    def test_long_string(self):
        assert estimate_tokens("a" * 400) == 100

    def test_single_char(self):
        assert estimate_tokens("x") == 1


# --- estimate_messages_tokens ---

class TestEstimateMessagesTokens:
    def test_string_content(self):
        messages = [{"role": "user", "content": "hello"}]
        tokens = estimate_messages_tokens(messages)
        assert tokens > 0

    def test_list_content_text(self):
        messages = [{"role": "assistant", "content": [{"type": "text", "text": "hi"}]}]
        tokens = estimate_messages_tokens(messages)
        assert tokens > 0

    def test_list_content_tool_use(self):
        messages = [
            {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "x.py"}},
                ],
            }
        ]
        tokens = estimate_messages_tokens(messages)
        assert tokens > 0

    def test_list_content_tool_result(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "file content"},
                ],
            }
        ]
        tokens = estimate_messages_tokens(messages)
        assert tokens > 0

    def test_tool_result_list_content(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": [{"text": "nested"}]},
                ],
            }
        ]
        tokens = estimate_messages_tokens(messages)
        assert tokens > 0

    def test_empty_messages(self):
        assert estimate_messages_tokens([]) == 0

    def test_non_dict_blocks_ignored(self):
        messages = [{"role": "user", "content": ["not a dict", 42]}]
        tokens = estimate_messages_tokens(messages)
        assert tokens == 0


# --- trim_messages ---

class TestTrimMessages:
    def test_no_trimming_needed(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
        assert trim_messages(messages) == messages

    def test_empty_messages(self):
        assert trim_messages([]) == []

    def test_preserves_first_message(self):
        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"t{i}", "name": "run_command", "input": {"command": f"echo {i}"}},
            ]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 5000},
            ]})

        result = trim_messages(messages, max_tokens=3000)
        assert result[0] == messages[0]

    def test_truncates_oversized_tool_results(self):
        """Large tool_results should be head+tail truncated by preprocessing."""
        messages = [
            {"role": "user", "content": "Read this"},
            {"role": "assistant", "content": [
                {"type": "tool_use", "id": "t0", "name": "read_file", "input": {"path": "big.py"}},
            ]},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t0", "content": "A" * 20000 + "Z" * 20000},
            ]},
        ]
        result = trim_messages(messages, max_tokens=1000)
        # Tool result should be truncated with head+tail
        tool_msg = result[2]
        rc = tool_msg["content"][0]["content"]
        assert "Truncated" in rc
        assert "A" in rc[:200]
        assert "Z" in rc[-200:]

    def test_over_budget_returns_preprocessed(self):
        """When over budget, trim_messages returns preprocessed result (no LLM, no rule-based)."""
        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"t{i}", "name": "read_file", "input": {"path": f"f{i}.py"}},
            ]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 5000},
            ]})

        result = trim_messages(messages, max_tokens=3000)
        # Should return all messages (preprocessed, tool_results truncated)
        assert len(result) == len(messages)
        assert result[0] == messages[0]


# --- _compact_oversized_blocks ---

class TestCompactOversizedBlocks:
    def test_small_message_unchanged(self):
        msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "small result"},
            ],
        }
        result = _compact_oversized_blocks(msg)
        assert result == msg

    def test_large_tool_result_truncated(self):
        msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "x" * 100_000},
            ],
        }
        result = _compact_oversized_blocks(msg)
        assert result is not msg
        block = result["content"][0]
        assert "Truncated" in block["content"]
        assert len(block["content"]) < 100_000

    def test_string_content_unchanged(self):
        msg = {"role": "assistant", "content": "just text"}
        assert _compact_oversized_blocks(msg) == msg

    def test_mixed_blocks_only_truncates_large(self):
        msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "small"},
                {"type": "tool_result", "tool_use_id": "t2", "content": "y" * 100_000},
            ],
        }
        result = _compact_oversized_blocks(msg)
        blocks = result["content"]
        assert blocks[0]["content"] == "small"  # unchanged
        assert "Truncated" in blocks[1]["content"]  # truncated

    def test_trimming_applies_oversized_block_compression_first(self):
        messages = [
            {"role": "user", "content": "Start"},
            {"role": "assistant", "content": [
                {"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "big.py"}},
            ]},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "x" * 80_000},
            ]},
            {"role": "assistant", "content": "Done"},
        ]
        result = trim_messages(messages, max_tokens=5000)
        # The oversized tool_result should have been truncated,
        # so the whole conversation should fit without needing full compaction
        total = estimate_messages_tokens(result)
        assert total <= 5000 + 500


# --- _strip_old_thinking ---

class TestStripOldThinking:
    def test_removes_old_thinking_keeps_recent(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "old long reasoning " * 200},
                {"type": "text", "text": "old answer"},
            ]},
            {"role": "user", "content": "next question"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "recent reasoning " * 200},
                {"type": "text", "text": "recent answer"},
            ]},
            {"role": "user", "content": "another question"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "newest reasoning " * 200},
                {"type": "text", "text": "newest answer"},
            ]},
        ]
        result = _strip_old_thinking(messages, keep_recent=2)
        # 第一个 assistant 的 thinking 应被移除
        old_asst = result[1]
        assert all(b.get("type") != "thinking" for b in old_asst["content"])
        # 最近两个 assistant 的 thinking 应保留
        recent_asst = result[3]
        assert any(b.get("type") == "thinking" for b in recent_asst["content"])
        newest_asst = result[5]
        assert any(b.get("type") == "thinking" for b in newest_asst["content"])

    def test_recent_thinking_kept_intact(self):
        long_thinking = "x" * 2000
        messages = [
            {"role": "user", "content": "q"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": long_thinking},
                {"type": "text", "text": "answer"},
            ]},
        ]
        result = _strip_old_thinking(messages, keep_recent=1)
        thinking_block = [b for b in result[1]["content"] if b.get("type") == "thinking"][0]
        # Recent thinking should be kept intact, not truncated
        assert thinking_block["thinking"] == long_thinking

    def test_no_thinking_blocks_unchanged(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "just text"},
        ]
        assert _strip_old_thinking(messages) == messages

    def test_empty_messages(self):
        assert _strip_old_thinking([]) == []


# --- _repair_json ---

class TestRepairJson:
    def test_valid_json(self):
        assert _repair_json('{"key": "value"}') == {"key": "value"}

    def test_missing_closing_brace(self):
        result = _repair_json('{"key": "value"')
        assert isinstance(result, dict)
        assert result.get("key") == "value"

    def test_missing_opening_brace(self):
        result = _repair_json('"key": "value"}')
        assert isinstance(result, dict)

    def test_trailing_comma(self):
        result = _repair_json('{"key": "value",}')
        assert isinstance(result, dict)
        assert result.get("key") == "value"

    def test_completely_broken_returns_empty(self):
        result = _repair_json("}{][")
        assert isinstance(result, dict)


# --- _validate_config ---

class TestValidateConfig:
    def test_missing_model_id(self, monkeypatch):
        monkeypatch.setattr(agent_loop_module, "MODEL_ID", None)
        monkeypatch.setattr(agent_loop_module, "API_KEY", "test-key")
        with pytest.raises(EnvironmentError, match="MODEL_ID"):
            agent_loop_module._validate_config()

    def test_missing_api_key(self, monkeypatch):
        monkeypatch.setattr(agent_loop_module, "MODEL_ID", "test-model")
        monkeypatch.setattr(agent_loop_module, "API_KEY", None)
        with pytest.raises(EnvironmentError, match="API_KEY"):
            agent_loop_module._validate_config()

    def test_both_missing(self, monkeypatch):
        monkeypatch.setattr(agent_loop_module, "MODEL_ID", None)
        monkeypatch.setattr(agent_loop_module, "API_KEY", None)
        with pytest.raises(EnvironmentError, match="MODEL_ID"):
            agent_loop_module._validate_config()

    def test_valid_config(self, monkeypatch):
        monkeypatch.setattr(agent_loop_module, "MODEL_ID", "test-model")
        monkeypatch.setattr(agent_loop_module, "API_KEY", "test-key")
        agent_loop_module._validate_config()  # should not raise
