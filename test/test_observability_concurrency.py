"""Execution-site tracing, context isolation, and asynchronous lifecycle tests."""

from contextlib import contextmanager
from contextvars import ContextVar
from importlib import import_module
from types import SimpleNamespace
import threading

import pytest

from src import agent_teams, background_tasks, parallel_executor
from src.permissions import PermissionLevel
from src.tools.dispatcher import ToolDispatcher
from src.tools.run_command import RunCommandTool


dispatcher_module = import_module("src.tools.dispatcher")
command_module = import_module("src.tools.run_command")


class Recorder:
    def __init__(self):
        self.context = ContextVar("test_trace_context", default={})
        self.current = ContextVar("test_current_span", default=None)
        self.spans = []
        self.ended = threading.Event()
        self.on_end = None

    @contextmanager
    def bind_context(self, **metadata):
        token = self.context.set({**self.context.get(), **metadata})
        try:
            yield
        finally:
            self.context.reset(token)

    @contextmanager
    def observation(self, name, **kwargs):
        recorder = self

        class Span:
            enabled = True

            def __init__(self):
                self.name = name
                self.metadata = {**recorder.context.get(), **kwargs.get("metadata", {})}
                self.kind = kwargs.get("as_type", "span")
                self.status = "completed"
                self.values = {}
                self.closed = False
                self.thread = threading.get_ident()
                self.first_tokens = 0

            def update(self, **values):
                self.values.update(values)

            def set_status(self, status, **metadata):
                self.status = status
                self.metadata.update(metadata)

            def first_token(self):
                self.first_tokens += 1

        span = Span()
        self.spans.append(span)
        token = self.current.set(span)
        try:
            yield span
        except BaseException:
            span.status = "error"
            raise
        finally:
            span.closed = True
            self.current.reset(token)
            if self.on_end:
                self.on_end(span)
            if name == "background.execute":
                self.ended.set()

    def set_status(self, status, **metadata):
        self.current.get().set_status(status, **metadata)

    def record_response(self, span, response):
        span.values["response"] = response


@pytest.fixture
def recorder(monkeypatch):
    recorder = Recorder()
    for module in (parallel_executor, dispatcher_module, command_module,
                   background_tasks, agent_teams):
        for attr in ("bind_context", "observation", "set_status", "record_response"):
            if hasattr(module, attr):
                monkeypatch.setattr(module, attr, getattr(recorder, attr))
    monkeypatch.setattr(agent_teams, "run_context", recorder.observation)
    monkeypatch.setattr(agent_teams, "current_trace_fields", recorder.context.get)
    return recorder


def test_parallel_tools_keep_context_and_end_before_callback_replay(recorder):
    dispatcher = ToolDispatcher()
    barrier = threading.Barrier(2)
    fast_ended = threading.Event()
    callback_ids = []
    main_thread = threading.get_ident()

    def read(which):
        barrier.wait(timeout=3)
        if which == "slow":
            assert fast_ended.wait(3), "fast span must end while slow tool is running"
        return which

    def on_end(span):
        if span.metadata.get("tool_use_id") == "fast-id":
            fast_ended.set()

    recorder.on_end = on_end
    dispatcher.register_dynamic("read_file", read)
    calls = [
        {"id": "slow-id", "name": "read_file", "input": {"which": "slow"}},
        {"id": "fast-id", "name": "read_file", "input": {"which": "fast"}},
    ]
    with recorder.bind_context(trace_id="parent", session_id="conversation"):
        results = parallel_executor.execute_tools_parallel(
            calls, dispatcher.dispatch,
            on_tool_result=lambda *_: callback_ids.append(recorder.context.get()["tool_use_id"]),
        )
        assert "tool_use_id" not in recorder.context.get()

    assert [r["content"] for r in results] == ["slow", "fast"]
    assert callback_ids == ["slow-id", "fast-id"]
    assert {s.metadata["tool_use_id"] for s in recorder.spans} == {"slow-id", "fast-id"}
    assert all(s.metadata["trace_id"] == "parent" for s in recorder.spans)
    assert all(s.thread != main_thread and s.closed for s in recorder.spans)
    assert len({s.thread for s in recorder.spans}) == 2


def test_sequential_context_is_restored_after_tool_exception(recorder):
    dispatcher = ToolDispatcher()

    def failing():
        raise RuntimeError("tool failed")

    dispatcher.register_dynamic("read_file", failing)
    dispatcher.register_dynamic("list_directory", lambda: "ok")
    calls = [{"id": str(i), "name": name, "input": {}}
             for i, name in enumerate(("read_file", "list_directory"))]
    results = parallel_executor.execute_tools_parallel(calls, dispatcher.dispatch, enabled=False)
    assert "tool failed" in results[0]["content"]
    assert results[1]["content"] == "ok"
    assert [s.status for s in recorder.spans] == ["error", "completed"]
    assert [s.metadata["tool_use_id"] for s in recorder.spans] == ["0", "1"]
    assert recorder.context.get() == {}


def test_string_returned_failures_are_not_reported_as_success(recorder, monkeypatch):
    dispatcher = ToolDispatcher()
    dispatcher.register(RunCommandTool())
    assert "invalid arguments" in dispatcher.dispatch("run_command", {})
    assert recorder.spans[-1].status == "invalid_arguments"
    assert "Unknown tool" in dispatcher.dispatch("missing", {})
    assert recorder.spans[-1].status == "unknown_tool"

    dispatcher.set_permission_manager(SimpleNamespace(
        check=lambda *_: SimpleNamespace(level=PermissionLevel.DENY, reason="blocked")
    ))
    assert "Permission denied" in dispatcher.dispatch("run_command", {"command": "echo test"})
    assert recorder.spans[-1].status == "permission_denied"

    dispatcher.set_permission_manager(None)
    monkeypatch.setattr(command_module.subprocess, "run", lambda *a, **kw:
                        SimpleNamespace(stdout="", stderr="failed", returncode=7))
    result = dispatcher.dispatch("run_command", {"command": "example"})
    assert "Exit code: 7" in result
    assert recorder.spans[-1].status == "error"
    assert recorder.spans[-1].metadata["exit_code"] == 7


def test_background_execution_outlives_submit_and_keeps_context(recorder, monkeypatch):
    released = threading.Event()
    started = threading.Event()

    def command(*args, **kwargs):
        started.set()
        assert released.wait(3)
        return SimpleNamespace(stdout="output", stderr="", returncode=4)

    monkeypatch.setattr(background_tasks.subprocess, "run", command)
    manager = background_tasks.BackgroundManager()
    with recorder.bind_context(trace_id="parent", session_id="session"):
        manager.run("example")
    assert started.wait(3)
    submit = next(s for s in recorder.spans if s.name == "background.submit")
    execute = next(s for s in recorder.spans if s.name == "background.execute")
    assert submit.closed and not execute.closed
    released.set()
    assert recorder.ended.wait(3)
    assert execute.metadata["trace_id"] == "parent"
    assert execute.metadata["session_id"] == "session"
    assert execute.metadata["background_task_id"] in manager.tasks
    assert execute.status == "error"
    assert execute.metadata["exit_code"] == 4
    assert execute.values["output"] == "output\nExit code: 4"
    # Legacy public state continues to mean the subprocess finished.
    assert manager.drain_notifications()[0]["status"] == "completed"


@pytest.fixture
def team_manager(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_teams, "ALLOWED_BASE_DIR", tmp_path)
    monkeypatch.setattr(agent_teams, "AGENT_WORKSPACE_DIR", tmp_path / ".agent")
    monkeypatch.setattr(agent_teams, "SHARED_DIR", tmp_path / "shared")
    monkeypatch.setattr(agent_teams, "MODEL_ID", "test-model")
    monkeypatch.setattr(agent_teams, "llm_compact_messages", lambda messages, *a, **kw: messages)
    return agent_teams.TeamManager(tmp_path / ".team")


def test_team_thread_records_stream_usage_and_inherits_trace(recorder, team_manager, monkeypatch):
    response = SimpleNamespace(stop_reason="end_turn", usage=SimpleNamespace(input_tokens=9, output_tokens=3))

    class Stream:
        def __enter__(self):
            assert recorder.current.get().kind == "generation"
            return self

        def __exit__(self, *args):
            return False

        def __iter__(self):
            yield SimpleNamespace(type="content_block_delta",
                                  delta=SimpleNamespace(type="text_delta", text="done"))

        def get_final_message(self):
            assert not recorder.current.get().closed
            return response

    monkeypatch.setattr(agent_teams, "client", SimpleNamespace(
        messages=SimpleNamespace(stream=lambda **kwargs: Stream())))
    with recorder.bind_context(trace_id="parent", session_id="session"):
        team_manager.spawn("reviewer", "qa", "review")
    team_manager.threads["reviewer"].join(3)
    assert not team_manager.threads["reviewer"].is_alive()
    generation = next(s for s in recorder.spans if s.kind == "generation")
    assert generation.metadata["trace_id"] == "parent"
    assert generation.metadata["agent_name"] == "reviewer"
    assert generation.metadata["iteration"] == 1
    assert generation.values["response"] is response
    assert generation.first_tokens == 1
    assert generation.closed
    root = next(s for s in recorder.spans if s.name == "agent.team_run")
    assert root.status == "completed"


def test_team_api_failure_marks_run_and_generation(recorder, team_manager, monkeypatch):
    def fail(**kwargs):
        raise RuntimeError("API unavailable")

    monkeypatch.setattr(agent_teams, "client", SimpleNamespace(messages=SimpleNamespace(stream=fail)))
    team_manager._teammate_loop("reviewer", "qa", "review", threading.Event())
    assert next(s for s in recorder.spans if s.kind == "generation").status == "error"
    assert next(s for s in recorder.spans if s.name == "agent.team_run").status == "api_error"


def test_message_bus_keeps_sender_correlation_without_reparenting(recorder, team_manager):
    with recorder.bind_context(trace_id="sender-trace", span_id="sender-span"):
        team_manager.bus.send("alice", "bob", "hello")
    message = team_manager.bus.read_inbox("bob")[0]
    assert message["sender_trace_id"] == "sender-trace"
    assert message["sender_span_id"] == "sender-span"
    assert message["message_id"]
    assert recorder.context.get() == {}
