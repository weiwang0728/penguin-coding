"""Memory tool — query and manual management interface.

Saving is automatic (extract_from_turn). This tool is for:
- recall: retrieve a specific memory by ID
- search: find by keyword
- list: see all memories
- delete: remove a memory
- save: explicit save (for user-requested "remember this")
"""

from ..memory import memory_store, MemoryType, MemoryScope
from ..tool_registry import register_tool
from .base import Tool


@register_tool
class MemoryTool(Tool):
    default_permission_level = "allow"
    name = "memory"
    description = (
        "Query and manage persistent memories. "
        "Use 'recall' to retrieve a specific memory by ID, "
        "'search' to find by keyword, 'list' to see all. "
        "Saving is automatic — memories are extracted from conversation context. "
        "Use 'save' only for explicitly requested memory saves."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["save", "recall", "search", "list", "delete"],
                "description": "Action to perform",
            },
            "title": {
                "type": "string",
                "description": "Short title (required for save)",
            },
            "content": {
                "type": "string",
                "description": "Full memory content in markdown (required for save)",
            },
            "memory_id": {
                "type": "string",
                "description": "Memory ID, e.g. 'global_001' or 'project_003' (required for recall/delete)",
            },
            "memory_type": {
                "type": "string",
                "enum": ["user", "project", "feedback", "reference"],
                "description": "Type of memory (default: project)",
            },
            "scope": {
                "type": "string",
                "enum": ["global", "project"],
                "description": "Storage scope. Global = user-level across all projects. Project = this workspace only.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Tags for categorization and search",
            },
            "query": {
                "type": "string",
                "description": "Search query (required for search)",
            },
            "relevance": {
                "type": "integer",
                "description": "Relevance priority 1-10 for context injection (default: 5). Higher = more likely to be injected.",
            },
        },
        "required": ["action"],
    }

    def execute(self, **kwargs) -> str:
        action = kwargs["action"]
        try:
            if action == "save":
                return memory_store.save(
                    title=kwargs.get("title", ""),
                    content=kwargs.get("content", ""),
                    memory_type=kwargs.get("memory_type", "project"),
                    scope=kwargs.get("scope", "project"),
                    tags=kwargs.get("tags"),
                    relevance=kwargs.get("relevance", 5),
                )
            elif action == "recall":
                return memory_store.recall(
                    memory_id=kwargs.get("memory_id", ""),
                    scope=kwargs.get("scope"),
                )
            elif action == "search":
                return memory_store.search(
                    query=kwargs.get("query", ""),
                    scope=kwargs.get("scope"),
                )
            elif action == "list":
                return memory_store.list_memories(
                    scope=kwargs.get("scope"),
                    memory_type=kwargs.get("memory_type"),
                )
            elif action == "delete":
                return memory_store.delete(
                    memory_id=kwargs.get("memory_id", ""),
                    scope=kwargs.get("scope"),
                )
            else:
                return f"Error: unknown action '{action}'"
        except (ValueError, PermissionError) as e:
            return f"Error: {e}"
