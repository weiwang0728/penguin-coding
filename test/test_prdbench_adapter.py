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


class TestMetricIdExtraction(unittest.TestCase):
    def test_three_level_id(self):
        from src.prdbench.run_evaluation import _extract_metric_id
        self.assertEqual(
            _extract_metric_id("0.1.1 Environment and Documentation"),
            "0.1.1",
        )

    def test_letter_suffix_id(self):
        from src.prdbench.run_evaluation import _extract_metric_id
        self.assertEqual(_extract_metric_id("2.5.1a User Input Validation"), "2.5.1a")

    def test_four_level_id_not_truncated(self):
        from src.prdbench.run_evaluation import _extract_metric_id
        # Project 34 uses four-level IDs; truncating to 2.1.1 would collide
        self.assertEqual(
            _extract_metric_id("2.1.1.1 Member Information Entry: Date"),
            "2.1.1.1",
        )
        self.assertEqual(
            _extract_metric_id("2.2.2.1b Relationship Query"),
            "2.2.2.1b",
        )

    def test_two_level_id(self):
        from src.prdbench.run_evaluation import _extract_metric_id
        self.assertEqual(_extract_metric_id("1.1 System Startup"), "1.1")

    def test_no_id(self):
        from src.prdbench.run_evaluation import _extract_metric_id
        self.assertIsNone(_extract_metric_id("No numeric prefix here"))


class TestDevelopmentPromptIsolation(unittest.TestCase):
    def test_dev_prompt_hides_test_plan(self):
        from src.prdbench.prompts import DEVELOPMENT_PROMPT
        result = DEVELOPMENT_PROMPT.format(ID="1", project_path="/tmp/test")
        self.assertNotIn("detailed_test_plan", result)
        self.assertNotIn("evaluation/", result)
        self.assertIn("PRD.md", result)


class TestCalculateScores(unittest.TestCase):
    def _make_project(self, root: str, name: str, plan_metrics, reports: dict):
        project_dir = os.path.join(root, name)
        eval_dir = os.path.join(project_dir, "evaluation")
        report_dir = os.path.join(project_dir, "reports")
        os.makedirs(eval_dir, exist_ok=True)
        os.makedirs(report_dir, exist_ok=True)
        if plan_metrics is not None:
            with open(os.path.join(eval_dir, "detailed_test_plan.json"), "w") as f:
                json.dump([{"metric": m} for m in plan_metrics], f)
        for metric, score in reports.items():
            with open(os.path.join(report_dir, f"{metric}.json"), "w") as f:
                json.dump({"metric": metric, "score": score, "explanation": "x"}, f)

    def test_missing_metrics_count_as_zero(self):
        from src.prdbench.run_evaluation import calculate_scores
        with tempfile.TemporaryDirectory() as root:
            # Plan has 3 metrics; only one report exists (score 2/2)
            self._make_project(root, "1", ["a", "b", "c"], {"a": 2})
            result = calculate_scores(root)
            # 2 / (3 * 2) = 0.3333 — not 1.0 as partial-coverage averaging would give
            self.assertEqual(result["scores"]["1"], 0.3333)
            self.assertEqual(result["coverage"]["1"], {"evaluated": 1, "expected": 3})

    def test_fallback_without_test_plan(self):
        from src.prdbench.run_evaluation import calculate_scores
        with tempfile.TemporaryDirectory() as root:
            self._make_project(root, "2", None, {"a": 2, "b": 1})
            result = calculate_scores(root)
            # (2 + 1) / (2 * 2) = 0.75
            self.assertEqual(result["scores"]["2"], 0.75)

    def test_numeric_project_order(self):
        from src.prdbench.run_evaluation import calculate_scores
        with tempfile.TemporaryDirectory() as root:
            self._make_project(root, "10", ["a"], {"a": 2})
            self._make_project(root, "2", ["a"], {"a": 2})
            result = calculate_scores(root)
            self.assertEqual(list(result["scores"].keys()), ["2", "10"])


class TestSrcIntegritySnapshot(unittest.TestCase):
    def test_restore_modified_and_deleted(self):
        from src.prdbench.run_evaluation import _snapshot_src, _verify_and_restore_src
        with tempfile.TemporaryDirectory() as project_dir:
            src_dir = os.path.join(project_dir, "src")
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, "main.py"), "w") as f:
                f.write("print('original')\n")
            with open(os.path.join(src_dir, "util.py"), "w") as f:
                f.write("X = 1\n")

            backup = _snapshot_src(project_dir)
            self.assertTrue(os.path.isdir(backup))

            # Evaluator tampers: modifies main.py, deletes util.py, adds output
            with open(os.path.join(src_dir, "main.py"), "w") as f:
                f.write("print('tampered')\n")
            os.unlink(os.path.join(src_dir, "util.py"))
            os.makedirs(os.path.join(src_dir, "output"))
            with open(os.path.join(src_dir, "output", "result.txt"), "w") as f:
                f.write("generated\n")

            diff = _verify_and_restore_src(project_dir, backup)
            self.assertEqual(diff["modified"], ["main.py"])
            self.assertEqual(diff["deleted"], ["util.py"])
            self.assertEqual(diff["added"], [os.path.join("output", "result.txt")])

            # Modified/deleted restored; added file kept
            with open(os.path.join(src_dir, "main.py")) as f:
                self.assertEqual(f.read(), "print('original')\n")
            self.assertTrue(os.path.exists(os.path.join(src_dir, "util.py")))
            self.assertTrue(os.path.exists(os.path.join(src_dir, "output", "result.txt")))

    def test_pycache_excluded(self):
        from src.prdbench.run_evaluation import _snapshot_src, _verify_and_restore_src
        with tempfile.TemporaryDirectory() as project_dir:
            src_dir = os.path.join(project_dir, "src")
            cache_dir = os.path.join(src_dir, "__pycache__")
            os.makedirs(cache_dir)
            with open(os.path.join(src_dir, "main.py"), "w") as f:
                f.write("pass\n")
            with open(os.path.join(cache_dir, "main.cpython-311.pyc"), "w") as f:
                f.write("bytecode")

            backup = _snapshot_src(project_dir)
            os.unlink(os.path.join(cache_dir, "main.cpython-311.pyc"))
            diff = _verify_and_restore_src(project_dir, backup)
            # __pycache__ churn is not reported as tampering
            self.assertEqual(diff["deleted"], [])
            self.assertEqual(diff["modified"], [])


class TestReflection(unittest.TestCase):
    def _make_project(self, root: str, name: str, plan_metrics, reports: dict):
        project_dir = os.path.join(root, name)
        eval_dir = os.path.join(project_dir, "evaluation")
        report_dir = os.path.join(project_dir, "reports")
        os.makedirs(eval_dir, exist_ok=True)
        os.makedirs(report_dir, exist_ok=True)
        with open(os.path.join(eval_dir, "detailed_test_plan.json"), "w") as f:
            json.dump([{"metric": m} for m in plan_metrics], f)
        for metric, score in reports.items():
            with open(os.path.join(report_dir, f"{metric}.json"), "w") as f:
                json.dump({"metric": metric, "score": score, "explanation": "x"}, f)

    def test_collect_failed_metrics(self):
        from src.prdbench.run_evaluation import collect_failed_metrics
        with tempfile.TemporaryDirectory() as root:
            # metric a passed (2), b failed (0), c has no report
            self._make_project(root, "1", ["a", "b", "c"], {"a": 2, "b": 0})
            failures = collect_failed_metrics(root, threshold=0)
            self.assertEqual([f["metric"] for f in failures[1]], ["b", "c"])
            self.assertEqual(failures[1][0]["score"], 0)
            self.assertIsNone(failures[1][1]["score"])

    def test_collect_failed_metrics_threshold(self):
        from src.prdbench.run_evaluation import collect_failed_metrics
        with tempfile.TemporaryDirectory() as root:
            self._make_project(root, "1", ["a", "b"], {"a": 2, "b": 1})
            # threshold=1 treats partial passes as failures too
            failures = collect_failed_metrics(root, threshold=1)
            self.assertEqual([f["metric"] for f in failures[1]], ["b"])
            # default threshold=0 treats score 1 as a pass
            self.assertEqual(collect_failed_metrics(root), {})

    def test_merge_skill_candidates_dedupes(self):
        from src.prdbench.run_evaluation import _merge_skill_candidates
        with tempfile.TemporaryDirectory() as root:
            cands = [{"title": "T1", "guidance": "do X"}]
            self.assertEqual(_merge_skill_candidates(root, 1, cands), 1)
            # Same (project, title) is not added twice
            self.assertEqual(_merge_skill_candidates(root, 1, cands), 0)
            # Same title from another project is a separate entry
            self.assertEqual(_merge_skill_candidates(root, 2, cands), 1)

            with open(os.path.join(root, "reflection", "skill_candidates.json")) as f:
                queue = json.load(f)
            self.assertEqual(len(queue), 2)
            self.assertTrue(all(c["status"] == "pending" for c in queue))
            self.assertIn("created_at", queue[0])

    def test_load_approved_skills_only_approved(self):
        from src.prdbench.run_evaluation import _merge_skill_candidates, load_approved_skills
        with tempfile.TemporaryDirectory() as root:
            _merge_skill_candidates(root, 1, [
                {"title": "T1", "guidance": "do X", "trigger": "when Y"},
                {"title": "T2", "guidance": "do Z"},
            ])
            # Nothing approved yet
            self.assertEqual(load_approved_skills(root), "")

            queue_path = os.path.join(root, "reflection", "skill_candidates.json")
            with open(queue_path) as f:
                queue = json.load(f)
            queue[0]["status"] = "approved"
            queue[1]["status"] = "rejected"
            with open(queue_path, "w") as f:
                json.dump(queue, f)

            text = load_approved_skills(root)
            self.assertIn("T1", text)
            self.assertIn("do X", text)
            self.assertIn("when Y", text)
            self.assertNotIn("T2", text)

    def test_eval_prompt_injects_skills(self):
        from src.prdbench.run_evaluation import build_eval_prompt
        prompt = build_eval_prompt(
            metric_data={"metric": "1.1 M", "description": "d"},
            project_dir="/tmp/p",
            metric_report_file="/tmp/p/reports/m.json",
            skills_text="- **T1**\n  Guidance: do X",
        )
        self.assertIn("Lessons from Previous Evaluation Runs", prompt)
        self.assertIn("do X", prompt)

        prompt_without = build_eval_prompt(
            metric_data={"metric": "1.1 M", "description": "d"},
            project_dir="/tmp/p",
            metric_report_file="/tmp/p/reports/m.json",
        )
        self.assertNotIn("Lessons from Previous Evaluation Runs", prompt_without)

    def test_exec_log_excerpt(self):
        from src.prdbench.run_evaluation import _exec_log_excerpt
        with tempfile.TemporaryDirectory() as log_dir:
            path = os.path.join(log_dir, "eval_1_1.1_M_run1.jsonl")
            with open(path, "w") as f:
                f.write(json.dumps({"event": "tool_start", "name": "run_shell_command",
                                    "input": {"command": "python main.py"}}) + "\n")
                f.write(json.dumps({"event": "tool_result", "name": "run_shell_command",
                                    "result": "Traceback: boom"}) + "\n")
            excerpt = _exec_log_excerpt(log_dir, 1, "1.1 M")
            self.assertIn("tool_start run_shell_command", excerpt)
            self.assertIn("Traceback: boom", excerpt)
            # No matching log -> empty
            self.assertEqual(_exec_log_excerpt(log_dir, 2, "1.1 M"), "")


if __name__ == "__main__":
    unittest.main()
