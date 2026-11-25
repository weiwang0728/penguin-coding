"""Offline unit tests for the subagent/delegate mechanism (no API calls).

Covers:
  - SUBAGENT_TOOLS excludes delegate (no nesting)
  - register_delegate_tool schema registration
  - run_subagent: returns final text when no tool calls
  - run_subagent: executes tool calls and feeds tool_results back to the model
  - run_subagent: iteration-limit fallback message
"""

import pytest

import src.agent_loop as agent_loop_module
from src.agent_loop import SUBAGENT_TOOLS, run_subagent
from src.tools import TOOL_DEFINITIONS, register_delegate_tool


# --- structural guarantees ---------------------------------------------------

class TestDelegateToolShape:
    def test_subagent_tools_exclude_delegate(self):
        """Subagents must not be able to nest delegation."""
        assert "delegate" not in [t["name"] for t in SUBAGENT_TOOLS]

    def test_delegate_schema_registered(self):
        # cli.py registers at startup; tests must do it explicitly (idempotent guard)
        if "delegate" not in [t["name"] for t in TOOL_DEFINITIONS]:
            register_delegate_tool(client=None)
        assert "delegate" in [t["name"] for t in TOOL_DEFINITIONS]

    def test_delegate_schema_requires_prompt(self):
        if "delegate" not in [t["name"] for t in TOOL_DEFINITIONS]:
            register_delegate_tool(client=None)
        schema = next(t for t in TOOL_DEFINITIONS if t["name"] == "delegate")
        assert "prompt" in schema["input_schema"]["required"]


# --- run_subagent loop (mocked stream) ---------------------------------------

class FakeStream:
    """Scripted stream_response replacement; records the messages it sees."""

    def __init__(self, script):
        # script: list of event lists, one per LLM call
        self.script = script
        self.calls = []  # captured (messages, system_prompt, tools)

    def __call__(self, client, messages, system_prompt=None, tools=None,
                 max_tokens=1024, model_id=None):
        self.calls.append({"messages": [dict(m) for m in messages],
                           "system_prompt": system_prompt, "tools": tools})
        for ev in self.script[len(self.calls) - 1]:
            yield ev


@pytest.fixture
def mock_llm(monkeypatch):
    def install(script):
        fake = FakeStream(script)
        monkeypatch.setattr(agent_loop_module, "stream_response", fake)
        monkeypatch.setattr(
            agent_loop_module, "execute_tools_parallel",
            lambda tool_calls_list, dispatch_fn: [
                {"type": "tool_result", "tool_use_id": tc["id"],
                 "content": f"fake result for {tc['name']}"}
                for tc in tool_calls_list
            ],
        )
        return fake
    return install


class TestRunSubagentLoop:
    def test_returns_final_text_without_tool_calls(self, mock_llm):
        """A response with no tool calls ends the subagent immediately."""
        fake = mock_llm([[("text_delta", "Final answer: done")]])
        result = run_subagent(client=None, prompt="list files", max_iterations=5)
        assert result == "Final answer: done"
        assert len(fake.calls) == 1  # loop did not continue after a plain answer

    def test_executes_tool_and_feeds_result_back(self, mock_llm):
        fake = mock_llm([
            [("text_delta", "Let me check."),
             ("tool_calls", [{"id": "t1", "name": "list_directory", "input": {"path": "."}}])],
            [("text_delta", "Found: a.txt, b.txt")],
        ])
        result = run_subagent(client=None, prompt="list files", max_iterations=5)

        assert result == "Found: a.txt, b.txt"
        assert len(fake.calls) == 2
        # second call's history: user -> assistant(text+tool_use) -> user(tool_result)
        second = fake.calls[1]["messages"]
        assert second[0]["role"] == "user"
        assert second[1]["role"] == "assistant"
        assert {"type": "tool_use", "id": "t1", "name": "list_directory",
                "input": {"path": "."}} in second[1]["content"]
        assert second[2]["role"] == "user"
        tr = second[2]["content"][0]
        assert tr["type"] == "tool_result" and tr["tool_use_id"] == "t1"

    def test_subagent_uses_subagent_system_prompt_and_tools(self, mock_llm):
        fake = mock_llm([[("text_delta", "done")]])
        run_subagent(client=None, prompt="x", max_iterations=3)
        assert fake.calls[0]["system_prompt"] == agent_loop_module.SUBAGENT_SYSTEM_PROMPT
        assert fake.calls[0]["tools"] is SUBAGENT_TOOLS

    def test_iteration_limit_returns_partial(self, mock_llm):
        # every call wants another tool -> never terminates on its own
        mock_llm([
            [("tool_calls", [{"id": f"t{i}", "name": "run_command", "input": {}}])]
            for i in range(2)
        ])
        result = run_subagent(client=None, prompt="loop forever", max_iterations=2)
        assert "hit iteration limit (2)" in result

    def test_truncated_response_does_not_execute_tools(self, mock_llm):
        """Regression: truncated mid-tool-call — the call must NOT be executed."""
        fake = mock_llm([
            [("text_delta", "I'll run"),
             ("truncated", True)],  # truncation hit before the tool call closed
            [("text_delta", "Recovered.")],
        ])
        result = run_subagent(client=None, prompt="x", max_iterations=3)
        assert result == "Recovered."
        # continuation request must contain no tool_use in the backfilled
        # assistant message (otherwise pairing is broken / model thinks it ran)
        second = fake.calls[1]["messages"]
        assistant_blocks = [b for m in second if m["role"] == "assistant" for b in m["content"]]
        assert all(b["type"] != "tool_use" for b in assistant_blocks)
