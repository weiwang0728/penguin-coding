"""Session persistence, benchmark lineage, subprocess handoff and score import."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace as NS

import pytest

from src import observability as obs, session
from src.execution_log import ExecutionLog

ROOT = Path(__file__).resolve().parents[1]


def script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_session_id_exists_before_save_and_survives_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(session, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(session, "_current_session_file", None)
    monkeypatch.setattr(session, "_telemetry_session_id", None)
    telemetry_id = session.telemetry_session_id()
    saved_id = session.autosave_session([{"role": "user", "content": "hello"}], "test")
    session.reset_telemetry_session()
    assert session.telemetry_session_id() != telemetry_id
    session.load_session(saved_id)
    assert session.telemetry_session_id() == telemetry_id
    assert json.loads((tmp_path / f"{saved_id}.json").read_text())["telemetry_session_id"] == telemetry_id
    (tmp_path / "legacy.json").write_text(json.dumps({"messages": [], "model": "test"}))
    session.load_session("legacy")
    old_id = session.telemetry_session_id()
    session.reset_telemetry_session()
    session.load_session("legacy")
    assert session.telemetry_session_id() == old_id


def test_execution_log_links_active_span_and_tool_call(tracing, tmp_path):
    log = ExecutionLog(tmp_path / "events.jsonl")
    with obs.run_context("agent.run", session_id="session", run_id="request") as root:
        with obs.bind_context(iteration=2, tool_use_id="call"):
            with obs.observation("tool.read") as tool:
                log.log_tool_result("read_file", "content")
    record = json.loads((tmp_path / "events.jsonl").read_text())
    assert record["trace_id"] == root.trace_id
    assert record["span_id"] == tool.span_id
    assert record["parent_span_id"] == root.span_id
    assert record["run_id"] == "request" and record["tool_use_id"] == "call"
    assert record["schema_version"] == 2


def test_prdbench_direct_entry_returns_trace_and_marks_failures(tracing, monkeypatch):
    from src.prdbench import adapter
    monkeypatch.setattr(adapter, "_run_prdbench_agent", lambda *a: {"status": "error", "error": "failed"})
    result = adapter.run_prdbench_agent("task", adapter.PRDBenchSession("dev_1", "user", "app"),
                                      metadata={"experiment_id": "exp", "project_id": "1"})
    exported = tracing.spans("prdbench.run")[0]
    assert result["trace_id"] == f"{exported.context.trace_id:032x}"
    assert tracing.metadata(exported)["status"] == "error"
    assert exported.attributes["session.id"] == "exp:1"


def test_prdbench_whole_loop_retry_is_a_separate_attempt(tracing, monkeypatch):
    from src.prdbench import adapter
    calls = []

    def agent(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            raise TimeoutError("first attempt")
        return "done", []

    monkeypatch.setattr(adapter, "agent_loop", agent)
    monkeypatch.setattr(adapter, "_build_prdbench_dispatcher", lambda: NS(get_tool_definitions=lambda: []))
    monkeypatch.setattr("time.sleep", lambda _: None)
    result = adapter.run_prdbench_agent("task", adapter.PRDBenchSession("dev_1", "user", "app"))
    attempts = tracing.spans("prdbench.attempt")
    assert result["status"] == "success"
    assert len(attempts) == 2
    assert attempts[0].context.trace_id == attempts[1].context.trace_id
    assert tracing.metadata(attempts[0])["status"] == "error"
    assert tracing.metadata(tracing.spans("prdbench.run")[0])["status"] == "completed"


def test_prdbench_scores_target_artifact_and_skip_stale_reports(tmp_path, monkeypatch):
    from src.prdbench import run_evaluation as runner
    (tmp_path / "reports").mkdir()
    (tmp_path / "query_response.json").write_text(json.dumps({"trace_id": "dev", "artifact_id": "hash"}))
    (tmp_path / "reports" / "metric.json").write_text(json.dumps({"score": 2}))
    calls = []
    monkeypatch.setattr(runner, "record_score", lambda *a, **kw: calls.append((a, kw)))
    result = {"trace_id": "eval", "dev_trace_id": "dev", "artifact_id": "hash"}
    runner._publish_metric_score(tmp_path, "metric", result)
    metric = [c for c in calls if c[0][0] == "prdbench.metric.metric"]
    assert len(metric) == 1 and metric[0][1]["trace_id"] == "dev"
    first_id = metric[0][1]["score_id"]
    calls.clear()
    runner._publish_metric_score(tmp_path, "metric", result)
    assert calls[-1][1]["score_id"] == first_id
    calls.clear()
    runner._publish_metric_score(tmp_path, "metric", {**result, "dev_trace_id": "old-dev"})
    assert not any(c[0][0] == "prdbench.metric.metric" for c in calls)
    calls.clear()
    runner._publish_metric_score(tmp_path, "metric", result, integrity_ok=False)
    assert not any(c[0][0] == "prdbench.metric.metric" for c in calls)


def test_swe_controller_persists_trace_before_worker_and_records_timeout(tracing, tmp_path, monkeypatch):
    runner = script("run_swebench")
    args = argparse.Namespace(model="test", model_name="test", repo_root=None,
                              setup_timeout=1, setup_command=None, timeout=1, max_iterations=2)
    item = dict(instance_id="a__b-1", repo="a/b", base_commit="a" * 40, problem_statement="fix")
    received = {}

    def process(command, cwd, env, log, timeout):
        if command[0] == "git":
            return 0
        before = json.loads((tmp_path / item["instance_id"] / "result.json").read_text())
        assert before["status"] == "running" and before["trace_id"]
        received.update(env)
        raise subprocess.TimeoutExpired(command, timeout)

    monkeypatch.setattr(runner, "run_process", process)
    monkeypatch.setattr(runner, "git", lambda *a, **kw: b"")
    monkeypatch.setattr(runner, "export_patch", lambda *a: "partial patch")
    result = runner.run_instance(item, args, tmp_path)
    assert result["status"] == "timeout" and result["patch_bytes"] > 0
    assert obs.extract_trace_context(received)["trace_id"] == result["trace_id"]
    assert received["PENGUIN_RUN_ID"] == result["run_id"]
    assert tracing.metadata(tracing.spans("swebench.instance")[0])["status"] == "timeout"


def test_swe_worker_joins_parent_and_flushes(tracing, tmp_path, monkeypatch):
    from src.swebench import worker
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"instance_id": "case", "problem_statement": "fix"}))
    monkeypatch.setattr(worker, "Agent", lambda **kw: NS(run=lambda *a, **kw: ("done", [])))
    monkeypatch.setattr("sys.argv", ["worker", "--input", str(source), "--output", str(tmp_path), "--max-iterations", "2"])
    monkeypatch.setenv("PENGUIN_TRACEPARENT", f"00-{'a' * 32}-{'b' * 16}-01")
    monkeypatch.setenv("PENGUIN_SESSION_ID", "session")
    monkeypatch.setenv("PENGUIN_RUN_ID", "request")
    flushed = []
    monkeypatch.setattr(worker, "flush", lambda: flushed.append(True))
    assert worker.main() == 0
    assert flushed == [True]
    result = json.loads((tmp_path / "worker_result.json").read_text())
    assert result["trace_id"] == "a" * 32 and result["run_id"] == "request"
    assert tracing.spans("swebench.worker")[0].parent.span_id == int("b" * 16, 16)


def test_official_score_import_is_idempotent_and_does_not_score_errors(tmp_path, monkeypatch):
    importer = script("import_langfuse_scores")
    for case in ("good", "bad", "error", "missing"):
        (tmp_path / case).mkdir()
        (tmp_path / case / "result.json").write_text(json.dumps({"instance_id": case, "trace_id": case + "-trace"}))
    report = {"resolved_ids": ["good"], "unresolved_ids": ["bad", "error"], "error_ids": ["error"]}
    calls = []
    monkeypatch.setattr(importer, "score", lambda *a, **kw: calls.append((a, kw)) or True)
    assert importer.import_scores(tmp_path, report) == {"submitted": 2, "missing_trace": 0, "unavailable": 0}
    assert {args[1] for args, _ in calls} == {0, 1}
    assert {kwargs["trace_id"] for _, kwargs in calls} == {"good-trace", "bad-trace"}
    first = list(calls)
    calls.clear()
    importer.import_scores(tmp_path, report)
    assert calls == first
    with pytest.raises(ValueError, match="Conflicting"):
        importer.resolved_results({"resolved_ids": ["case"], "unresolved_ids": ["case"]})


def test_server_interrupt_flushes_without_waiting_for_itself(monkeypatch):
    from src.prdbench import server
    calls = []

    def serve():
        raise KeyboardInterrupt()

    httpd = NS(serve_forever=serve, server_close=lambda: calls.append("close"))
    monkeypatch.setattr(server, "HTTPServer", lambda *a: httpd)
    monkeypatch.setattr(server, "flush", lambda: calls.append("flush"))
    server.run_server("127.0.0.1", 0)
    assert calls == ["flush", "close"]


def test_file_errors_use_explicit_status_not_output_prefix(tracing, tmp_path, monkeypatch):
    import importlib
    from src.tools.dispatcher import ToolDispatcher
    from src.tools.read_file import ReadFileTool
    module = importlib.import_module("src.tools.read_file")
    monkeypatch.setattr(module, "resolve_and_validate_path", lambda path: tmp_path / path)
    dispatcher = ToolDispatcher()
    dispatcher.register(ReadFileTool())
    assert "File not found" in dispatcher.dispatch("read_file", {"path": "missing"})
    (tmp_path / "error.log").write_text("Error: this is file content, not a tool failure")
    dispatcher.dispatch("read_file", {"path": "error.log"})
    spans = tracing.spans("tool.read_file")
    assert [tracing.metadata(s)["status"] for s in spans] == ["error", "completed"]

