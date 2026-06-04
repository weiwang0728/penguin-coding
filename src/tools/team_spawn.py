from .base import Tool


class TeamSpawnTool(Tool):
    name = "team_spawn"
    description = "Spawn a new teammate agent that runs in a background thread. The teammate can use tools and communicate via messages."
    parameters = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Unique name for the teammate",
            },
            "role": {
                "type": "string",
                "description": "Role description (e.g. 'tester', 'code reviewer')",
            },
            "prompt": {
                "type": "string",
                "description": "The task description for the teammate",
            },
        },
        "required": ["name", "role", "prompt"],
    }

    def execute(self, **kwargs) -> str:
        from ..agent_teams import TEAM_MANAGER
        name = kwargs["name"]
        role = kwargs["role"]
        prompt = kwargs["prompt"]
        return TEAM_MANAGER.spawn(name, role, prompt)
