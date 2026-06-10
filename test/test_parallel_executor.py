"""Tests for parallel tool execution engine."""

import threading
import time
from unittest.mock import MagicMock

import pytest

from src.parallel_executor import (
    READ_ONLY_TOOLS,
    SEQUENTIAL_TOOLS,
    ToolCall,
    _group_tool_calls,
    execute_tools_parallel,
)
from src.tools.utils import _ThreadSafeSet


# ── _group_tool_calls tests ──


def _make_tc(index: int, name: str) -> dict:
    return {"id": f"tc_{index}", "name": name, "input": {}}


class TestGroupToolCalls:
    def test_all_read_only(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "list_directory"), _make_tc(2, "search_files")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 1
        assert len(groups[0]) == 3
        assert all(tc.name in READ_ONLY_TOOLS for tc in groups[0])

    def test_all_sequential(self):
        calls = [_make_tc(0, "write_file"), _make_tc(1, "edit_file")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 2
        assert all(len(g) == 1 for g in groups)

    def test_reads_then_write(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "list_directory"), _make_tc(2, "write_file")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 2
        assert len(groups[0]) == 2  # parallel group
        assert groups[1][0].name == "write_file"

    def test_write_then_reads(self):
        calls = [_make_tc(0, "write_file"), _make_tc(1, "read_file"), _make_tc(2, "list_directory")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 2
        assert groups[0][0].name == "write_file"
        assert len(groups[1]) == 2

    def test_alternating(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "write_file"), _make_tc(2, "list_directory"), _make_tc(3, "edit_file")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 4
        assert [len(g) for g in groups] == [1, 1, 1, 1]

    def test_stateful_in_middle(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "task"), _make_tc(2, "read_file")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 3
        assert groups[0][0].name == "read_file"
        assert groups[1][0].name == "task"
        assert groups[2][0].name == "read_file"

    def test_empty(self):
        assert _group_tool_calls([]) == []

    def test_single_read(self):
        groups = _group_tool_calls([_make_tc(0, "read_file")])
        assert len(groups) == 1
        assert len(groups[0]) == 1

    def test_single_write(self):
        groups = _group_tool_calls([_make_tc(0, "write_file")])
        assert len(groups) == 1
        assert len(groups[0]) == 1

    def test_delegate_is_sequential(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "delegate"), _make_tc(2, "read_file")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 3

    def test_unknown_tool_defaults_sequential(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "unknown_tool"), _make_tc(2, "read_file")]
        groups = _group_tool_calls(calls)
        assert len(groups) == 3
        assert groups[1][0].name == "unknown_tool"

    def test_indices_preserved(self):
        calls = [_make_tc(0, "read_file"), _make_tc(1, "write_file"), _make_tc(2, "list_directory")]
        groups = _group_tool_calls(calls)
        all_indices = [tc.index for g in groups for tc in g]
        assert all_indices == [0, 1, 2]


# ── execute_tools_parallel tests ──


class TestExecuteToolsParallel:
    def test_result_ordering(self):
        """Results must be in the same order as tool_calls_list."""
        call_order = []

        def dispatch(name, args):
            # Simulate different execution times
            if name == "slow_read":
                time.sleep(0.1)
            call_order.append(name)
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "slow_read" if "slow_read" in READ_ONLY_TOOLS else "read_file", "input": {}},
            {"id": "1", "name": "read_file", "input": {}},
            {"id": "2", "name": "list_directory", "input": {}},
        ]
        # Override name for the first call to simulate a slow read
        calls[0]["name"] = "read_file"

        # Use a slow dispatch for index 0
        results_by_index = {}

        def indexed_dispatch(name, args):
            # We need a way to make the first call slow
            time.sleep(0.1)
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "read_file", "input": {}},
            {"id": "1", "name": "read_file", "input": {}},
            {"id": "2", "name": "list_directory", "input": {}},
        ]

        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=lambda name, args: f"result_{name}",
        )

        # Results must be in original order
        assert len(results) == 3
        for i, r in enumerate(results):
            assert r["tool_use_id"] == str(i)

    def test_sequential_fallback_when_disabled(self):
        calls = [
            {"id": "0", "name": "read_file", "input": {}},
            {"id": "1", "name": "read_file", "input": {}},
        ]
        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=lambda name, args: f"result_{name}",
            enabled=False,
        )
        assert len(results) == 2

    def test_sequential_fallback_single_tool(self):
        calls = [{"id": "0", "name": "read_file", "input": {}}]
        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=lambda name, args: f"result_{name}",
            enabled=True,
        )
        assert len(results) == 1

    def test_sequential_fallback_no_parallelizable_tools(self):
        calls = [
            {"id": "0", "name": "write_file", "input": {}},
            {"id": "1", "name": "edit_file", "input": {}},
        ]
        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=lambda name, args: f"result_{name}",
            enabled=True,
        )
        assert len(results) == 2

    def test_parallel_execution_is_faster(self):
        """Two slow read-only tools should execute in parallel, not sequentially."""
        execution_times = []

        def slow_dispatch(name, args):
            start = time.time()
            time.sleep(0.2)
            execution_times.append(time.time() - start)
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "read_file", "input": {}},
            {"id": "1", "name": "list_directory", "input": {}},
        ]

        start = time.time()
        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=slow_dispatch,
            enabled=True,
        )
        elapsed = time.time() - start

        # Parallel execution should be < 0.5s (not 0.4s+ like sequential)
        assert elapsed < 0.45, f"Parallel execution took {elapsed:.2f}s, expected < 0.45s"
        assert len(results) == 2

    def test_write_waits_for_reads(self):
        """Write tool must not start until all preceding reads finish."""
        log = []
        barrier = threading.Event()

        def dispatch(name, args):
            log.append(f"start:{name}")
            if name == "read_file":
                time.sleep(0.1)
            log.append(f"end:{name}")
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "read_file", "input": {}},
            {"id": "1", "name": "write_file", "input": {}},
        ]

        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=dispatch,
            enabled=True,
        )

        # write_file must start after read_file ends
        read_end_idx = log.index("end:read_file")
        write_start_idx = log.index("start:write_file")
        assert write_start_idx > read_end_idx, f"Write started before read finished: {log}"

    def test_error_does_not_affect_other_tools(self):
        """A tool error should not prevent other tools from completing."""
        call_count = 0

        def dispatch(name, args):
            nonlocal call_count
            call_count += 1
            if name == "read_file" and args.get("fail"):
                raise RuntimeError("intentional failure")
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "read_file", "input": {"fail": True}},
            {"id": "1", "name": "list_directory", "input": {}},
        ]

        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=dispatch,
            enabled=True,
        )

        assert len(results) == 2
        assert "Error" in results[0]["content"]
        assert "result_list_directory" in results[1]["content"]

    def test_callbacks_fire_in_order(self):
        """on_tool_start fires in order; on_tool_result fires in order."""
        starts = []
        results_cb = []

        def dispatch(name, args):
            if name == "list_directory":
                time.sleep(0.05)
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "read_file", "input": {}},
            {"id": "1", "name": "list_directory", "input": {}},
        ]

        execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=dispatch,
            on_tool_start=lambda name, args: starts.append(name),
            on_tool_result=lambda name, result: results_cb.append(name),
            enabled=True,
        )

        assert starts == ["read_file", "list_directory"]
        assert results_cb == ["read_file", "list_directory"]

    def test_mixed_parallel_and_sequential(self):
        """Full mixed scenario: reads, write, reads, task."""
        execution_log = []

        def dispatch(name, args):
            execution_log.append(name)
            return f"result_{name}"

        calls = [
            {"id": "0", "name": "read_file", "input": {}},
            {"id": "1", "name": "list_directory", "input": {}},
            {"id": "2", "name": "write_file", "input": {}},
            {"id": "3", "name": "search_files", "input": {}},
            {"id": "4", "name": "task", "input": {}},
        ]

        results = execute_tools_parallel(
            tool_calls_list=calls,
            dispatch_fn=dispatch,
            enabled=True,
        )

        assert len(results) == 5
        # All results present in correct order
        for i, r in enumerate(results):
            assert r["tool_use_id"] == str(i)


# ── _ThreadSafeSet tests ──


class TestThreadSafeSet:
    def test_basic_add_and_contains(self):
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
