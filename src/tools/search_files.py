import subprocess

from .._constants import ALLOWED_BASE_DIR, _truncate_output
from .base import Tool
from .utils import resolve_and_validate_path


class SearchFilesTool(Tool):
    name = "search_files"
    description = "Search for a text pattern in files using grep"
    parameters = {
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
    }

    def execute(self, **kwargs) -> str:
        pattern = kwargs["pattern"]
        path = kwargs.get("path", ".")
        file_pattern = kwargs.get("file_pattern", "")
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
                return (
                    f"Error: {result.stderr.strip()}" if result.stderr else "Search failed."
                )
            return _truncate_output(result.stdout)
        except subprocess.TimeoutExpired:
            return "Error: Search timed out after 30 seconds"
        except Exception as e:
            return f"Error searching files: {e}"
