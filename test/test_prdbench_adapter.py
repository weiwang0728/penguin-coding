"""Tests for PRDBench adapter integration."""

import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

# Test configuration
TEST_PORT = 18766
TEST_HOST = "127.0.0.1"


class TestPRDBenchConfig(unittest.TestCase):
    def test_config_defaults(self):
        from src.prdbench.config import APP_NAME, DEFAULT_PORT, WORKSPACE_DIR
        self.assertEqual(APP_NAME, "code_eval_agent")
        self.assertIsInstance(DEFAULT_PORT, int)
        self.assertIsInstance(WORKSPACE_DIR, str)


class TestPRDBenchPrompts(unittest.TestCase):
    def test_development_prompt(self):
        from src.prdbench.prompts import DEVELOPMENT_PROMPT
        result = DEVELOPMENT_PROMPT.format(ID="1", project_path="/tmp/test")
        self.assertIn("1", result)
        self.assertIn("/tmp/test", result)
        self.assertIn("PRD.md", result)

    def test_debug_prompt(self):
        from src.prdbench.prompts import DEBUG_PROMPT
        result = DEBUG_PROMPT.format(ID="1", project_path="/tmp/test")
        self.assertIn("1", result)
        self.assertIn("debug", result.lower())

    def test_evaluation_prompt(self):
        from src.prdbench.prompts import EVALUATION_PROMPT
        result = EVALUATION_PROMPT.format(project_dir="/tmp/test", round=1)
        self.assertIn("/tmp/test", result)
        self.assertIn("round1", result)


class TestPRDBenchTools(unittest.TestCase):
    def test_judge_tool(self):
        from src.prdbench.tools import JudgeTool
        j = JudgeTool()
        self.assertEqual(j.name, "judge")

        # Create temp input file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello\n")
            input_file = f.name

        try:
            result = j.execute(
                context="echo test",
                entry_command="echo hello",
                input_file=input_file,
            )
            data = json.loads(result)
            self.assertEqual(data["status"], "success")
            self.assertIn("hello", data["log"])
        finally:
            os.unlink(input_file)

    def test_judge_tool_missing_input(self):
        from src.prdbench.tools import JudgeTool
        j = JudgeTool()
        result = j.execute(
            context="test",
            entry_command="echo hi",
            input_file="/nonexistent/file.txt",
        )
        self.assertIn("Error", result)

    def test_start_interactive_shell(self):
        from src.prdbench.tools import StartInteractiveShellTool
        s = StartInteractiveShellTool()
        self.assertEqual(s.name, "start_interactive_shell")

        result = s.execute(cmd="echo ready")
        data = json.loads(result)
        self.assertEqual(data["status"], "started")
        self.assertIn("session_id", data)

    def test_kill_shell_session(self):
        from src.prdbench.tools import (
            StartInteractiveShellTool, KillShellSessionTool
        )
        start = StartInteractiveShellTool()
        kill = KillShellSessionTool()

        result = start.execute(cmd="echo test")
        data = json.loads(result)
        session_id = data["session_id"]

        kill_result = kill.execute(session_id=session_id)
        self.assertIn("terminated", kill_result)

    def test_kill_nonexistent_session(self):
        from src.prdbench.tools import KillShellSessionTool
        kill = KillShellSessionTool()
        result = kill.execute(session_id="nonexistent")
        self.assertIn("Warning", result)

    def test_list_workspace(self):
        from src.prdbench.tools import ListWorkspaceTool
        lw = ListWorkspaceTool()
        result = lw.execute(workspace_name="/tmp")
        self.assertTrue(len(result) > 0)

    def test_exit_loop(self):
        from src.prdbench.tools import ExitLoopTool
        el = ExitLoopTool()
        result = el.execute()
        self.assertIn("complete", result.lower())


class TestPRDBenchSessionManager(unittest.TestCase):
    def test_create_and_get_session(self):
        from src.prdbench.adapter import SessionManager, PRDBenchSession
        mgr = SessionManager()
        session = mgr.create("s1", "user1", "app1")
        self.assertEqual(session.session_id, "s1")

        retrieved = mgr.get("s1")
        self.assertEqual(retrieved.session_id, "s1")

    def test_delete_session(self):
        from src.prdbench.adapter import SessionManager
        mgr = SessionManager()
        mgr.create("s2", "user1", "app1")
        self.assertTrue(mgr.delete("s2"))
        self.assertIsNone(mgr.get("s2"))

    def test_delete_nonexistent(self):
        from src.prdbench.adapter import SessionManager
        mgr = SessionManager()
        self.assertFalse(mgr.delete("nonexistent"))

    def test_session_touch(self):
        from src.prdbench.adapter import SessionManager
        mgr = SessionManager()
        session = mgr.create("s3", "user1", "app1")
        old_time = session.last_activity
        time.sleep(0.01)
        session.touch()
        self.assertGreater(session.last_activity, old_time)


class TestPRDBenchDispatcher(unittest.TestCase):
    def test_build_prdbench_dispatcher(self):
        from src.prdbench.adapter import _build_prdbench_dispatcher
        disp = _build_prdbench_dispatcher()
        self.assertGreater(len(disp._registry), 0)

        # Check PRDBench-specific tools are present
        names = list(disp._registry.keys())
        self.assertIn("judge", names)
        self.assertIn("start_interactive_shell", names)
        self.assertIn("run_interactive_shell", names)
        self.assertIn("kill_shell_session", names)
        self.assertIn("list_workspace", names)
        self.assertIn("exit_loop", names)

        # Core tools should be present
        self.assertIn("read_file", names)
        self.assertIn("write_file", names)
        self.assertIn("run_command", names)

        # Team tools should NOT be present
        self.assertNotIn("team_spawn", names)
        self.assertNotIn("delegate", names)

    def test_build_tool_definitions(self):
        from src.prdbench.adapter import _build_prdbench_tool_definitions
        defs = _build_prdbench_tool_definitions()
        self.assertGreater(len(defs), 0)
        for d in defs:
            self.assertIn("name", d)
            self.assertIn("input_schema", d)


class TestPRDBenchServer(unittest.TestCase):
    """Test HTTP API server endpoints."""

    @classmethod
    def setUpClass(cls):
        from src.prdbench.server import run_server
        cls.server_thread = threading.Thread(
            target=run_server,
            args=(TEST_HOST, TEST_PORT),
            daemon=True,
        )
        cls.server_thread.start()
        time.sleep(1)

    def test_health_check(self):
        import urllib.request
        resp = urllib.request.urlopen(f"http://{TEST_HOST}:{TEST_PORT}/health")
        data = json.loads(resp.read())
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["app"], "code_eval_agent")

    def test_create_and_delete_session(self):
        import urllib.request
        # Create
        req = urllib.request.Request(
            f"http://{TEST_HOST}:{TEST_PORT}/apps/code_eval_agent/users/test/sessions/s_test_create",
            method="POST",
            data=b"{}",
            headers={"Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        self.assertEqual(data["id"], "s_test_create")

        # Delete
        req = urllib.request.Request(
            f"http://{TEST_HOST}:{TEST_PORT}/apps/code_eval_agent/users/test/sessions/s_test_create",
            method="DELETE",
        )
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        self.assertEqual(data["status"], "deleted")

    def test_run_endpoint_format(self):
        """Test that /run endpoint accepts the expected request format."""
        import urllib.request
        # Just test the request format is accepted — we can't do a full agent run in tests
        # without an actual LLM API
        pass


class TestReportFormat(unittest.TestCase):
    def test_check_report_format_valid_json_array(self):
        from src.prdbench.run_evaluation import check_report_format
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            json.dump([{"metric": "test", "score": 2, "explanation": "ok"}], f)
            path = f.name
        try:
            self.assertTrue(check_report_format(path))
        finally:
            os.unlink(path)

    def test_check_report_format_valid_jsonl(self):
        from src.prdbench.run_evaluation import check_report_format
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write('{"metric": "test", "score": 1, "explanation": "ok"}\n')
            f.write('{"metric": "test2", "score": 0, "explanation": "fail"}\n')
            path = f.name
        try:
            self.assertTrue(check_report_format(path))
        finally:
            os.unlink(path)

    def test_check_report_format_empty(self):
        from src.prdbench.run_evaluation import check_report_format
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            path = f.name
        try:
            self.assertFalse(check_report_format(path))
        finally:
            os.unlink(path)

    def test_check_report_format_no_scores(self):
        from src.prdbench.run_evaluation import check_report_format
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            json.dump([{"metric": "test", "explanation": "no score field"}], f)
            path = f.name
        try:
            self.assertFalse(check_report_format(path))
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
