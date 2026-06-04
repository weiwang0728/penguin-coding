from .base import Tool


class TeamListTool(Tool):
    name = "team_list"
    description = "List all team members and their current status."
    parameters = {
        "type": "object",
        "properties": {},
    }

    def execute(self, **kwargs) -> str:
        from ..agent_teams import TEAM_MANAGER
        return TEAM_MANAGER.list_members()
