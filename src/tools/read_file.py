from .._constants import MAX_READ_SIZE
from ..tool_registry import register_tool
from ..observability import set_status
from .base import Tool
from .utils import resolve_and_validate_path


@register_tool
class ReadFileTool(Tool):
    name = "read_file"
    description = "Read the contents of a file. Returns up to 2000 lines per call; use offset/limit to page through large files — the tool reports the total line count and the offset for the next page. Prefer relative paths."
    default_permission_level = "allow"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read",
            },
            "offset": {
                "type": "integer",
                "description": "1-based line number to start reading from (default: 1)",
            },
            "limit": {
                "type": "integer",
                "description": "Max number of lines to return (default: 2000)",
            },
        },
        "required": ["path"],
    }

    def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        offset = kwargs.get("offset") or 1
        limit = kwargs.get("limit") or 2000
        try:
            if offset < 1:
                offset = 1
            if limit is not None and limit < 1:
                limit = 1
            resolved_path = resolve_and_validate_path(path)
            file_size = resolved_path.stat().st_size
            with open(resolved_path, "r", encoding="utf-8", errors="strict") as f:
                lines = f.readlines()
            total_lines = len(lines)
            start = offset - 1
            selected = lines[start:start + limit] if limit is not None else lines[start:]
            content = "".join(selected)
            end_line = start + len(selected)
            content = f"[Showing lines {start + 1}-{end_line} of {total_lines} total]\n" + content
            if end_line < total_lines:
                content += f"\n... [File continues: use offset={end_line + 1} to read more]"
            if len(content) > MAX_READ_SIZE:
                content = content[:MAX_READ_SIZE] + f"\n... [Output truncated at {MAX_READ_SIZE} bytes; use offset/limit to read smaller ranges]"
            return content
        except PermissionError as e:
            set_status("permission_denied")
            return f"Error: {e}"
        except FileNotFoundError:
            set_status("error", error_type="FileNotFoundError")
            return f"Error: File not found: {path}"
        except UnicodeDecodeError:
            set_status("error", error_type="UnicodeDecodeError")
            return f"Error: Cannot read binary file: {path}"
        except Exception as e:
            set_status("error", error_type=type(e).__name__)
            return f"Error reading file: {e}"
