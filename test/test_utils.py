"""Tests for tools/utils.py — fuzzy_replace, resolve_and_validate_path, unified_diff, _ThreadSafeSet."""

import threading
import time

import pytest

from src.tools.utils import (
    _ThreadSafeSet,
    fuzzy_replace,
    normalize,
    resolve_and_validate_path,
    unified_diff,
)
from src._constants import ALLOWED_BASE_DIR

from src.skill_loader import SKILLS_DIR


# ═══════════════════════════════════════════════════════════════
# fuzzy_replace
# ═══════════════════════════════════════════════════════════════


class TestFuzzyReplace:
    def test_exact_match(self):
        result = fuzzy_replace("hello world", "world", "earth")
        assert result is not None
        new_content, match_type = result
        assert new_content == "hello earth"
        assert match_type == "exact"

    def test_multiple_exact_match_returns_none(self):
        result = fuzzy_replace("aaa\naaa\nbbb", "aaa", "ccc")
        assert result is None  # ambiguous

    def test_normalized_match(self):
        # Content has trailing whitespace but old_string doesn't —
        # after normalization, the match succeeds
        content = "line one\nline two  \nline three"
        result = fuzzy_replace(content, "line two", "LINE TWO")
        assert result is not None
        new_content, match_type = result
        assert "LINE TWO" in new_content
        # If content has trailing spaces but old_string doesn't, it may match exactly
        # or via normalization depending on whitespace arrangement
        assert match_type in ("exact", "normalized")

    def test_no_match(self):
        result = fuzzy_replace("hello world", "not found", "replacement")
        assert result is None

    def test_normalized_multiple_match_returns_none(self):
        content = "aaa  \naaa  \nbbb"
        result = fuzzy_replace(content, "aaa", "ccc")
        assert result is None  # still ambiguous after normalization


class TestNormalize:
    def test_trailing_whitespace_stripped(self):
        assert normalize("hello   \nworld  ") == "hello\nworld"

    def test_trailing_blank_lines_removed(self):
        assert normalize("hello\n\n\n") == "hello"

    def test_no_trailing_whitespace(self):
        assert normalize("hello\nworld") == "hello\nworld"


class TestUnifiedDiff:
    def test_short_diff(self):
        old = "line one\nline two\nline three"
        new = "line one\nLINE TWO\nline three"
        diff = unified_diff(old, new, "test.txt")
        assert "-line two" in diff
        assert "+LINE TWO" in diff

    def test_no_diff(self):
        content = "same content"
        diff = unified_diff(content, content, "same.txt")
        assert diff == ""

    def test_long_diff_truncated(self):
        old = "\n".join(f"old line {i}" for i in range(500))
        new = "\n".join(f"new line {i}" for i in range(500))
        diff = unified_diff(old, new, "big.txt")
        assert len(diff) <= 3000


class TestThreadSafeSet:
    def test_add_and_contains(self):
        s = _ThreadSafeSet()
        s.add("a")
        s.add("b")
        assert "a" in s
        assert "b" in s
        assert "c" not in s

    def test_bool_and_len(self):
        s = _ThreadSafeSet()
        assert not s
        s.add("a")
        assert s
        assert len(s) == 1

    def test_clear(self):
        s = _ThreadSafeSet()
        s.add("a")
        s.clear()
        assert not s
        assert len(s) == 0

    def test_sorted_items(self):
        s = _ThreadSafeSet()
        s.add("c")
        s.add("a")
        s.add("b")
        assert s.sorted_items() == ["a", "b", "c"]

    def test_concurrent_adds(self):
        s = _ThreadSafeSet()
        n = 1000

        def add_items(start):
            for i in range(start, start + n):
                s.add(str(i))

        threads = [threading.Thread(target=add_items, args=(i * n,)) for i in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(s) == n * 4

    def test_concurrent_add_and_clear(self):
        s = _ThreadSafeSet()
        errors = []

        def adder():
            try:
                for i in range(500):
                    s.add(str(i))
            except Exception as e:
                errors.append(e)

        def clearer():
            try:
                for _ in range(50):
                    s.clear()
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=adder), threading.Thread(target=clearer)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f"Concurrent add/clear errors: {errors}"


class TestResolveAndValidatePath:
    def test_normal_relative_path(self):
        result = resolve_and_validate_path("test/sort.py")
        assert result == ALLOWED_BASE_DIR / "test" / "sort.py"

    def test_dot_path(self):
        result = resolve_and_validate_path(".")
        assert result == ALLOWED_BASE_DIR

    def test_path_traversal_blocked(self):
        with pytest.raises(PermissionError, match="outside the allowed directory"):
            resolve_and_validate_path("../../../etc/passwd")

    def test_absolute_path_outside_blocked(self):
        with pytest.raises(PermissionError, match="outside the allowed directory"):
            resolve_and_validate_path("/etc/passwd")

    def test_empty_path(self):
        result = resolve_and_validate_path("")
        assert result == ALLOWED_BASE_DIR

    def test_absolute_in_skills_dir(self):
        result = resolve_and_validate_path(str(SKILLS_DIR))
        assert result == SKILLS_DIR
