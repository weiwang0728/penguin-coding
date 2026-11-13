"""Regression coverage for exit_loop history and session continuation."""

from copy import deepcopy
from unittest.mock import Mock

import pytest

import src.agent_loop as loop
from src.compact import estimate_messages_tokens


@pytest.fixture(autouse=True)
def reset_usage(monkeypatch):
    monkeypatch.setattr(loop, "usage_stats", {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "last_input_tokens": 0,
        "pending_delta": 0,
    })


@pytest.mark.parametrize("tool_names, text", [
    (["exit_loop"], "Done."),
    (["exit_loop"], ""),
    (["read_file", "exit_loop", "run_command"], "Done."),
    (["exit_loop", "write_file"], "Done."),
])
def test_exit_closes_all_calls_without_executing_tools(monkeypatch, tool_names, text):
    calls = [
        {"id": f"tool_{index}", "name": name, "input": {}}
        for index, name in enumerate(tool_names)
    ]
    stream = Mock(return_value=iter([
        ("text_delta", text),
        ("tool_calls", calls),
        ("usage", 20),
    ]))
    execute = Mock()
    dispatcher = Mock()
    monkeypatch.setattr(loop, "stream_response", stream)
    monkeypatch.setattr(loop, "execute_tools_parallel", execute)
    history = []

    content, messages = loop.agent_loop(
        client=Mock(), user_message="Finish", messages=history,
        tool_dispatcher=dispatcher,
    )

    assert content == text
    assert messages is history
    assert len(messages) == 3
    assert messages[1]["role"] == "assistant"
    assert messages[2]["role"] == "user"
    results = messages[2]["content"]
    assert len(results) == len(calls)
    for call, result in zip(calls, results):
        assert result["type"] == "tool_result"
        assert result["tool_use_id"] == call["id"]
        if call["name"] == "exit_loop":
            assert not result.get("is_error", False)
            assert "complete" in result["content"].lower()
        else:
            assert result["is_error"] is True
            assert "skipped" in result["content"].lower()
    assert loop.usage_stats["pending_delta"] == estimate_messages_tokens(messages[1:])
    stream.assert_called_once()
    execute.assert_not_called()
    dispatcher.dispatch.assert_not_called()


def test_adapter_continues_same_session_with_paired_history(monkeypatch):
    from src.prdbench import adapter

    requests = []

    def stream_response(client, messages, **kwargs):
        requests.append(deepcopy(messages))
        if len(requests) == 1:
            yield "tool_calls", [{"id": "exit_id", "name": "exit_loop", "input": {}}]
        else:
            yield "text_delta", "Follow-up complete."
        yield "usage", 20

    monkeypatch.setattr(loop, "stream_response", stream_response)
    session = adapter.PRDBenchSession("exit-repro", "test", "code_agent_local")

    first = adapter.run_prdbench_agent("Finish", session, mode="dev")
    second = adapter.run_prdbench_agent("Follow up", session, mode="dev")

    assert first["status"] == second["status"] == "success"
    assert second["content"] == "Follow-up complete."
    assert len(requests) == 2
    assert [message["role"] for message in requests[1]] == [
        "user", "assistant", "user", "user",
    ]
    call = requests[1][1]["content"][0]
    result = requests[1][2]["content"][0]
    assert call["type"] == "tool_use"
    assert result["type"] == "tool_result"
    assert result["tool_use_id"] == call["id"] == "exit_id"
    assert requests[1][3]["content"] == "Follow up"
