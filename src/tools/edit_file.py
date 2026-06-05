from .base import Tool
from .utils import resolve_and_validate_path, unified_diff, _changed_files, fuzzy_replace


class EditFileTool(Tool):
    name = "edit_file"
    description = """Replace text in an existing file. Use this instead of write_file for editing — it's more token-efficient.
Rules:
- old_string must match the file content exactly (including whitespace/indentation). If the match fails, the system retries with normalization (ignoring trailing whitespace and blank lines).
- Include 2-3 lines of surrounding context in old_string to ensure uniqueness.
- For multiple edits in the same file, use the 'edits' array parameter to apply them in one call — this is more efficient than multiple separate calls.
- The tool returns a diff of the changes, so you do NOT need to read_file again to verify the result."""
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to edit",
            },
            "old_string": {
                "type": "string",
                "description": "The exact text to find and replace. Include 2-3 lines of context for uniqueness.",
            },
            "new_string": {
                "type": "string",
                "description": "The replacement text",
            },
            "edits": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "old_string": {
                            "type": "string",
                            "description": "The exact text to find and replace",
                        },
                        "new_string": {
                            "type": "string",
                            "description": "The replacement text",
                        },
                    },
                    "required": ["old_string", "new_string"],
                },
                "description": "Multiple edits to apply in order. Use instead of old_string/new_string for batch edits in the same file.",
            },
        },
        "required": ["path"],
    }

    def execute(self, **kwargs) -> str:
        path = kwargs["path"]
        edits = kwargs.get("edits")
        old_string = kwargs.get("old_string")
        new_string = kwargs.get("new_string")

        # Validate: either edits array or old_string/new_string pair, not both
        if edits and (old_string or new_string):
            return "Error: Use either 'edits' array or 'old_string'/'new_string' pair, not both"
        if not edits and not old_string:
            return "Error: Provide either 'edits' array or 'old_string'/'new_string' pair"

        # Normalize single edit into edits list
        if not edits:
            edits = [{"old_string": old_string, "new_string": new_string}]

        try:
            resolved_path = resolve_and_validate_path(path)
            if not resolved_path.is_file():
                return f"Error: File not found: {path}"

            content = resolved_path.read_text(encoding="utf-8")
            original_content = content
            match_types = []

            for i, edit in enumerate(edits):
                result = fuzzy_replace(content, edit["old_string"], edit["new_string"])
                if result is None:
                    # Check why it failed for better error message
                    count = content.count(edit["old_string"])
                    if count > 1:
                        return (
                            f"Error in edit #{i + 1}: old_string found {count} times in '{path}' "
                            f"— must be unique to avoid ambiguous edits"
                        )
                    if count == 0:
                        return (
                            f"Error in edit #{i + 1}: old_string not found in '{path}' "
                            f"(exact match and normalized match both failed)"
                        )

                new_content, match_type = result
                match_types.append(match_type)
                content = new_content

            # Write the final content
            resolved_path.write_text(content, encoding="utf-8")
            _changed_files.add(path)

            # Build result message
            edit_count = len(edits)
            match_summary = ", ".join(
                f"#{i + 1}: {t}" for i, t in enumerate(match_types)
            )
            result = f"Successfully edited {path} ({edit_count} edit(s), matches: {match_summary})"
            diff = unified_diff(original_content, content, path)
            if diff:
                result += f"\n\n{diff}"
            return result

        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error editing file: {e}"
