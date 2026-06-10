from ..tool_registry import register_tool
from .base import Tool


@register_tool
class TeamListTool(Tool):
    default_permission_level = "allow"
    name = "team_list"
    description = "List all team members and their current status."
    parameters = {
        "type": "object",
        "properties": {},
    }

    def execute(self, **kwargs) -> str:
        from ..agent_teams import TEAM_MANAGER
        return TEAM_MANAGER.list_members()
