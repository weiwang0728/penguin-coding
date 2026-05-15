import json
from pathlib import Path

VALID_STATUSES = ("pending", "in_progress", "completed", "blocked")


class TaskManager:
    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(exist_ok=True)
        self._next_id = self._max_id() + 1

    def _max_id(self) -> int:
        ids = [int(f.stem.split("_")[1]) for f in self.dir.glob("task_*.json")]
        return max(ids) if ids else 0

    def _load(self, task_id: int) -> dict:
        path = self.dir / f"task_{task_id}.json"
        if not path.exists():
            raise ValueError(f"Task {task_id} not found")
        return json.loads(path.read_text())

    def _save(self, task: dict):
        path = self.dir / f"task_{task['id']}.json"
        path.write_text(json.dumps(task, indent=2, ensure_ascii=False))

    def _validate_blocked_by(self, ids: list[int]) -> None:
        for bid in ids:
            try:
                task = self._load(bid)
            except ValueError:
                raise ValueError(f"Dependency task {bid} not found")
            if task["status"] == "completed":
                raise ValueError(f"Dependency task {bid} is already completed")

    def _count_in_progress(self) -> int:
        count = 0
        for f in self.dir.glob("task_*.json"):
            task = json.loads(f.read_text())
            if task.get("status") == "in_progress":
                count += 1
        return count

    def _clear_dependency(self, completed_id: int):
        for f in self.dir.glob("task_*.json"):
            task = json.loads(f.read_text())
            if completed_id in task.get("blockedBy", []):
                task["blockedBy"].remove(completed_id)
                self._save(task)
                if not task["blockedBy"] and task["status"] == "blocked":
                    task["status"] = "pending"
                    self._save(task)

    def _auto_status(self, task: dict) -> dict:
        if task["blockedBy"] and task["status"] == "pending":
            task["status"] = "blocked"
        elif not task["blockedBy"] and task["status"] == "blocked":
            task["status"] = "pending"
        return task

    def create(self, subject: str, description: str = "",
               add_blocked_by: list[int] | None = None) -> str:
        blocked_by = list(add_blocked_by) if add_blocked_by else []
        if blocked_by:
            self._validate_blocked_by(blocked_by)

        task = {
            "id": self._next_id,
            "subject": subject,
            "description": description,
            "status": "pending",
            "blockedBy": blocked_by,
            "owner": "",
        }
        self._next_id += 1

        task = self._auto_status(task)
        self._save(task)
        return self.render()

    def get(self, task_id: int) -> str:
        return json.dumps(self._load(task_id), indent=2, ensure_ascii=False)

    def update(self, task_id: int, status: str | None = None,
               subject: str | None = None, description: str | None = None,
               add_blocked_by: list[int] | None = None,
               remove_blocked_by: list[int] | None = None) -> str:
        task = self._load(task_id)

        if status is not None:
            if status not in VALID_STATUSES:
                raise ValueError(f"Invalid status: {status}")
            if status == "in_progress" and task["status"] != "in_progress":
                if self._count_in_progress() > 0:
                    raise ValueError("Only one task can be in_progress at a time")
            task["status"] = status
            if status == "completed":
                task["blockedBy"] = []
                self._save(task)
                self._clear_dependency(task_id)
                return self.render()

        if subject is not None:
            task["subject"] = subject
        if description is not None:
            task["description"] = description

        if add_blocked_by:
            self._validate_blocked_by(add_blocked_by)
            task["blockedBy"] = list(set(task["blockedBy"] + add_blocked_by))
        if remove_blocked_by:
            task["blockedBy"] = [x for x in task["blockedBy"] if x not in remove_blocked_by]

        task = self._auto_status(task)
        self._save(task)
        return self.render()

    def list_all(self) -> str:
        return self.render()

    def render(self) -> str:
        tasks = []
        files = sorted(
            self.dir.glob("task_*.json"),
            key=lambda f: int(f.stem.split("_")[1]),
        )
        for f in files:
            tasks.append(json.loads(f.read_text()))

        if not tasks:
            return "No tasks."

        lines = []
        markers = {
            "pending": "[ ]", "in_progress": "[>]",
            "completed": "[x]", "blocked": "[!]",
        }
        for t in tasks:
            marker = markers.get(t["status"], "[?]")
            blocked = f" (blocked by: {t['blockedBy']})" if t.get("blockedBy") else ""
            lines.append(f"{marker} #{t['id']}: {t['subject']}{blocked}")

        done = sum(1 for t in tasks if t["status"] == "completed")
        lines.append(f"\n({done}/{len(tasks)} completed)")
        return "\n".join(lines)


TASKS_DIR = Path(__file__).resolve().parent.parent / "workspace" / ".penguin_tasks"
task_manager = TaskManager(TASKS_DIR)
