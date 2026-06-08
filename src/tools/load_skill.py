from ..skill_loader import SKILL_LOADER
from .base import Tool


class LoadSkillTool(Tool):
    default_permission_level = "allow"
    name = "load_skill"
    description = "Load the full body of a named skill into the current context. Use when a task needs specialized instructions before acting."
    parameters = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the skill to load",
            },
        },
        "required": ["name"],
    }

    def execute(self, **kwargs) -> str:
        name = kwargs["name"]
        return SKILL_LOADER.get_content(name)
