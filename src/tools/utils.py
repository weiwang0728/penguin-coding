"""Shared utilities for tool implementations."""

import difflib
from pathlib import Path

from .._constants import ALLOWED_BASE_DIR
from ..skill_loader import SKILLS_DIR

ALLOWED_DIRS = [ALLOWED_BASE_DIR, SKILLS_DIR]

_changed_files: set[str] = set()


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
