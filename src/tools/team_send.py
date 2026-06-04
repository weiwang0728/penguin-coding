from .base import Tool


class TeamSendTool(Tool):
    name = "team_send"
    description = "Send a message to a specific teammate."
    parameters = {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Name of the teammate to send to",
            },
            "content": {
                "type": "string",
                "description": "Message content",
            },
        },
        "required": ["to", "content"],
    }

    def execute(self, **kwargs) -> str:
        from ..agent_teams import TEAM_MANAGER
        to = kwargs["to"]
        content = kwargs["content"]
        return TEAM_MANAGER.send_message("coordinator", to, content)
