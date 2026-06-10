from ..tool_registry import register_tool
from .base import Tool


@register_tool
class TeamShutdownTool(Tool):
    default_permission_level = "confirm"
    name = "team_shutdown"
    description = "Send a shutdown request to a teammate agent."
    parameters = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the teammate to shut down",
            },
        },
        "required": ["name"],
    }

    def execute(self, **kwargs) -> str:
        from ..agent_teams import TEAM_MANAGER
        name = kwargs["name"]
        return TEAM_MANAGER.shutdown(name)
