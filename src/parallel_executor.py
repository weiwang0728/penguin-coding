"""Parallel execution engine for independent tool calls."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable

logger = logging.getLogger("penguin")

# ── Configuration ──

PARALLEL_TOOLS_ENABLED = os.getenv("PENGUIN_PARALLEL_TOOLS", "1") == "1"
PARALLEL_MAX_WORKERS = int(os.getenv("PENGUIN_PARALLEL_WORKERS", "4"))

# ── Tool categories ──

READ_ONLY_TOOLS = frozenset({
    "read_file", "list_directory", "search_files",
    "check_background", "team_list", "load_skill",
})

WRITE_TOOLS = frozenset({
    "write_file", "edit_file", "run_command", "background_run",
})

STATEFUL_TOOLS = frozenset({
    "task", "team_spawn", "team_send", "team_broadcast",
    "team_shutdown", "delegate",
})

SEQUENTIAL_TOOLS = WRITE_TOOLS | STATEFUL_TOOLS


@dataclass
class ToolCall:
    index: int
    id: str
    name: str
    input: dict[str, Any]


def _group_tool_calls(tool_calls: list[dict]) -> list[list[ToolCall]]:
    """Partition tool calls into ordered execution groups.

    Consecutive READ-ONLY tools form a parallel group.
    Each SEQUENTIAL tool forms its own single-item group.
    Unknown tools default to sequential (safe).
    """
    groups: list[list[ToolCall]] = []
    current_parallel: list[ToolCall] = []

    for i, tc in enumerate(tool_calls):
        call = ToolCall(index=i, id=tc["id"], name=tc["name"], input=tc["input"])

        if call.name in READ_ONLY_TOOLS:
            current_parallel.append(call)
        else:
            if current_parallel:
                groups.append(current_parallel)
                current_parallel = []
            groups.append([call])

    if current_parallel:
        groups.append(current_parallel)

    return groups


def execute_tools_parallel(
    tool_calls_list: list[dict],
    dispatch_fn: Callable[[str, dict], str],
    on_tool_start: Callable[[str, dict], None] | None = None,
    on_tool_result: Callable[[str, str], None] | None = None,
    max_workers: int = PARALLEL_MAX_WORKERS,
    enabled: bool = PARALLEL_TOOLS_ENABLED,
) -> list[dict[str, Any]]:
    """Execute a batch of tool calls, parallelizing READ-ONLY tools.

    Returns tool_result dicts in the same order as tool_calls_list.
    """
    if not enabled or len(tool_calls_list) <= 1:
        return _execute_sequential(tool_calls_list, dispatch_fn, on_tool_start, on_tool_result)

    read_only_count = sum(1 for tc in tool_calls_list if tc["name"] in READ_ONLY_TOOLS)
    if read_only_count <= 1:
        return _execute_sequential(tool_calls_list, dispatch_fn, on_tool_start, on_tool_result)

    groups = _group_tool_calls(tool_calls_list)
    results: dict[int, str] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for group in groups:
            is_parallel_group = len(group) > 1 and all(
                tc.name in READ_ONLY_TOOLS for tc in group
            )

            if is_parallel_group:
                _execute_parallel_group(group, executor, dispatch_fn,
                                        on_tool_start, on_tool_result, results)
            else:
                _execute_sequential_group(group, dispatch_fn,
                                          on_tool_start, on_tool_result, results)

    tool_results = []
    for i in range(len(tool_calls_list)):
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_calls_list[i]["id"],
            "content": results[i],
        })

    return tool_results


def _execute_sequential(
    tool_calls_list: list[dict],
    dispatch_fn: Callable[[str, dict], str],
    on_tool_start: Callable[[str, dict], None] | None,
    on_tool_result: Callable[[str, str], None] | None,
) -> list[dict[str, Any]]:
    """Fallback sequential execution (original behavior)."""
    from ._constants import _truncate_for_context

    tool_results = []
    for tc in tool_calls_list:
        fn_name, fn_args = tc["name"], tc["input"]
        if on_tool_start:
            on_tool_start(fn_name, fn_args)
        try:
            result = dispatch_fn(fn_name, fn_args)
        except Exception as e:
            result = f"Error: {e}"
            logger.exception("Tool %s failed", fn_name)
        if on_tool_result:
            on_tool_result(fn_name, result)
        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tc["id"],
            "content": _truncate_for_context(result),
        })
    return tool_results


def _execute_parallel_group(
    group: list[ToolCall],
    executor: ThreadPoolExecutor,
    dispatch_fn: Callable[[str, dict], str],
    on_tool_start: Callable[[str, dict], None] | None,
    on_tool_result: Callable[[str, str], None] | None,
    results: dict[int, str],
) -> None:
    """Execute a group of READ-ONLY tools in parallel."""
    from ._constants import _truncate_for_context

    # Fire start callbacks in order before submitting
    for tc in group:
        if on_tool_start:
            on_tool_start(tc.name, tc.input)

    # Submit all to executor
    futures = {}
    for tc in group:
        future = executor.submit(dispatch_fn, tc.name, tc.input)
        futures[future] = tc

    # Collect results as they complete
    buffered_callbacks: list[tuple[int, str, str]] = []

    for future in as_completed(futures):
        tc = futures[future]
        try:
            result = future.result()
        except Exception as e:
            result = f"Error: {e}"
            logger.exception("Parallel tool %s failed", tc.name)

        results[tc.index] = _truncate_for_context(result)
        if on_tool_result:
            buffered_callbacks.append((tc.index, tc.name, result))

    # Fire result callbacks in original order
    buffered_callbacks.sort(key=lambda x: x[0])
    for _idx, name, result in buffered_callbacks:
        on_tool_result(name, result)


def _execute_sequential_group(
    group: list[ToolCall],
    dispatch_fn: Callable[[str, dict], str],
    on_tool_start: Callable[[str, dict], None] | None,
    on_tool_result: Callable[[str, str], None] | None,
    results: dict[int, str],
) -> None:
    """Execute a single sequential tool."""
    from ._constants import _truncate_for_context

    for tc in group:
        if on_tool_start:
            on_tool_start(tc.name, tc.input)
        try:
            result = dispatch_fn(tc.name, tc.input)
        except Exception as e:
            result = f"Error: {e}"
            logger.exception("Tool %s failed", tc.name)
        if on_tool_result:
            on_tool_result(tc.name, result)
        results[tc.index] = _truncate_for_context(result)
