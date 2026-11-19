import threading
import uuid
import subprocess
from contextvars import copy_context
from ._constants import ALLOWED_BASE_DIR, check_dangerous_command, _truncate_output
from .observability import bind_context, observation, set_status

class BackgroundManager:
    def __init__(self):
        self.tasks = {}  # task_id -> {status, result, command}
        self._notification_queue = []  # completed task results
        self._lock = threading.Lock()

    def run(self, command: str) -> str:
        """Start a background thread, return task_id immediately."""
        with observation("background.submit", input={"command": command}) as span:
            result = self._start(command)
            span.update(output=result)
            return result

    def _start(self, command: str) -> str:
        danger = check_dangerous_command(command)
        if danger:
            set_status("permission_denied")
            return f"Error: {danger}"

        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = {"status": "running", "result": None, "command": command}
        context = copy_context()
        thread = threading.Thread(target=context.run,
                                  args=(self._execute, task_id, command), daemon=True)
        thread.start()
        return f"Background task {task_id} started: {command}\nYou can continue working. Results will be delivered when the task completes."

    def _execute(self, task_id: str, command: str):
        """Thread target: run subprocess, capture output, push to queue."""
        with bind_context(background_task_id=task_id):
            with observation("background.execute", input={"command": command}) as span:
                self._execute_command(task_id, command)
                span.update(output=self.tasks[task_id]["result"])

    def _execute_command(self, task_id: str, command: str):
        try:
            r = subprocess.run(
                command, shell=True, cwd=ALLOWED_BASE_DIR,
                capture_output=True, text=True, timeout=300
            )
            output = r.stdout
            if r.stderr:
                output += f"\nSTDERR:\n{r.stderr}"
            if r.returncode != 0:
                output += f"\nExit code: {r.returncode}"
            set_status("completed" if r.returncode == 0 else "error", exit_code=r.returncode)
            output = _truncate_output(output.strip())
            status = "completed"
        except subprocess.TimeoutExpired:
            set_status("timeout", timeout_seconds=300)
            output = "Error: Timeout (300s)"
            status = "timeout"
        except Exception as e:
            set_status("error", error_type=type(e).__name__)
            output = f"Error: {e}"
            status = "error"
        self.tasks[task_id]["status"] = status
        self.tasks[task_id]["result"] = output
        with self._lock:
            self._notification_queue.append({
                "task_id": task_id,
                "status": status,
                "command": command,
                "result": output or "(no output)"
            })

    def check(self, task_id: str = None) -> str:
        """Check status of one task or list all."""
        if task_id:
            t = self.tasks.get(task_id)
            if not t:
                return f"Error: Unknown task {task_id}"
            return f"[{t['status']}] {t['command']}\n{t.get('result') or '(running)'}"
        lines = []
        for tid, t in self.tasks.items():
            lines.append(f"{tid}: [{t['status']}] {t['command'][:80]}")
        return "\n".join(lines) if lines else "No background tasks."

    def drain_notifications(self) -> list:
        """Return and clear all pending completion notifications."""
        with self._lock:
            notifs = list(self._notification_queue)
            self._notification_queue.clear()
        return notifs

BG = BackgroundManager()
