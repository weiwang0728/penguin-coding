from ..background_tasks import BG
from ..tool_registry import register_tool
from .base import Tool


@register_tool
class BackgroundRunTool(Tool):
    default_permission_level = "confirm"
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
