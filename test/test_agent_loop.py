"""Unit tests for agent_loop.py and compact.py"""

from unittest.mock import Mock

import pytest

import src.agent_loop as agent_loop_module
from src.compact import (
    _compact_oversized_blocks,
    _strip_old_thinking,
    estimate_messages_tokens,
    estimate_tokens,
    trim_messages,
)
from src.agent_loop import _budget_hint, _collect_tool_calls, _repair_json


class TestBudgetHint:
    def test_plenty_remaining_keeps_working(self):
        assert _budget_hint(50, 100) == "Keep working — do not stop until the task is complete."

    def test_finalize_zone_at_85_percent(self):
        hint = _budget_hint(15, 100)
        assert "Budget nearly exhausted" in hint
        assert "call exit_loop" in hint
        # finalize boundary: 15% of 100 = 15
        assert _budget_hint(16, 100) == "Keep working — do not stop until the task is complete."

    def test_exhausted_overrides_finalize(self):
        hint = _budget_hint(5, 100)
        assert "Budget exhausted" in hint
        assert "exit_loop now" in hint

    def test_small_max_iterations_still_finalizes(self):
        # max_iterations=20: finalize at remaining <= 3, exhausted at <= 5 takes precedence
        assert "Budget exhausted" in _budget_hint(3, 20)
        assert "Budget nearly exhausted" in _budget_hint(6, 200)


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

    def test_completely_broken_returns_none(self):
        assert _repair_json("}{][") is None


# --- run_agent truncation recovery ---

@pytest.fixture(autouse=True)
def reset_usage(monkeypatch):
    monkeypatch.setattr(agent_loop_module, "usage_stats", {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "last_input_tokens": 0,
        "pending_delta": 0,
    })


class TestTruncationRecovery:
    def test_preserves_partial_output_and_closes_tool_calls(self, monkeypatch):
        """First truncation: partial text + tool_use kept, tool_result synthesized,
        budget escalated, and the truncated tool call is never executed."""
        calls_seen = []

        def fake_stream(client, messages, system_prompt=None, tools=None,
                        max_tokens=16384, model_id=None):
            calls_seen.append(max_tokens)
            if len(calls_seen) == 1:
                yield ("text_delta", "partial ")
                yield ("truncated", True)
                yield ("tool_calls", [
                    {"id": "t0", "name": "run_command", "input": {"command": "ls"}},
                ])
            else:
                yield ("text_delta", "done")
                yield ("usage", 10)

        dispatcher = Mock()
        monkeypatch.setattr(agent_loop_module, "stream_response", fake_stream)

        content, messages = agent_loop_module.agent_loop(
            client=Mock(), user_message="Go", messages=[], tool_dispatcher=dispatcher,
        )

        # attempt 1 at the default budget, attempt 2 escalated
        assert calls_seen == [agent_loop_module.MAX_OUTPUT_TOKENS,
                              agent_loop_module.ESCALATED_MAX_TOKENS]
        # messages: user, assistant(truncated), user(tool_result+continuation), assistant(done)
        assert len(messages) == 4
        assert messages[1]["role"] == "assistant"
        tool_use = [b for b in messages[1]["content"] if b["type"] == "tool_use"]
        assert tool_use and tool_use[0]["id"] == "t0"
        assert messages[2]["role"] == "user"
        results = [b for b in messages[2]["content"] if b.get("type") == "tool_result"]
        assert results and results[0]["tool_use_id"] == "t0"
        assert results[0]["is_error"] is True
        assert "not executed" in results[0]["content"].lower()
        # continuation hint text is present alongside the synthetic result
        assert any(b.get("type") == "text" and "Resume" in b["text"]
                   for b in messages[2]["content"])
        dispatcher.dispatch.assert_not_called()
        assert content == "done"

    def test_truncation_without_tool_calls_appends_plain_continuation(self, monkeypatch):
        def fake_stream(client, messages, **kwargs):
            if len(messages) == 1:
                yield ("text_delta", "half ")
                yield ("truncated", True)
            else:
                yield ("text_delta", "done")
                yield ("usage", 5)

        monkeypatch.setattr(agent_loop_module, "stream_response", fake_stream)
        content, messages = agent_loop_module.agent_loop(
            client=Mock(), user_message="Go", messages=[], tool_dispatcher=Mock(),
        )
        # continuation message is plain text (no tool_result blocks needed)
        assert isinstance(messages[2]["content"], str)
        assert "Resume" in messages[2]["content"]
        assert content == "done"

    def test_gives_up_after_max_continuations(self, monkeypatch):
        attempts = []

        def fake_stream(client, messages, **kwargs):
            attempts.append(len(messages))
            yield ("text_delta", "x")
            yield ("truncated", True)

        monkeypatch.setattr(agent_loop_module, "stream_response", fake_stream)
        content, messages = agent_loop_module.agent_loop(
            client=Mock(), user_message="Go", messages=[], tool_dispatcher=Mock(),
        )
        # 1 initial + 1 escalated + MAX_RECOVERY_RETRIES continuations
        assert len(attempts) == 2 + agent_loop_module.MAX_RECOVERY_RETRIES
        assert content == "x"

    def test_provider_rejecting_escalated_budget_reverts_to_default(self, monkeypatch):
        import anthropic

        calls_seen = []

        def fake_stream(client, messages, system_prompt=None, tools=None,
                        max_tokens=16384, model_id=None):
            calls_seen.append(max_tokens)
            if len(calls_seen) == 1:
                yield ("text_delta", "p")
                yield ("truncated", True)
            elif len(calls_seen) == 2:
                raise anthropic.APIStatusError(
                    "max_tokens: 65536 > 32768, reduce the value",
                    response=Mock(status_code=400, headers={}, request=Mock()),
                    body=None,
                )
            else:
                yield ("text_delta", "ok")
                yield ("usage", 5)

        monkeypatch.setattr(agent_loop_module, "stream_response", fake_stream)
        content, messages = agent_loop_module.agent_loop(
            client=Mock(), user_message="Go", messages=[], tool_dispatcher=Mock(),
        )
        assert calls_seen == [agent_loop_module.MAX_OUTPUT_TOKENS,
                              agent_loop_module.ESCALATED_MAX_TOKENS,
                              agent_loop_module.MAX_OUTPUT_TOKENS]
        assert content == "ok"


# --- _collect_tool_calls ---

class TestCollectToolCalls:
    @staticmethod
    def _block(idx, name="run_command", complete=True, parse_failed=False, has_input=True):
        block = {
            "id": f"tool_{idx}",
            "name": name,
            "_partial_json": "",
            "_complete": complete,
        }
        if has_input:
            block["input"] = {}
        if parse_failed:
            block["_parse_failed"] = True
        return block

    def test_complete_blocks_kept_in_index_order(self):
        blocks = {1: self._block(1, "read_file"), 0: self._block(0, "run_command")}
        calls = _collect_tool_calls(blocks)
        assert [c["id"] for c in calls] == ["tool_0", "tool_1"]

    def test_incomplete_block_dropped(self):
        # content_block_stop never fired (stream truncated mid-JSON):
        # block has no "input" key at all — must not raise KeyError.
        blocks = {0: self._block(0, complete=True), 1: self._block(1, complete=False, has_input=False)}
        calls = _collect_tool_calls(blocks)
        assert [c["id"] for c in calls] == ["tool_0"]

    def test_parse_failed_block_dropped(self):
        blocks = {0: self._block(0, parse_failed=True)}
        assert _collect_tool_calls(blocks) == []

    def test_missing_input_defaults_to_empty_dict(self):
        blocks = {0: self._block(0, has_input=False, complete=True)}
        calls = _collect_tool_calls(blocks)
        assert calls == [{"id": "tool_0", "name": "run_command", "input": {}}]

    def test_empty_blocks(self):
        assert _collect_tool_calls({}) == []
