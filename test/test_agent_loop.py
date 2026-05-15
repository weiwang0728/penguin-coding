"""Unit tests for agent_loop.py and compact.py"""

import pytest

import src.agent_loop as agent_loop_module
from src.compact import (
    _compact_oversized_blocks,
    _compact_tool_round,
    _is_error_result,
    _strip_old_thinking,
    estimate_messages_tokens,
    estimate_tokens,
    trim_messages,
)
from src.agent_loop import _repair_json


# --- estimate_tokens ---

class TestEstimateTokens:
    def test_empty_string(self):
        assert estimate_tokens("") == 1

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


# --- _compact_tool_round ---

class TestCompactToolRound:
    def test_basic_compaction(self):
        assistant_msg = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Let me read the file"},
                {"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "main.py"}},
            ],
        }
        user_msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": 'print("hello")'},
            ],
        }
        ca, cu = _compact_tool_round(assistant_msg, user_msg)

        assert ca["role"] == "assistant"
        assert cu["role"] == "user"
        assert "read(main.py)" in ca["content"]
        assert "Compacted" in ca["content"]
        assert "Compacted" in cu["content"]

    def test_multiple_tools(self):
        assistant_msg = {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "a.py"}},
                {"type": "tool_use", "id": "t2", "name": "run_command", "input": {"command": "ls"}},
            ],
        }
        user_msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "content_a"},
                {"type": "tool_result", "tool_use_id": "t2", "content": "content_b"},
            ],
        }
        ca, cu = _compact_tool_round(assistant_msg, user_msg)

        assert "read(a.py)" in ca["content"]
        assert "read(ls)" in ca["content"]
        assert "content_a" in cu["content"]
        assert "content_b" in cu["content"]

    def test_empty_tool_round(self):
        assistant_msg = {"role": "assistant", "content": []}
        user_msg = {"role": "user", "content": []}
        ca, cu = _compact_tool_round(assistant_msg, user_msg)

        assert ca["content"] == "[Compacted]"
        assert cu["content"] == "[Compacted tool results]"

    def test_string_content_messages(self):
        assistant_msg = {"role": "assistant", "content": "just text"}
        user_msg = {"role": "user", "content": "user reply"}
        ca, cu = _compact_tool_round(assistant_msg, user_msg)

        assert ca["role"] == "assistant"
        assert cu["role"] == "user"


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

    def test_maintains_alternation(self):
        messages = [{"role": "user", "content": "Start"}]
        for i in range(5):
            messages.append({"role": "assistant", "content": [
                {"type": "tool_use", "id": f"t{i}", "name": "read_file", "input": {"path": f"f{i}.py"}},
            ]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 5000},
            ]})

        result = trim_messages(messages, max_tokens=2000)
        for j in range(len(result)):
            expected = "user" if j % 2 == 0 else "assistant"
            assert result[j]["role"] == expected, f"Message {j}: expected {expected}"

    def test_compacts_old_preserves_recent(self):
        messages = [{"role": "user", "content": "Start"}]
        for i in range(8):
            messages.append({"role": "assistant", "content": [
                {"type": "text", "text": f"Step {i}"},
                {"type": "tool_use", "id": f"t{i}", "name": "run_command", "input": {"command": f"echo {i}"}},
            ]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": "x" * 5000},
            ]})

        result = trim_messages(messages, max_tokens=5000)

        has_compacted = any(
            isinstance(m.get("content"), str) and "[Compacted]" in m.get("content", "")
            for m in result
        )
        assert has_compacted, "Some old messages should be compacted"

    def test_recent_messages_preserved_over_old(self):
        """最老的消息应该被压缩/丢弃，最新的消息应该原样保留"""
        messages = [{"role": "user", "content": "Start"}]
        for i in range(10):
            messages.append({"role": "assistant", "content": [
                {"type": "text", "text": f"Step {i} text"},
                {"type": "tool_use", "id": f"t{i}", "name": "read_file", "input": {"path": f"file{i}.py"}},
            ]})
            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": f"t{i}", "content": f"content_{i} " * 500},
            ]})

        result = trim_messages(messages, max_tokens=3000)

        # 最近的消息应该保留原始结构（list content，不是 compacted string）
        last_assistant = result[-2]
        assert last_assistant["role"] == "assistant"
        assert isinstance(last_assistant["content"], list), \
            "Most recent assistant message should preserve original structure"
        assert any(b.get("type") == "tool_use" for b in last_assistant["content"]), \
            "Most recent tool_use should be intact"

        # 最老的消息应该被压缩（string content with [Compacted]）
        first_assistant_after_user = result[1]
        assert first_assistant_after_user["role"] == "assistant"
        assert isinstance(first_assistant_after_user["content"], str), \
            "Oldest assistant message should be compacted to string"
        assert "[Compacted]" in first_assistant_after_user["content"]

    def test_drops_oldest_when_compact_not_enough(self):
        """压缩后仍放不下的老消息应被丢弃，而不是挤掉新消息"""
        messages = [{"role": "user", "content": "Start"}]
        # 加一轮超大的 tool result
        messages.append({"role": "assistant", "content": [
            {"type": "tool_use", "id": "t0", "name": "read_file", "input": {"path": "huge.py"}},
        ]})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t0", "content": "x" * 80_000},
        ]})
        # 加一轮正常的小消息
        messages.append({"role": "assistant", "content": [
            {"type": "text", "text": "Final answer"},
        ]})

        result = trim_messages(messages, max_tokens=5000)

        # 最新消息（Final answer）必须在
        last = result[-1]
        assert last["role"] == "assistant"
        assert "Final answer" in last.get("content", "") if isinstance(last.get("content"), str) else any(
            b.get("type") == "text" and "Final answer" in b.get("text", "") for b in last.get("content", [])
        )

    def test_single_huge_round(self):
        messages = [
            {"role": "user", "content": "Read this"},
            {"role": "assistant", "content": [
                {"type": "tool_use", "id": "t0", "name": "read_file", "input": {"path": "big.py"}},
            ]},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "t0", "content": "x" * 50000},
            ]},
        ]
        result = trim_messages(messages, max_tokens=1000)
        total = estimate_messages_tokens(result)
        assert total <= 1500


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

    def test_recent_thinking_truncated(self):
        long_thinking = "x" * 2000
        messages = [
            {"role": "user", "content": "q"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": long_thinking},
                {"type": "text", "text": "answer"},
            ]},
        ]
        result = _strip_old_thinking(messages, keep_recent=2)
        thinking_block = [b for b in result[1]["content"] if b.get("type") == "thinking"][0]
        assert len(thinking_block["thinking"]) <= 300

    def test_no_thinking_blocks_unchanged(self):
        messages = [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "just text"},
        ]
        assert _strip_old_thinking(messages) == messages

    def test_empty_messages(self):
        assert _strip_old_thinking([]) == []


# --- _is_error_result ---

class TestIsErrorResult:
    def test_is_error_flag(self):
        block = {"type": "tool_result", "is_error": True, "content": "oops"}
        assert _is_error_result(block) is True

    def test_error_keyword(self):
        block = {"type": "tool_result", "content": "Traceback (most recent call):"}
        assert _is_error_result(block) is True

    def test_success_result(self):
        block = {"type": "tool_result", "content": "File written successfully"}
        assert _is_error_result(block) is False

    def test_non_string_content(self):
        block = {"type": "tool_result", "content": [{"type": "text", "text": "ok"}]}
        assert _is_error_result(block) is False


# --- differentiated _compact_tool_round ---

class TestDifferentiatedCompact:
    def test_write_tool_preserves_path(self):
        assistant_msg = {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "write_file", "input": {"path": "src/main.py"}},
            ],
        }
        user_msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "File written successfully"},
            ],
        }
        ca, cu = _compact_tool_round(assistant_msg, user_msg)
        assert "write_file(src/main.py)" in ca["content"]
        assert "OK" in cu["content"]

    def test_error_result_preserved(self):
        assistant_msg = {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "read_file", "input": {"path": "missing.py"}},
            ],
        }
        user_msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "Error: FileNotFoundError: missing.py not found"},
            ],
        }
        ca, cu = _compact_tool_round(assistant_msg, user_msg)
        assert "ERROR" in cu["content"]
        assert "FileNotFoundError" in cu["content"]

    def test_explore_tool_minimal(self):
        assistant_msg = {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "list_directory", "input": {"directory": "/tmp"}},
            ],
        }
        user_msg = {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "t1", "content": "file1.txt\nfile2.txt\nfile3.txt\n" * 20},
            ],
        }
        ca, cu = _compact_tool_round(assistant_msg, user_msg)
        assert "list_directory" in ca["content"]
        # explore 工具结果应比原始内容短很多
        assert len(cu["content"]) < 200


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
