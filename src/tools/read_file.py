from .._constants import MAX_READ_SIZE
from ..tool_registry import register_tool
from .base import Tool
from .utils import resolve_and_validate_path


@register_tool
class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the contents of a file"
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read",
            }
        },
        "required": ["path"],
    }

    def execute(self, **kwargs) -> str:
        path = kwargs["path"]
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
