from .base import Tool


class TeamBroadcastTool(Tool):
    default_permission_level = "allow"
    name = "team_broadcast"
    description = "Broadcast a message to all teammates."
    parameters = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Message content to broadcast",
            },
        },
        "required": ["content"],
    }

    def execute(self, **kwargs) -> str:
        from ..agent_teams import TEAM_MANAGER
        content = kwargs["content"]
        return TEAM_MANAGER.broadcast_message("coordinator", content)
