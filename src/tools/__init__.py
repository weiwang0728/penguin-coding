"""Tools package: unified registration and exports."""

from .._constants import ALLOWED_BASE_DIR
from .dispatcher import dispatcher, execute_tool
from .utils import _changed_files, resolve_and_validate_path, unified_diff
from .._constants import check_dangerous_command, check_risky_command, _truncate_output, _truncate_for_context
from ..agent_teams import TEAM_MANAGER
from ..permissions import PermissionManager
from ..permissions_config import load_permissions_config

# Import all tool implementations
from .read_file import ReadFileTool
from .write_file import WriteFileTool
from .run_command import RunCommandTool
from .list_directory import ListDirectoryTool
from .search_files import SearchFilesTool
from .edit_file import EditFileTool
from .task import TaskTool
from .load_skill import LoadSkillTool
from .background_run import BackgroundRunTool
from .check_background import CheckBackgroundTool
from .team_spawn import TeamSpawnTool
from .team_list import TeamListTool
from .team_shutdown import TeamShutdownTool
from .team_send import TeamSendTool
from .team_broadcast import TeamBroadcastTool

# Instantiate and register all tools (except delegate, which needs runtime deps)
_tools = [
    ReadFileTool(),
    WriteFileTool(),
    RunCommandTool(),
    ListDirectoryTool(),
    SearchFilesTool(),
    EditFileTool(),
    TaskTool(),
    LoadSkillTool(),
    BackgroundRunTool(),
    CheckBackgroundTool(),
    TeamSpawnTool(),
    TeamListTool(),
    TeamShutdownTool(),
    TeamSendTool(),
    TeamBroadcastTool(),
]

for _tool in _tools:
    dispatcher.register(_tool)

# Initialize permission manager
_permissions_config = load_permissions_config()
permission_manager = PermissionManager(_permissions_config)
permission_manager.set_registry(dispatcher._registry)
dispatcher.set_permission_manager(permission_manager)

TOOL_DEFINITIONS = dispatcher.get_tool_definitions()

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
    return _tools[0].execute(path=path)

def write_file(path: str, content: str) -> str:
    return _tools[1].execute(path=path, content=content)

def run_command(command: str, timeout: int = 300) -> str:
    return _tools[2].execute(command=command, timeout=timeout)

def list_directory(path: str = ".") -> str:
    return _tools[3].execute(path=path)

def search_files(pattern: str, path: str = ".", file_pattern: str = "") -> str:
    return _tools[4].execute(pattern=pattern, path=path, file_pattern=file_pattern)

def edit_file(path: str, old_string: str = "", new_string: str = "", edits: list | None = None) -> str:
    kwargs = {"path": path}
    if edits is not None:
        kwargs["edits"] = edits
    else:
        kwargs["old_string"] = old_string
        kwargs["new_string"] = new_string
    return _tools[5].execute(**kwargs)

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
    "TEAM_MANAGER",
]
