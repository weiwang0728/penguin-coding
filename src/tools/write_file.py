from .base import Tool
from .utils import resolve_and_validate_path, unified_diff, _changed_files


class WriteFileTool(Tool):
    name = "write_file"
    description = "Write content to a file"
    default_permission_level = "confirm"
    parameters = {
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
    }

    def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        content = kwargs["content"]
        try:
            resolved_path = resolve_and_validate_path(path)
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            old_content = ""
            if resolved_path.is_file():
                old_content = resolved_path.read_text(encoding="utf-8")
            with open(resolved_path, "w", encoding="utf-8") as f:
                f.write(content)
            _changed_files.add(path)
            result = f"Successfully wrote to {path}"
            if old_content != content:
                diff = unified_diff(old_content, content, path)
                if diff:
                    result += f"\n\n{diff}"
            return result
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error writing file: {e}"
