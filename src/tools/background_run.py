from ..background_tasks import BG
from .base import Tool


class BackgroundRunTool(Tool):
    name = "background_run"
    description = "Run command in background thread. Returns task_id immediately."
    parameters = {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    }

    def execute(self, **kwargs) -> str:
        command = kwargs["command"]
        return BG.run(command)
