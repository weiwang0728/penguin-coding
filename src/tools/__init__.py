"""Tools package: unified registration and exports."""

from typing import Any

from .._constants import ALLOWED_BASE_DIR
from .dispatcher import ToolDispatcher
from .utils import _changed_files, resolve_and_validate_path, unified_diff
from .._constants import check_dangerous_command, check_risky_command, _truncate_output, _truncate_for_context
from ..agent_teams import TEAM_MANAGER
from ..permissions import PermissionManager
from ..permissions_config import load_permissions_config
from ..tool_registry import ToolRegistry

# Import tool modules to trigger @register_tool decorators
from . import read_file, write_file, run_command, list_directory, search_files
from . import edit_file, task, load_skill, background_run, check_background
from . import team_spawn, team_list, team_shutdown, team_send, team_broadcast

# ── Default global dispatcher (backward compatibility) ──
# Creates a dispatcher with ALL tools registered, for existing code
# that imports `dispatcher` / `TOOL_DEFINITIONS` / `execute_tool`.

dispatcher = ToolDispatcher()
for _name in ToolRegistry.all_names():
    _inst = ToolRegistry.create_instance(_name)
    if _inst:
        dispatcher.register(_inst)

# Initialize permission manager on global dispatcher
_permissions_config = load_permissions_config()
permission_manager = PermissionManager(_permissions_config)
permission_manager.set_registry(dispatcher._registry)
dispatcher.set_permission_manager(permission_manager)

TOOL_DEFINITIONS = dispatcher.get_tool_definitions()


def execute_tool(name: str, args: dict[str, Any], skip_permission_check: bool = False) -> str:
    """Execute a tool via the global dispatcher. For Agent-specific dispatch, use agent.dispatcher.dispatch()."""
    return dispatcher.dispatch(name, args, skip_permission_check)

# Delegate tool schema — registered dynamically at runtime via register_delegate_tool()
DELEGATE_SCHEMA = {
    "name": "delegate",
    "description": "Spawn a sub-agent to handle a task in an isolated context. The sub-agent can use all tools except delegate itself. Use for research, exploration, or multi-step work that would bloat the parent context. The sub-agent returns a concise summary — intermediate tool calls are discarded.",
    "input_schema": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The task description for the sub-agent. Be specific about what to do and what information to return.",
            },
            "max_iterations": {
                "type": "integer",
                "description": "Max iterations for the sub-agent. Default 20. Increase for complex tasks.",
            },
        },
        "required": ["prompt"],
    },
}


def register_delegate_tool(client) -> None:
    """Register the delegate tool handler. Must be called after client creation."""
    from ..agent_loop import run_subagent

    def handle_delegate(prompt: str, max_iterations: int = 20) -> str:
        return run_subagent(client, prompt, max_iterations)

    dispatcher.register_dynamic("delegate", handle_delegate, DELEGATE_SCHEMA)
    TOOL_DEFINITIONS.append(DELEGATE_SCHEMA)


# Convenience functions — allow direct calls like read_file("path")
def read_file(path: str) -> str:
    return ToolRegistry.create_instance("read_file").execute(path=path)

def write_file(path: str, content: str) -> str:
    return ToolRegistry.create_instance("write_file").execute(path=path, content=content)

def run_command(command: str, timeout: int = 300) -> str:
    return ToolRegistry.create_instance("run_command").execute(command=command, timeout=timeout)

def list_directory(path: str = ".") -> str:
    return ToolRegistry.create_instance("list_directory").execute(path=path)

def search_files(pattern: str, path: str = ".", file_pattern: str = "") -> str:
    return ToolRegistry.create_instance("search_files").execute(pattern=pattern, path=path, file_pattern=file_pattern)

def edit_file(path: str, old_string: str = "", new_string: str = "", edits: list | None = None) -> str:
    kwargs = {"path": path}
    if edits is not None:
        kwargs["edits"] = edits
    else:
        kwargs["old_string"] = old_string
        kwargs["new_string"] = new_string
    return ToolRegistry.create_instance("edit_file").execute(**kwargs)

__all__ = [
    "dispatcher",
    "execute_tool",
    "TOOL_DEFINITIONS",
    "ALLOWED_BASE_DIR",
    "register_delegate_tool",
    "resolve_and_validate_path",
    "check_dangerous_command",
    "check_risky_command",
    "_truncate_output",
    "_truncate_for_context",
    "read_file",
    "write_file",
    "run_command",
    "list_directory",
    "search_files",
    "edit_file",
    "permission_manager",
    "ToolRegistry",
    "TEAM_MANAGER",
]
