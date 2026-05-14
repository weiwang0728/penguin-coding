import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

from task_system import task_manager
ALLOWED_BASE_DIR = Path(os.getcwd()).resolve()
MAX_READ_SIZE = 100 * 1024  # 100KB
MAX_OUTPUT_LENGTH = 30_000  # ~30K chars for command output
MAX_TOOL_RESULT_CHARS = 10_000  # Max chars per tool result in context

DANGEROUS_COMMANDS = [
    # Destructive file operations
    r"\brm\s+-rf\s+/",
    r"\brm\s+-rf\s+~",
    r"\brm\s+-rf\s+\$HOME",
    r"\bmkfs\.",
    r"\bdd\s+if=.*of=/dev/",
    r">\s*/etc/passwd",
    r">\s*/etc/shadow",
    r">\s+/dev/(sda|nvme|hd)",
    # Fork bomb
    r"\b:(){ :|:& };:",
    # Permission escalation
    r"\bchmod\s+-R\s+777\s+/",
    r"\bchown\s+-R\s+.*\s+/",
    # Privilege escalation
    r"\bsudo\s+rm\s+-rf",
    r"\bsu\s+-",
    r"\bpasswd\b",
    r"\buseradd\b",
    r"\busermod\b",
    r"\bgroupadd\b",
    # System disruption
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+0",
    r"\bsystemctl\s+(stop|restart)\s+(ssh|network|systemd)",
    # Cluster/container destruction
    r"\bkubectl\s+delete\s+.*--all",
    r"\bdocker\s+(rm|kill)\s+.*\*",
    # Remote code execution
    r"\bcurl\s+.*\|\s*sh",
    r"\bwget\s+.*\|\s*sh",
    r"\beval\s*\$",
    r"\bexec\s*\$",
    # Shell injection via command substitution
    r"\$\(",
    r"`",
    # Pipe to shell variants
    r"\|\s*(ba)?sh\b",
    # Environment/credential exfiltration
    r"\bexport\s+\w*(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)",
    # Overwrite critical files
    r"\btee\s+/etc/(passwd|shadow|sudoers|hosts)",
    # Kill critical processes
    r"\bkill\s+-9\s+1\b",
    r"\bkillall\s+(init|systemd|sshd)",
]

SHELL_INJECTION_PATTERNS = [re.compile(p, re.IGNORECASE) for p in [r"\$\(", r"`"]]
DANGEROUS_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in DANGEROUS_COMMANDS if p not in [r"\$\(", r"`"]
]

TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                }
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return its output. Use longer timeouts for install/build commands.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Default 60. Use 300 for installs/builds, 600 for heavy builds.",
                },
            },
            "required": ["command"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories at the given path",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to the working directory.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "search_files",
        "description": "Search for a text pattern in files using grep",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern to search for",
                },
                "path": {
                    "type": "string",
                    "description": "Directory or file to search in. Defaults to the working directory.",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter files, e.g. '*.py'. Defaults to all files.",
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace a specific string in a file with a new string",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit",
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact text to find and replace",
                },
                "new_string": {
                    "type": "string",
                    "description": "The replacement text",
                },
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    {
        "name": "task",
        "description": "Manage tasks with dependencies. Use 'create' to add tasks, 'update' to modify status/dependencies, 'list' to see all tasks.",
        "input_schema": {
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
        },
    }
]


class ToolDispatcher:
    def __init__(self) -> None:
        self._registry: dict[str, Callable[..., str]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}

    def register(
        self, name: str, schema: dict[str, Any] | None = None
    ) -> Callable[[Callable[..., str]], Callable[..., str]]:
        def decorator(func: Callable[..., str]) -> Callable[..., str]:
            self._registry[name] = func
            if schema:
                self._schemas[name] = schema
            return func

        return decorator

    def dispatch(self, name: str, args: dict[str, Any]) -> str:
        if name not in self._registry:
            return f"Unknown tool: {name}"
        errors = self._validate_args(name, args)
        if errors:
            return f"Error: invalid arguments for '{name}': {'; '.join(errors)}"
        try:
            return self._registry[name](**args)
        except TypeError as e:
            return f"Error calling tool '{name}': {e}"

    def list_tools(self) -> list[str]:
        return list(self._registry.keys())

    def _validate_args(self, name: str, args: dict[str, Any]) -> list[str]:
        schema = self._schemas.get(name)
        if not schema:
            return []
        input_schema = schema.get("input_schema", schema)
        errors: list[str] = []
        required = input_schema.get("required", [])
        for field in required:
            if field not in args:
                errors.append(f"missing required field '{field}'")
        properties = input_schema.get("properties", {})
        for key, value in args.items():
            if key not in properties:
                errors.append(f"unexpected field '{key}'")
                continue
            expected_type = properties[key].get("type")
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"field '{key}' must be a string")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"field '{key}' must be an integer")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"field '{key}' must be an array")
        return errors


dispatcher = ToolDispatcher()


def resolve_and_validate_path(path: str) -> Path:
    try:
        resolved = (ALLOWED_BASE_DIR / path).resolve()
        resolved.relative_to(ALLOWED_BASE_DIR)
        if resolved.is_symlink():
            real_target = resolved.resolve()
            real_target.relative_to(ALLOWED_BASE_DIR)
        return resolved
    except (ValueError, RuntimeError):
        raise PermissionError(
            f"Path '{path}' is outside the allowed directory: {ALLOWED_BASE_DIR}"
        )


def check_dangerous_command(command: str) -> str | None:
    for pattern in SHELL_INJECTION_PATTERNS:
        if pattern.search(command):
            return f"Shell command substitution blocked for safety (matched '{pattern.pattern}'). Use direct commands instead of $() or backtick substitution."
    for pattern in DANGEROUS_PATTERNS:
        if pattern.search(command):
            return f"Dangerous command detected and blocked: pattern '{pattern.pattern}'"
    return None


def _truncate_output(output: str, max_length: int = MAX_OUTPUT_LENGTH) -> str:
    if len(output) <= max_length:
        return output
    half = max_length // 2
    return (
        output[:half]
        + f"\n\n... [Output truncated: {len(output)} chars total, showing first and last {half} chars] ...\n\n"
        + output[-half:]
    )


def _truncate_for_context(text: str, max_chars: int = MAX_TOOL_RESULT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + f"\n... [Result truncated for context: {len(text)} chars total] ...\n"
        + text[-half:]
    )


@dispatcher.register("read_file", TOOL_DEFINITIONS[0])
def read_file(path: str) -> str:
    try:
        resolved_path = resolve_and_validate_path(path)
        file_size = resolved_path.stat().st_size
        with open(resolved_path, "r", encoding="utf-8") as f:
            content = f.read(MAX_READ_SIZE)
            if file_size > MAX_READ_SIZE or f.read(1):
                content += f"\n... [File truncated: {file_size} bytes total, showing first {MAX_READ_SIZE} bytes]"
            return content
    except PermissionError as e:
        return f"Error: {e}"
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except UnicodeDecodeError:
        return f"Error: Cannot read binary file: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@dispatcher.register("write_file", TOOL_DEFINITIONS[1])
def write_file(path: str, content: str) -> str:
    try:
        resolved_path = resolve_and_validate_path(path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error writing file: {e}"


@dispatcher.register("run_command", TOOL_DEFINITIONS[2])
def run_command(command: str, timeout: int = 300) -> str:
    danger_check = check_dangerous_command(command)
    if danger_check:
        return f"Error: {danger_check}"

    timeout = max(10, min(timeout, 600))

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=ALLOWED_BASE_DIR,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
        return _truncate_output(output) or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error running command: {e}"


@dispatcher.register("list_directory", TOOL_DEFINITIONS[3])
def list_directory(path: str = ".") -> str:
    try:
        resolved = resolve_and_validate_path(path)
        if not resolved.is_dir():
            return f"Error: '{path}' is not a directory"
        entries = sorted(resolved.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = []
        for entry in entries:
            prefix = "[DIR]  " if entry.is_dir() else "[FILE] "
            size = ""
            try:
                if entry.is_file():
                    size = f" ({entry.stat().st_size} bytes)"
            except OSError:
                pass
            lines.append(f"{prefix}{entry.name}{size}")
        return "\n".join(lines) if lines else "(empty directory)"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error listing directory: {e}"


@dispatcher.register("search_files", TOOL_DEFINITIONS[4])
def search_files(pattern: str, path: str = ".", file_pattern: str = "") -> str:
    try:
        resolve_and_validate_path(path)
    except PermissionError as e:
        return f"Error: {e}"

    cmd = ["grep", "-rn", "--color=never", "-E", pattern]
    if file_pattern:
        cmd.extend(["--include", file_pattern])
    cmd.append(path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=ALLOWED_BASE_DIR,
        )
        if result.returncode == 1:
            return "No matches found."
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}" if result.stderr else "Search failed."
        return _truncate_output(result.stdout)
    except subprocess.TimeoutExpired:
        return "Error: Search timed out after 30 seconds"
    except Exception as e:
        return f"Error searching files: {e}"


@dispatcher.register("edit_file", TOOL_DEFINITIONS[5])
def edit_file(path: str, old_string: str, new_string: str) -> str:
    try:
        resolved_path = resolve_and_validate_path(path)
        if not resolved_path.is_file():
            return f"Error: File not found: {path}"

        content = resolved_path.read_text(encoding="utf-8")
        count = content.count(old_string)
        if count == 0:
            return f"Error: old_string not found in '{path}'"
        if count > 1:
            return f"Error: old_string found {count} times in '{path}' — must be unique to avoid ambiguous edits"

        new_content = content.replace(old_string, new_string, 1)
        resolved_path.write_text(new_content, encoding="utf-8")
        return f"Successfully edited {path} (replaced 1 occurrence)"
    except PermissionError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error editing file: {e}"

@dispatcher.register("task", TOOL_DEFINITIONS[6])
def handle_task(action: str, task_id: int = None, subject: str = "",
                description: str = "", status: str = None,
                add_blocked_by: list = None, remove_blocked_by: list = None) -> str:
    try:
        if action == "create":
            return task_manager.create(subject, description, add_blocked_by)
        elif action == "update":
            if task_id is None:
                return "Error: task_id is required for update action"
            return task_manager.update(task_id, status, subject, description,
                                       add_blocked_by, remove_blocked_by)
        elif action == "list":
            return task_manager.list_all()
        else:
            return f"Error: unknown action '{action}'"
    except (ValueError, PermissionError) as e:
        return f"Error: {e}"

def execute_tool(name: str, args: dict[str, Any]) -> str:
    return dispatcher.dispatch(name, args)
