from ..tool_registry import register_tool
from ..observability import set_status
from .base import Tool
from .utils import resolve_and_validate_path, unified_diff, _changed_files, fuzzy_replace


def _nearest_match_hint(content: str, old_string: str) -> str:
    """Best-effort hint for a failed edit: locate the first non-empty line of
    old_string in the file and report where it appears, so the model can
    re-read the right region instead of guessing."""
    lines = content.split('\n')
    anchor = next((ln.strip() for ln in old_string.split('\n') if ln.strip()), '')
    if not anchor:
        return f"File has {len(lines)} lines; old_string was empty after normalization."
    hits = [i + 1 for i, ln in enumerate(lines) if anchor in ln]
    if hits:
        show = ', '.join(str(h) for h in hits[:3])
        more = f" (and {len(hits) - 3} more)" if len(hits) > 3 else ""
        return (f"The first line of your old_string appears at line(s) {show}{more}, "
                f"but the surrounding content differs — re-read that region "
                f"(read_file with offset={max(1, hits[0] - 10)}) and retry with the exact text.")
    anchor40 = anchor[:40]
    partial = [i + 1 for i, ln in enumerate(lines) if anchor40 and anchor40 in ln]
    if partial:
        return (f"A line similar to your old_string's first line appears at line(s) "
                f"{', '.join(str(h) for h in partial[:3])} — re-read that region and retry with the exact text.")
    return (f"None of old_string's lines match the file ({len(lines)} lines) — "
            f"the file content differs from what you expect; re-read it before editing.")


@register_tool
class EditFileTool(Tool):
    name = "edit_file"
    default_permission_level = "confirm"
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
            set_status("invalid_arguments")
            return "Error: Use either 'edits' array or 'old_string'/'new_string' pair, not both"
        if not edits and not old_string:
            set_status("invalid_arguments")
            return "Error: Provide either 'edits' array or 'old_string'/'new_string' pair"

        # Normalize single edit into edits list
        if not edits:
            edits = [{"old_string": old_string, "new_string": new_string}]

        try:
            resolved_path = resolve_and_validate_path(path)
            if not resolved_path.is_file():
                set_status("error", error_type="FileNotFoundError")
                return f"Error: File not found: {path}"

            content = resolved_path.read_text(encoding="utf-8")
            original_content = content
            match_types = []

            for i, edit in enumerate(edits):
                result = fuzzy_replace(content, edit["old_string"], edit["new_string"])
                if result is None:
                    set_status("error", error_type="EditMatchError")
                    # Check why it failed for better error message
                    count = content.count(edit["old_string"])
                    if count > 1:
                        return (
                            f"Error in edit #{i + 1}: old_string found {count} times in '{path}' "
                            f"— must be unique to avoid ambiguous edits"
                        )
                    if count == 0:
                        hint = _nearest_match_hint(content, edit["old_string"])
                        return (
                            f"Error in edit #{i + 1}: old_string not found in '{path}' "
                            f"(exact match and normalized match both failed). {hint}"
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
            set_status("permission_denied")
            return f"Error: {e}"
        except Exception as e:
            set_status("error", error_type=type(e).__name__)
            return f"Error editing file: {e}"
