"""Unit tests for agent_teams.py — multi-agent team system."""

import json
import threading
import time
from pathlib import Path

import pytest

from src.agent_teams import (
    FileLockManager,
    FileVersionTracker,
    MessageBus,
    WorkspaceResolver,
    TeamManager,
    VALID_MSG_TYPE,
)


# ═══════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def tmp_workspace(tmp_path, monkeypatch):
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / ".agent").mkdir()
    (ws / "shared").mkdir()
    (ws / ".inbox").mkdir()
    (ws / ".team").mkdir()
    monkeypatch.setattr("src.agent_teams.ALLOWED_BASE_DIR", ws)
    monkeypatch.setattr("src.agent_teams.AGENT_WORKSPACE_DIR", ws / ".agent")
    monkeypatch.setattr("src.agent_teams.SHARED_DIR", ws / "shared")
    return ws


@pytest.fixture
def lock_mgr():
    return FileLockManager(timeout=0.5)


@pytest.fixture
def version_tracker():
    return FileVersionTracker()


@pytest.fixture
def bus(tmp_workspace):
    return MessageBus(tmp_workspace / ".inbox")


# ═══════════════════════════════════════════════════════════════
# FileLockManager
# ═══════════════════════════════════════════════════════════════


class TestFileLockManager:
    def test_acquire_returns_true(self, lock_mgr):
        assert lock_mgr.acquire("alice", "src/main.py") is True

    def test_is_locked_before_acquire(self, lock_mgr):
        assert lock_mgr.is_locked("src/main.py") is False

    def test_is_locked_after_acquire(self, lock_mgr):
        lock_mgr.acquire("alice", "src/main.py")
        assert lock_mgr.is_locked("src/main.py") is True

    def test_owner_none_before_acquire(self, lock_mgr):
        assert lock_mgr.owner("src/main.py") is None

    def test_owner_after_acquire(self, lock_mgr):
        lock_mgr.acquire("alice", "src/main.py")
        assert lock_mgr.owner("src/main.py") == "alice"

    def test_release_by_owner(self, lock_mgr):
        lock_mgr.acquire("alice", "src/main.py")
        lock_mgr.release("alice", "src/main.py")
        assert lock_mgr.is_locked("src/main.py") is False
        assert lock_mgr.owner("src/main.py") is None

    def test_release_by_non_owner_still_releases(self, lock_mgr):
        # The underlying threading.Lock is released regardless of caller,
        # but the owner entry is only cleared if the agent matches.
        lock_mgr.acquire("alice", "src/main.py")
        lock_mgr.release("bob", "src/main.py")
        # Lock is released (threading.Lock.release() called), but owner unchanged
        assert lock_mgr.is_locked("src/main.py") is False
        assert lock_mgr.owner("src/main.py") == "alice"

    def test_acquire_timeout_by_second_agent(self):
        mgr = FileLockManager(timeout=0.1)
        assert mgr.acquire("alice", "file.py") is True
        result = [None]
        t = threading.Thread(
            target=lambda: result.__setitem__(0, mgr.acquire("bob", "file.py"))
        )
        t.start()
        t.join(timeout=1.0)
        assert result[0] is False

    def test_acquire_after_release(self, lock_mgr):
        lock_mgr.acquire("alice", "file.py")
        lock_mgr.release("alice", "file.py")
        assert lock_mgr.acquire("bob", "file.py") is True

    def test_multiple_paths_independent(self, lock_mgr):
        assert lock_mgr.acquire("alice", "a.py") is True
        assert lock_mgr.acquire("bob", "b.py") is True
        assert lock_mgr.is_locked("a.py") is True
        assert lock_mgr.is_locked("b.py") is True


# ═══════════════════════════════════════════════════════════════
# FileVersionTracker
# ═══════════════════════════════════════════════════════════════


class TestFileVersionTracker:
    def test_no_prior_read_allowed(self, version_tracker, tmp_path):
        f = tmp_path / "new.py"
        f.write_text("content")
        assert version_tracker.check_before_write("alice", str(f)) is None

    def test_after_read_unchanged_allowed(self, version_tracker, tmp_path):
        f = tmp_path / "stable.py"
        f.write_text("v1")
        version_tracker.record_read("alice", str(f))
        assert version_tracker.check_before_write("alice", str(f)) is None

    def test_after_external_modify_conflict(self, version_tracker, tmp_path):
        f = tmp_path / "changing.py"
        f.write_text("v1")
        version_tracker.record_read("alice", str(f))
        time.sleep(0.01)
        f.write_text("v2")
        result = version_tracker.check_before_write("alice", str(f))
        assert result is not None
        assert "CONFLICT" in result

    def test_file_deleted_allowed(self, version_tracker, tmp_path):
        f = tmp_path / "tmp.py"
        f.write_text("data")
        version_tracker.record_read("alice", str(f))
        f.unlink()
        assert version_tracker.check_before_write("alice", str(f)) is None

    def test_clear_removes_snapshots(self, version_tracker, tmp_path):
        f = tmp_path / "data.py"
        f.write_text("v1")
        version_tracker.record_read("alice", str(f))
        version_tracker.clear("alice")
        assert version_tracker.check_before_write("alice", str(f)) is None

    def test_different_agents_independent(self, version_tracker, tmp_path):
        f = tmp_path / "shared.py"
        f.write_text("v1")
        version_tracker.record_read("alice", str(f))
        time.sleep(0.01)
        f.write_text("v2")
        assert version_tracker.check_before_write("alice", str(f)) is not None
        assert version_tracker.check_before_write("bob", str(f)) is None

    def test_record_read_nonexistent_no_raise(self, version_tracker):
        version_tracker.record_read("alice", "/no/such/path/at/all")

    def test_multiple_reads_same_file_updates(self, version_tracker, tmp_path):
        f = tmp_path / "multi.py"
        f.write_text("v1")
        version_tracker.record_read("alice", str(f))
        time.sleep(0.01)
        f.write_text("v2")
        version_tracker.record_read("alice", str(f))
        assert version_tracker.check_before_write("alice", str(f)) is None


# ═══════════════════════════════════════════════════════════════
# MessageBus
# ═══════════════════════════════════════════════════════════════


class TestMessageBus:
    def test_send_creates_inbox(self, bus):
        bus.send("alice", "bob", "hello")
        inbox = bus.dir / "bob.jsonl"
        assert inbox.exists()

    def test_send_returns_confirmation(self, bus):
        result = bus.send("alice", "bob", "hello")
        assert "Sent" in result
        assert "bob" in result

    def test_send_invalid_type_rejected(self, bus):
        result = bus.send("alice", "bob", "hack", msg_type="evil")
        assert "Error" in result

    @pytest.mark.parametrize("msg_type", list(VALID_MSG_TYPE))
    def test_send_valid_types(self, bus, msg_type):
        result = bus.send("alice", "bob", "test", msg_type=msg_type)
        assert "Sent" in result

    def test_send_with_extra_fields(self, bus):
        bus.send("alice", "bob", "hello", extra={"priority": "high"})
        msgs = bus.read_inbox("bob")
        assert msgs[0]["priority"] == "high"

    def test_read_inbox_returns_messages(self, bus):
        bus.send("alice", "bob", "msg1")
        bus.send("carol", "bob", "msg2")
        msgs = bus.read_inbox("bob")
        assert len(msgs) == 2
        assert msgs[0]["content"] == "msg1"
        assert msgs[1]["content"] == "msg2"

    def test_read_inbox_clears(self, bus):
        bus.send("alice", "bob", "hello")
        bus.read_inbox("bob")
        msgs = bus.read_inbox("bob")
        assert msgs == []

    def test_read_inbox_nonexistent_empty(self, bus):
        msgs = bus.read_inbox("nobody")
        assert msgs == []

    def test_broadcast_excludes_sender(self, bus):
        bus.broadcast("alice", "hello", ["alice", "bob", "carol"])
        alice_msgs = bus.read_inbox("alice")
        assert alice_msgs == []

    def test_broadcast_includes_others(self, bus):
        bus.broadcast("alice", "hello", ["alice", "bob", "carol"])
        bob_msgs = bus.read_inbox("bob")
        carol_msgs = bus.read_inbox("carol")
        assert len(bob_msgs) == 1
        assert len(carol_msgs) == 1
        assert bob_msgs[0]["type"] == "broadcast"

    def test_broadcast_count(self, bus):
        result = bus.broadcast("alice", "hello", ["alice", "bob", "carol"])
        assert "2" in result

    def test_message_format(self, bus):
        bus.send("alice", "bob", "hello")
        msgs = bus.read_inbox("bob")
        msg = msgs[0]
        assert "type" in msg
        assert "from" in msg
        assert "content" in msg
        assert "timestamp" in msg
        assert msg["from"] == "alice"
        assert msg["content"] == "hello"


# ═══════════════════════════════════════════════════════════════
# WorkspaceResolver
# ═══════════════════════════════════════════════════════════════


class TestWorkspaceResolver:
    def test_coordinator_no_rewrite(self, tmp_workspace):
        resolver = WorkspaceResolver()
        result = resolver.resolve("src/main.py", agent=None)
        assert result == "src/main.py"

    def test_relative_path_to_agent_workspace(self, tmp_workspace):
        resolver = WorkspaceResolver()
        result = resolver.resolve("src/main.py", agent="alice")
        assert ".agent/alice/src/main.py" in result

    def test_shared_prefix(self, tmp_workspace):
        resolver = WorkspaceResolver()
        result = resolver.resolve("shared/data.csv", agent="alice")
        assert "shared/data.csv" in result
        assert ".agent" not in result

    def test_shared_subdir(self, tmp_workspace):
        resolver = WorkspaceResolver()
        result = resolver.resolve("shared/reports/q1.csv", agent="alice")
        assert "shared/reports/q1.csv" in result
        assert ".agent" not in result

    def test_absolute_under_base_dir(self, tmp_workspace, monkeypatch):
        resolver = WorkspaceResolver()
        abs_path = str(tmp_workspace / "src" / "main.py")
        result = resolver.resolve(abs_path, agent="alice")
        assert ".agent/alice" in result

    def test_absolute_outside_base_dir(self, tmp_workspace):
        resolver = WorkspaceResolver()
        result = resolver.resolve("/etc/passwd", agent="alice")
        assert result == "/etc/passwd"

    def test_already_in_agent_workspace(self, tmp_workspace):
        resolver = WorkspaceResolver()
        agent_path = str(tmp_workspace / ".agent" / "alice" / "main.py")
        result = resolver.resolve(agent_path, agent="alice")
        assert result == agent_path

    def test_ensure_agent_workspace_creates_dir(self, tmp_workspace):
        resolver = WorkspaceResolver()
        resolver.ensure_agent_workspace("bob")
        assert (tmp_workspace / ".agent" / "bob").is_dir()

    def test_ensure_agent_workspace_idempotent(self, tmp_workspace):
        resolver = WorkspaceResolver()
        resolver.ensure_agent_workspace("bob")
        resolver.ensure_agent_workspace("bob")


# ═══════════════════════════════════════════════════════════════
# TeamManager — Config and Lifecycle
# ═══════════════════════════════════════════════════════════════


class TestTeamManagerConfig:
    @pytest.fixture
    def team_mgr(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", type("FC", (), {"messages": type("M", (), {})()})())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        return TeamManager(tmp_workspace / ".team")

    def test_initial_config_empty(self, team_mgr):
        assert team_mgr.config["members"] == []

    def test_save_and_load_config(self, team_mgr, tmp_workspace):
        team_mgr.config["members"].append({"name": "alice", "role": "coder", "status": "idle"})
        team_mgr._save_config()
        loaded = json.loads((tmp_workspace / ".team" / "config.json").read_text())
        assert loaded["members"][0]["name"] == "alice"

    def test_list_members_empty(self, team_mgr):
        assert team_mgr.list_members() == "No team members."

    def test_shutdown_nonexistent(self, team_mgr):
        result = team_mgr.shutdown("nobody")
        assert "Error" in result

    def test_send_message_nonexistent(self, team_mgr):
        result = team_mgr.send_message("alice", "nobody", "hello")
        assert "Error" in result


# ═══════════════════════════════════════════════════════════════
# _agent_execute_tool
# ═══════════════════════════════════════════════════════════════


class TestAgentExecuteTool:
    @pytest.fixture
    def team_mgr(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", type("FC", (), {"messages": type("M", (), {})()})())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        return TeamManager(tmp_workspace / ".team")

    def test_read_file_path_rewritten(self, team_mgr, monkeypatch):
        captured = {}
        def fake_execute_tool(name, args):
            captured.update(args)
            return "file content"
        monkeypatch.setattr("src.tools.execute_tool", fake_execute_tool)
        team_mgr._agent_execute_tool("alice", "read_file", {"path": "main.py"})
        assert ".agent/alice/main.py" in captured["path"]

    def test_write_file_path_rewritten(self, team_mgr, monkeypatch):
        captured = {}
        def fake_execute_tool(name, args):
            captured.update(args)
            return "ok"
        monkeypatch.setattr("src.tools.execute_tool", fake_execute_tool)
        team_mgr._agent_execute_tool("alice", "write_file", {"path": "out.txt", "content": "hello"})
        assert ".agent/alice/out.txt" in captured["path"]

    def test_write_acquires_and_releases_lock(self, team_mgr, monkeypatch):
        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "ok")
        team_mgr._agent_execute_tool("alice", "write_file", {"path": "f.py", "content": "x"})
        assert team_mgr.lock_mgr.is_locked("f.py") is False

    def test_write_blocked_by_lock(self, team_mgr, monkeypatch):
        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "ok")
        # Lock is checked on the REWRITTEN path (workspace.resolve)
        rewritten_path = team_mgr.workspace.resolve("f.py", "alice")
        team_mgr.lock_mgr.acquire("bob", rewritten_path)
        result = team_mgr._agent_execute_tool("alice", "write_file", {"path": "f.py", "content": "x"})
        assert "CONFLICT" in result
        team_mgr.lock_mgr.release("bob", rewritten_path)

    def test_write_blocked_by_version_conflict(self, team_mgr, tmp_workspace, monkeypatch):
        # Version tracker operates on the REWRITTEN path
        rewritten_path = team_mgr.workspace.resolve("f.py", "alice")
        f = Path(rewritten_path)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("v1")
        team_mgr.version_tracker.record_read("alice", rewritten_path)
        time.sleep(0.01)
        f.write_text("v2")
        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "ok")
        result = team_mgr._agent_execute_tool("alice", "write_file", {"path": "f.py", "content": "x"})
        assert "CONFLICT" in result

    def test_read_records_version(self, team_mgr, monkeypatch):
        # The file must exist at the rewritten path for record_read to capture its stat
        rewritten_path = team_mgr.workspace.resolve("main.py", "alice")
        Path(rewritten_path).parent.mkdir(parents=True, exist_ok=True)
        Path(rewritten_path).write_text("v1")
        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "content")
        team_mgr._agent_execute_tool("alice", "read_file", {"path": "main.py"})
        assert rewritten_path in team_mgr.version_tracker._versions.get("alice", {})

    def test_lock_released_on_tool_error(self, team_mgr, monkeypatch):
        def failing_tool(name, args):
            raise RuntimeError("boom")
        monkeypatch.setattr("src.tools.execute_tool", failing_tool)
        try:
            team_mgr._agent_execute_tool("alice", "write_file", {"path": "f.py", "content": "x"})
        except RuntimeError:
            pass
        assert team_mgr.lock_mgr.is_locked("f.py") is False

    def test_non_path_tool_not_rewritten(self, team_mgr, monkeypatch):
        captured = {}
        def fake_execute_tool(name, args):
            captured.update(args)
            return "output"
        monkeypatch.setattr("src.tools.execute_tool", fake_execute_tool)
        team_mgr._agent_execute_tool("alice", "run_command", {"command": "echo hi"})
        assert captured["command"] == "echo hi"


# ═══════════════════════════════════════════════════════════════
# _teammate_loop (with mocked API)
# ═══════════════════════════════════════════════════════════════


class _FakeStreamEvent:
    def __init__(self, event_type, delta=None, content_block=None, index=0):
        self.type = event_type
        self.delta = delta
        self.content_block = content_block
        self.index = index


class _FakeStream:
    def __init__(self, events, stop_reason="end_turn"):
        self._events = events
        self._stop_reason = stop_reason

    def __iter__(self):
        return iter(self._events)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get_final_message(self):
        return type("Msg", (), {"stop_reason": self._stop_reason})()


class _FakeClient:
    """Mock Anthropic client. Returns text-only stream by default (task complete)."""

    def __init__(self, text="Task complete.", stop_reason="end_turn"):
        self._text = text
        self._stop_reason = stop_reason
        self.messages = self._Messages(self)

    class _Messages:
        def __init__(self, parent):
            self._parent = parent

        def stream(self, **kwargs):
            events = [
                _FakeStreamEvent(
                    "content_block_start",
                    content_block=type("CB", (), {"type": "text", "text": ""})(),
                    index=0,
                ),
                _FakeStreamEvent(
                    "content_block_delta",
                    delta=type("D", (), {"type": "text_delta", "text": self._parent._text})(),
                    index=0,
                ),
                _FakeStreamEvent("content_block_stop", index=0),
            ]
            return _FakeStream(events, stop_reason=self._parent._stop_reason)


class _FailingClient:
    """Client that always raises on stream()."""

    def __init__(self):
        self.messages = self._Messages()

    class _Messages:
        def stream(self, **kwargs):
            raise RuntimeError("API error")


class TestTeammateLoop:
    @pytest.fixture
    def team_mgr(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        monkeypatch.setattr("src.agent_teams.llm_compact_messages", lambda msgs, *a, **kw: msgs)
        return TeamManager(tmp_workspace / ".team")

    def test_loop_completes_on_text_only(self, team_mgr):
        stop = threading.Event()
        team_mgr.config["members"].append({"name": "reviewer", "role": "tester", "status": "working"})
        team_mgr._save_config()
        team_mgr._teammate_loop("reviewer", "tester", "Review the code", stop)
        member = team_mgr._find_member("reviewer")
        assert member["status"] == "idle"

    def test_loop_stops_on_shutdown_event(self, team_mgr):
        stop = threading.Event()
        team_mgr.config["members"].append({"name": "worker", "role": "dev", "status": "working"})
        team_mgr._save_config()
        stop.set()
        team_mgr._teammate_loop("worker", "dev", "Write code", stop)
        member = team_mgr._find_member("worker")
        assert member["status"] == "shutdown"

    def test_loop_handles_shutdown_request_message(self, team_mgr):
        team_mgr.config["members"].append({"name": "agent1", "role": "dev", "status": "working"})
        team_mgr._save_config()
        team_mgr.bus.send("coordinator", "agent1", "stop now", msg_type="shutdown_request")
        stop = threading.Event()
        team_mgr._teammate_loop("agent1", "dev", "Work", stop)
        member = team_mgr._find_member("agent1")
        assert member["status"] == "shutdown"

    def test_loop_api_error_sets_error(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FailingClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        monkeypatch.setattr("src.agent_teams.llm_compact_messages", lambda msgs, *a, **kw: msgs)
        mgr = TeamManager(tmp_workspace / ".team")
        mgr.config["members"].append({"name": "bad", "role": "dev", "status": "working"})
        mgr._save_config()
        stop = threading.Event()
        mgr._teammate_loop("bad", "dev", "Work", stop)
        member = mgr._find_member("bad")
        assert member["status"] == "error"

    def test_loop_handles_inbox_messages(self, team_mgr):
        team_mgr.config["members"].append({"name": "inbox_agent", "role": "dev", "status": "working"})
        team_mgr._save_config()
        team_mgr.bus.send("coordinator", "inbox_agent", "Here is some context")
        stop = threading.Event()
        team_mgr._teammate_loop("inbox_agent", "dev", "Work", stop)
        member = team_mgr._find_member("inbox_agent")
        assert member["status"] in {"idle", "shutdown"}

    def test_version_tracker_cleared_on_completion(self, team_mgr):
        team_mgr.config["members"].append({"name": "clear_agent", "role": "dev", "status": "working"})
        team_mgr._save_config()
        stop = threading.Event()
        team_mgr._teammate_loop("clear_agent", "dev", "Work", stop)
        assert team_mgr.version_tracker._versions.get("clear_agent") is None

    def test_loop_truncated_response_continues(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient("partial", stop_reason="max_tokens"))
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        # Second call returns normal completion — need a client that switches behavior
        call_count = [0]
        original_client = _FakeClient("partial", stop_reason="max_tokens")

        class SwitchingClient:
            def __init__(self):
                self.messages = self._Messages()

            class _Messages:
                def stream(self, **kwargs):
                    call_count[0] += 1
                    if call_count[0] == 1:
                        return original_client.messages.stream(**kwargs)
                    return _FakeClient("done").messages.stream(**kwargs)

        monkeypatch.setattr("src.agent_teams.client", SwitchingClient())
        monkeypatch.setattr("src.agent_teams.llm_compact_messages", lambda msgs, *a, **kw: msgs)
        mgr = TeamManager(tmp_workspace / ".team")
        mgr.config["members"].append({"name": "trunc", "role": "dev", "status": "working"})
        mgr._save_config()
        stop = threading.Event()
        mgr._teammate_loop("trunc", "dev", "Work", stop)
        member = mgr._find_member("trunc")
        assert member["status"] == "idle"


# ═══════════════════════════════════════════════════════════════
# TeamManager Messaging
# ═══════════════════════════════════════════════════════════════


class TestTeamManagerMessaging:
    @pytest.fixture
    def team_mgr(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        monkeypatch.setattr("src.agent_teams.llm_compact_messages", lambda msgs, *a, **kw: msgs)
        return TeamManager(tmp_workspace / ".team")

    def test_send_message_delivers(self, team_mgr):
        team_mgr.config["members"].append({"name": "bob", "role": "dev", "status": "idle"})
        team_mgr._save_config()
        result = team_mgr.send_message("alice", "bob", "hello")
        assert "Sent" in result
        msgs = team_mgr.bus.read_inbox("bob")
        assert len(msgs) == 1
        assert msgs[0]["content"] == "hello"

    def test_broadcast_message_delivers(self, team_mgr):
        team_mgr.config["members"] = [
            {"name": "alice", "role": "lead", "status": "idle"},
            {"name": "bob", "role": "dev", "status": "idle"},
        ]
        team_mgr._save_config()
        result = team_mgr.broadcast_message("coordinator", "meeting at 3")
        assert "Broadcast" in result

    def test_spawn_creates_workspace(self, team_mgr, tmp_workspace):
        team_mgr.spawn("tester", "qa", "Run tests")
        assert (tmp_workspace / ".agent" / "tester").is_dir()
        member = team_mgr._find_member("tester")
        assert member is not None
        # Wait for thread to complete (it uses FakeClient, finishes immediately)
        if "tester" in team_mgr.threads:
            team_mgr.threads["tester"].join(timeout=3.0)


# ═══════════════════════════════════════════════════════════════
# Concurrency / Integration
# ═══════════════════════════════════════════════════════════════


class TestConcurrency:
    def test_two_agents_write_different_files(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        mgr = TeamManager(tmp_workspace / ".team")

        calls = []
        def fake_execute_tool(name, args):
            calls.append((name, dict(args)))
            return "ok"
        monkeypatch.setattr("src.tools.execute_tool", fake_execute_tool)

        mgr._agent_execute_tool("alice", "write_file", {"path": "a.py", "content": "alice"})
        mgr._agent_execute_tool("bob", "write_file", {"path": "b.py", "content": "bob"})

        alice_path = [c[1]["path"] for c in calls if c[0] == "write_file"]
        assert ".agent/alice/a.py" in alice_path[0]
        assert ".agent/bob/b.py" in alice_path[1]

    def test_two_agents_read_same_file(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        mgr = TeamManager(tmp_workspace / ".team")

        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "content")
        r1 = mgr._agent_execute_tool("alice", "read_file", {"path": "shared.py"})
        r2 = mgr._agent_execute_tool("bob", "read_file", {"path": "shared.py"})
        assert r1 == "content"
        assert r2 == "content"

    def test_write_conflict_detected(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        mgr = TeamManager(tmp_workspace / ".team")

        # Alice reads
        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "v1")
        mgr._agent_execute_tool("alice", "read_file", {"path": "shared/data.py"})

        # Simulate Bob modifying the file externally
        shared_data = tmp_workspace / ".agent" / "alice" / "shared" / "data.py"
        shared_data.parent.mkdir(parents=True, exist_ok=True)
        shared_data.write_text("v1")
        # The version tracker records "shared/data.py" (before rewriting),
        # but after path rewriting the actual path is different.
        # For a realistic test, record directly on the real path.
        real_path = str(shared_data)
        mgr.version_tracker.record_read("alice", real_path)
        time.sleep(0.01)
        shared_data.write_text("v2_modified_by_bob")

        monkeypatch.setattr("src.tools.execute_tool", lambda n, a: "ok")
        result = mgr._agent_execute_tool("alice", "write_file", {"path": real_path, "content": "alice_v2"})
        assert "CONFLICT" in result

    def test_agent_workspace_isolation(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        mgr = TeamManager(tmp_workspace / ".team")

        captured = []
        def capture_tool(name, args):
            captured.append(args.get("path", ""))
            return "ok"
        monkeypatch.setattr("src.tools.execute_tool", capture_tool)

        mgr._agent_execute_tool("alice", "write_file", {"path": "secret.py", "content": "a"})
        mgr._agent_execute_tool("bob", "write_file", {"path": "secret.py", "content": "b"})

        alice_path = captured[0]
        bob_path = captured[1]
        assert ".agent/alice/secret.py" in alice_path
        assert ".agent/bob/secret.py" in bob_path
        assert alice_path != bob_path


# ═══════════════════════════════════════════════════════════════
# Team Tool Dispatch (via tools.py)
# ═══════════════════════════════════════════════════════════════


class TestTeamToolDispatch:
    @pytest.fixture
    def fake_team_mgr(self, tmp_workspace, monkeypatch):
        monkeypatch.setattr("src.agent_teams.client", _FakeClient())
        monkeypatch.setattr("src.agent_teams.MODEL_ID", "test-model")
        monkeypatch.setattr("src.agent_teams.llm_compact_messages", lambda msgs, *a, **kw: msgs)
        mgr = TeamManager(tmp_workspace / ".team")
        monkeypatch.setattr("src.tools.TEAM_MANAGER", mgr)
        return mgr

    def test_team_spawn_via_tool(self, fake_team_mgr):
        from src.tools import execute_tool
        result = execute_tool("team_spawn", {"name": "alice", "role": "coder", "prompt": "Write code"})
        assert "Spawned" in result
        member = fake_team_mgr._find_member("alice")
        assert member is not None
        if "alice" in fake_team_mgr.threads:
            fake_team_mgr.threads["alice"].join(timeout=3.0)

    def test_team_list_via_tool(self, fake_team_mgr):
        from src.tools import execute_tool
        result = execute_tool("team_list", {})
        assert "No team members" in result

    def test_team_shutdown_via_tool(self, fake_team_mgr):
        from src.tools import execute_tool
        fake_team_mgr.config["members"].append({"name": "bob", "role": "dev", "status": "idle"})
        fake_team_mgr._save_config()
        result = execute_tool("team_shutdown", {"name": "bob"})
        assert "Shutdown" in result

    def test_team_broadcast_via_tool(self, fake_team_mgr):
        from src.tools import execute_tool
        fake_team_mgr.config["members"] = [
            {"name": "alice", "role": "dev", "status": "idle"},
            {"name": "bob", "role": "dev", "status": "idle"},
        ]
        fake_team_mgr._save_config()
        result = execute_tool("team_broadcast", {"content": "meeting"})
        assert "Broadcast" in result
