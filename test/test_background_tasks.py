"""Tests for background_tasks.py — BackgroundManager."""

import time

import pytest

from src.background_tasks import BackgroundManager


class TestBackgroundManager:
    def test_run_returns_task_id(self):
        bg = BackgroundManager()
        result = bg.run("echo hello")
        assert "started" in result
        assert "Background task" in result

    def test_run_dangerous_command_blocked(self):
        bg = BackgroundManager()
        result = bg.run("rm -rf /")
        assert "Error" in result

    def test_check_completed_task(self):
        bg = BackgroundManager()
        bg.run("echo hello")
        time.sleep(1)
        tasks = list(bg.tasks.keys())
        assert len(tasks) == 1
        result = bg.check(tasks[0])
        assert "completed" in result

    def test_check_all_tasks(self):
        bg = BackgroundManager()
        bg.run("echo a")
        bg.run("echo b")
        time.sleep(1)
        result = bg.check()
        assert "echo a" in result or "echo b" in result

    def test_check_unknown_task(self):
        bg = BackgroundManager()
        result = bg.check("nonexistent_id")
        assert "Unknown task" in result

    def test_drain_notifications(self):
        bg = BackgroundManager()
        bg.run("echo hello")
        time.sleep(1)
        notifs = bg.drain_notifications()
        assert len(notifs) == 1
        assert notifs[0]["status"] == "completed"

    def test_drain_clears_queue(self):
        bg = BackgroundManager()
        bg.run("echo hello")
        time.sleep(1)
        bg.drain_notifications()
        notifs2 = bg.drain_notifications()
        assert len(notifs2) == 0

    def test_task_timeout(self):
        bg = BackgroundManager()
        bg.run("sleep 600")
        time.sleep(2)
        tasks = list(bg.tasks.keys())
        # The background task runs with 300s timeout internally,
        # so it will still be running — check the status
        result = bg.check(tasks[0])
        assert "running" in result

    def test_task_error_status(self):
        bg = BackgroundManager()
        bg.run("false_command_that_does_not_exist_xyz")
        time.sleep(1)
        tasks = list(bg.tasks.keys())
        result = bg.check(tasks[0])
        assert "completed" in result or "error" in result

    def test_task_result_includes_output(self):
        bg = BackgroundManager()
        bg.run("echo test_output_123")
        time.sleep(1)
        tasks = list(bg.tasks.keys())
        result = bg.check(tasks[0])
        assert "test_output_123" in result
