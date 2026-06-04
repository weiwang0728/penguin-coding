from .base import Tool
from .utils import resolve_and_validate_path, unified_diff, _changed_files


class EditFileTool(Tool):
    name = "edit_file"
    description = "Replace a specific string in a file with a new string"
    parameters = {
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
    }

    def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        old_string = kwargs["old_string"]
        new_string = kwargs["new_string"]
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
            _changed_files.add(path)
            result = f"Successfully edited {path} (replaced 1 occurrence)"
            diff = unified_diff(content, new_content, path)
            if diff:
                result += f"\n\n{diff}"
            return result
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error editing file: {e}"
