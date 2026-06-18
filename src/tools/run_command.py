import os
import subprocess

from .._constants import ALLOWED_BASE_DIR, check_dangerous_command, _truncate_output
from ..tool_registry import register_tool
from .base import Tool


@register_tool
class RunCommandTool(Tool):
    name = "run_command"
    description = "Run a shell command and return its output. Use longer timeouts for install/build commands."
    default_permission_level = "confirm"
    parameters = {
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
            "cwd": {
                "type": "string",
                "description": "Working directory for the command. Defaults to the workspace directory.",
            },
        },
        "required": ["command"],
    }

    def execute(self, **kwargs) -> str:
        command = kwargs["command"]
        timeout = kwargs.get("timeout", 300)
        cwd = kwargs.get("cwd")

        # In PRDBench mode, allow custom cwd; otherwise use default
        if cwd:
            cwd = str(cwd)
        else:
            cwd = os.getenv("CODE_AGENT_WORKSPACE_DIR", str(ALLOWED_BASE_DIR))

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
                cwd=cwd,
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
