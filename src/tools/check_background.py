from ..background_tasks import BG
from .base import Tool


class CheckBackgroundTool(Tool):
    name = "check_background"
    description = "Check background task status. Omit task_id to list all."
    parameters = {
        "type": "object",
        "properties": {"task_id": {"type": "string"}},
    }

    def execute(self, **kwargs) -> str:
        task_id = kwargs.get("task_id")
        return BG.check(task_id)
