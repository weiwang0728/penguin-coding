from ..task_system import task_manager
from ..tool_registry import register_tool
from .base import Tool


@register_tool
class TaskTool(Tool):
    default_permission_level = "allow"
    name = "task"
    description = "Manage tasks with dependencies. Use 'create' to add tasks, 'update' to modify status/dependencies, 'list' to see all tasks."
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["create", "update", "list"],
                "description": "Action to perform",
            },
            "task_id": {
                "type": "integer",
                "description": "Task ID (required for update)",
            },
            "subject": {
                "type": "string",
                "description": "Task title (required for create)",
            },
            "description": {
                "type": "string",
                "description": "Task description (optional for create/update)",
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "completed"],
                "description": "New status (for update). 'blocked' is set automatically.",
            },
            "add_blocked_by": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Task IDs this task depends on (for create/update)",
            },
            "remove_blocked_by": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Task IDs to remove from dependencies (for update)",
            },
        },
        "required": ["action"],
    }

    def execute(self, **kwargs) -> str:
        action = kwargs["action"]
        task_id = kwargs.get("task_id")
        subject = kwargs.get("subject", "")
        description = kwargs.get("description", "")
        status = kwargs.get("status")
        add_blocked_by = kwargs.get("add_blocked_by")
        remove_blocked_by = kwargs.get("remove_blocked_by")
        try:
            if action == "create":
                return task_manager.create(subject, description, add_blocked_by)
            elif action == "update":
                if task_id is None:
                    return "Error: task_id is required for update action"
                return task_manager.update(
                    task_id, status, subject, description, add_blocked_by, remove_blocked_by
                )
            elif action == "list":
                return task_manager.list_all()
            else:
                return f"Error: unknown action '{action}'"
        except (ValueError, PermissionError) as e:
            return f"Error: {e}"
