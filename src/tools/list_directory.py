from .base import Tool
from .utils import resolve_and_validate_path


class ListDirectoryTool(Tool):
    default_permission_level = "allow"
    name = "list_directory"
    description = "List files and directories at the given path"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to list. Defaults to the working directory.",
            },
        },
        "required": [],
    }

    def execute(self, **kwargs) -> str:
        path = kwargs.get("path", ".")
        try:
            resolved = resolve_and_validate_path(path)
            if not resolved.is_dir():
                return f"Error: '{path}' is not a directory"
            entries = sorted(
                resolved.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())
            )
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
