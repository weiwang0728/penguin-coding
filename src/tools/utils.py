"""Shared utilities for tool implementations."""

import difflib
from pathlib import Path

from .._constants import ALLOWED_BASE_DIR
from ..skill_loader import SKILLS_DIR

ALLOWED_DIRS = [ALLOWED_BASE_DIR, SKILLS_DIR]

_changed_files: set[str] = set()


def normalize(text: str) -> str:
    """Normalize text for fuzzy matching: strip trailing whitespace and trailing blank lines."""
    lines = [line.rstrip() for line in text.split('\n')]
    while lines and lines[-1] == '':
        lines.pop()
    return '\n'.join(lines)


def _find_normalized_match(content: str, old_string: str) -> tuple[int, int] | None:
    """Find the line range in content that matches old_string after normalization.

    Returns (start_line, end_line) as 0-based inclusive indices, or None if no match.
    """
    norm_old = normalize(old_string)
    norm_content = normalize(content)

    if norm_old not in norm_content:
        return None

    # Map normalized match position back to original line range
    norm_old_lines = norm_old.split('\n')
    old_line_count = len(norm_old_lines)

    content_lines = content.split('\n')
    norm_content_lines = norm_content.split('\n')

    # Find which line in norm_content the match starts at
    match_start_in_norm = None
    for i in range(len(norm_content_lines) - old_line_count + 1):
        candidate = '\n'.join(norm_content_lines[i:i + old_line_count])
        if candidate == norm_old:
            match_start_in_norm = i
            break

    if match_start_in_norm is None:
        return None

    # Map norm_content line index back to content line index
    # norm_content strips trailing blanks and rstrips each line,
    # but preserves the same number of non-trailing-blank lines.
    # The line index in norm_content corresponds 1:1 to content_lines
    # for non-trailing-blank lines.
    start = match_start_in_norm
    end = start + old_line_count - 1
    return (start, end)


def fuzzy_replace(content: str, old_string: str, new_string: str) -> tuple[str, str] | None:
    """Try to find and replace old_string in content, with normalization fallback.

    Returns (new_content, match_type) where match_type is 'exact' or 'normalized',
    or None if no match found.
    """
    # Layer 1: exact match
    count = content.count(old_string)
    if count == 1:
        return content.replace(old_string, new_string, 1), 'exact'
    if count > 1:
        return None  # ambiguous, don't attempt fuzzy

    # Layer 2: normalized match
    norm_content = normalize(content)
    norm_old = normalize(old_string)
    count = norm_content.count(norm_old)
    if count != 1:
        return None  # not found or ambiguous after normalization

    range_result = _find_normalized_match(content, old_string)
    if range_result is None:
        return None

    start, end = range_result
    content_lines = content.split('\n')
    new_lines = new_string.split('\n')
    content_lines[start:end + 1] = new_lines
    return '\n'.join(content_lines), 'normalized'


def resolve_and_validate_path(path: str) -> Path:
    """Resolve and validate a path against allowed directories."""
    abs_path = Path(path)
    if abs_path.is_absolute():
        for allowed_dir in ALLOWED_DIRS:
            try:
                abs_path.relative_to(allowed_dir)
                if abs_path.is_symlink():
                    abs_path.resolve().relative_to(allowed_dir)
                return abs_path
            except (ValueError, RuntimeError):
                continue
        raise PermissionError(
            f"Path '{path}' is outside the allowed directory: {ALLOWED_DIRS}"
        )

    resolved = (ALLOWED_BASE_DIR / path).resolve()
    try:
        resolved.relative_to(ALLOWED_BASE_DIR)
        if resolved.is_symlink():
            resolved.resolve().relative_to(ALLOWED_BASE_DIR)
        return resolved
    except (ValueError, RuntimeError):
        raise PermissionError(
            f"Path '{path}' is outside the allowed directory: {ALLOWED_BASE_DIR}"
        )


def unified_diff(old: str, new: str, filename: str, context: int = 3) -> str:
    """Generate a unified diff between old and new content."""
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=context,
    )
    result = "".join(diff)
    if len(result) > 3000:
        result = result[:2500] + "\n... (diff truncated)\n"
    return result
