import json
import logging
import os
import threading
import time
from typing import Any, Callable, Generator
from .background_tasks import BG
import anthropic
from dotenv import load_dotenv

from .compact import (
    MAX_CONTEXT_TOKENS,
    llm_compact_messages,
    needs_compaction,
    estimate_messages_tokens,
    reactive_compact,
)
from .tools import (
    ALLOWED_BASE_DIR,
    TOOL_DEFINITIONS,
    _truncate_for_context,
    dispatcher,
    execute_tool,
    register_delegate_tool,
)
from .parallel_executor import execute_tools_parallel
from .task_system import (
    task_manager
)
from .skill_loader import SKILL_LOADER
from .memory import memory_store
from ._constants import client

load_dotenv()
MODEL_ID = os.getenv("MODEL_ID")

SYSTEM_PROMPT = f"""You are a helpful coding assistant at {ALLOWED_BASE_DIR}. You can help users with software engineering tasks.

Core principles:
- COMPLETE every task you start. Never stop mid-work to summarize or explain unless the user asks.
- When you encounter errors, fix them. Do not just report the error and stop.
- Prefer action over exploration. Read only what you need, then start writing code immediately.
- Use the task tool to track progress. Break large work into sub-tasks.
- Batch related tool calls in a single response when possible (e.g., read multiple files at once).
- If a task has multiple steps, complete ALL steps before responding to the user.
- Use load_skill when a task needs specialized instructions before you act.
- For parallel work, use team_spawn to create teammate agents. Use team_send/team_broadcast to coordinate. Use team_shutdown when done.

Skills available:
{SKILL_LOADER.get_descriptions()}

When writing code, always provide complete and correct implementations."""

logger = logging.getLogger("penguin")

# Callback type aliases
ContentCallback = Callable[[str], None]
ToolStartCallback = Callable[[str, dict], None]
ToolResultCallback = Callable[[str, str], None]

MAX_API_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds
KEEP_RECENT_TOOLS = 5
PRESERVE_RESULT_TOOLS = []
TODO = task_manager

usage_stats = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "last_input_tokens": 0,
    "pending_delta": 0,
}

MAX_OUTPUT_TOKENS = 16384
ESCALATED_MAX_TOKENS = 65536  # 64K — escalation when default output limit is insufficient
MAX_RECOVERY_RETRIES = 3


class _RecoveryState:
    """Tracks truncation escalation and reactive compact state across iterations."""
    __slots__ = ("has_escalated", "recovery_count", "has_attempted_reactive_compact")

    def __init__(self) -> None:
        self.has_escalated = False
        self.recovery_count = 0
        self.has_attempted_reactive_compact = False


def _is_prompt_too_long_error(e: anthropic.APIStatusError) -> bool:
    """Check if the API error is specifically about prompt/context being too long."""
    if e.status_code != 400:
        return False
    msg = (e.message or "").lower()
    return "too long" in msg

SUBAGENT_SYSTEM_PROMPT = f"""You are a focused coding sub-agent at {ALLOWED_BASE_DIR}. Complete the given task thoroughly.
When finished, provide a concise summary of:
1. What you did (files read/written/edited, commands run)
2. Key findings or results
3. Any errors encountered

Be thorough in execution but concise in your summary. Do NOT delegate — complete the work yourself."""

# Tools available to subagents (no delegate to prevent nesting)
SUBAGENT_TOOLS = [t for t in TOOL_DEFINITIONS if t["name"] != "delegate"]


def stream_response(
    client: anthropic.Anthropic,
    messages: list[dict[str, Any]],
    system_prompt: str | None = None,
    tools: list[dict] | None = None,
    max_tokens: int = MAX_OUTPUT_TOKENS,
) -> Generator[tuple[str, Any], None, None]:
    """逐 token 流式消费 API 响应，实时 yield 事件。

    事件类型：
      ("text_delta", str)   — 文本增量，逐 token 产出，可用于打字机输出
      ("truncated", bool)   — 是否因 max_tokens 截断
      ("tool_calls", list)  — 完整的工具调用列表（流结束后一次性 yield）
    """
    tool_use_blocks: dict[int, dict[str, Any]] = {}
    was_truncated = False

    with client.messages.stream(
        model=MODEL_ID,
        max_tokens=max_tokens,
        system=system_prompt or SYSTEM_PROMPT,
        messages=messages,
        tools=tools or TOOL_DEFINITIONS,
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    yield ("text_delta", event.delta.text)

                elif event.delta.type == "input_json_delta":
                    idx = event.index
                    if idx in tool_use_blocks and not tool_use_blocks[idx].get("_complete"):
                        tool_use_blocks[idx]["_partial_json"] += (
                            event.delta.partial_json
                        )

            elif event.type == "content_block_start":
                if event.content_block.type == "tool_use":
                    tool_use_blocks[event.index] = {
                        "id": event.content_block.id,
                        "name": event.content_block.name,
                        "_partial_json": "",
                        "_complete": False,
                    }

            elif event.type == "content_block_stop":
                if event.index in tool_use_blocks:
                    block = tool_use_blocks[event.index]
                    block["_complete"] = True
                    raw_json = block["_partial_json"]
                    if raw_json:
                        try:
                            block["input"] = json.loads(raw_json)
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse tool input JSON, attempting repair")
                            block["input"] = _repair_json(raw_json)
                    else:
                        block["input"] = {}

        final_msg = stream.get_final_message()
        if final_msg.stop_reason == "max_tokens":
            was_truncated = True
            logger.warning("Response truncated at max_tokens=%d", MAX_OUTPUT_TOKENS)

    tool_calls_list = []
    for idx in sorted(tool_use_blocks):
        block = tool_use_blocks[idx]
        tool_calls_list.append(
            {
                "id": block["id"],
                "name": block["name"],
                "input": block["input"],
            }
        )

    usage = final_msg.usage
    usage_stats["prompt_tokens"] += usage.input_tokens
    usage_stats["completion_tokens"] += usage.output_tokens

    if was_truncated:
        yield ("truncated", True)
    if tool_calls_list:
        yield ("tool_calls", tool_calls_list)
    yield ("usage", usage.input_tokens)


def _repair_json(raw: str) -> dict[str, Any]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    repaired = raw.strip()
    if not repaired.startswith("{"):
        repaired = "{" + repaired
    if not repaired.endswith("}"):
        repaired += "}"
    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        pass
    for pos in range(len(repaired) - 1, 0, -1):
        if repaired[pos] in (",", ":"):
            try:
                return json.loads(repaired[:pos] + repaired[pos + 1:])
            except json.JSONDecodeError:
                continue
    logger.error("Could not repair JSON, falling back to empty dict: %s", raw[:100])
    return {}


def run_subagent(
    client: anthropic.Anthropic,
    prompt: str,
    max_iterations: int = 20,
) -> str:
    """Run a subagent with a fresh context. Returns a summary string.

    The subagent operates in complete isolation:
    - Fresh messages list (no parent history)
    - No delegate tool (prevents nesting)
    - Own compaction if context grows
    - Only the final text response is returned
    """
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    sub_last_input_tokens = 0
    sub_pending_delta = estimate_messages_tokens(messages)

    for iteration in range(max_iterations):
        if needs_compaction(sub_last_input_tokens, sub_pending_delta):
            messages[:] = llm_compact_messages(
                messages, client, MODEL_ID, max_tokens=MAX_CONTEXT_TOKENS
            )
            sub_last_input_tokens = estimate_messages_tokens(messages)
            sub_pending_delta = 0

        collected_content = ""
        has_tool_calls = False
        was_truncated = False
        tool_calls_list = []

        for retry in range(MAX_API_RETRIES):
            try:
                for event_type, data in stream_response(
                    client, messages,
                    system_prompt=SUBAGENT_SYSTEM_PROMPT,
                    tools=SUBAGENT_TOOLS,
                ):
                    if event_type == "text_delta":
                        collected_content += data
                    elif event_type == "truncated":
                        was_truncated = True
                    elif event_type == "tool_calls":
                        has_tool_calls = True
                        tool_calls_list = data
                    elif event_type == "usage":
                        sub_last_input_tokens = data
                        sub_pending_delta = 0
                break
            except anthropic.APIStatusError as e:
                if e.status_code in (429, 503, 529) and retry < MAX_API_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** retry))
                    continue
                return f"[Subagent error] API status {e.status_code}: {e.message}"
            except anthropic.APIConnectionError as e:
                if retry < MAX_API_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** retry))
                    continue
                return f"[Subagent error] Connection failed: {e}"

        assistant_content: list[dict[str, Any]] = []
        if collected_content:
            assistant_content.append({"type": "text", "text": collected_content})
        for tc in tool_calls_list:
            assistant_content.append({
                "type": "tool_use",
                "id": tc["id"],
                "name": tc["name"],
                "input": tc["input"],
            })
        assistant_msg = {"role": "assistant", "content": assistant_content}
        messages.append(assistant_msg)
        sub_pending_delta += estimate_messages_tokens([assistant_msg])

        if was_truncated:
            trunc_msg = {
                "role": "user",
                "content": "[System: Response truncated. Continue from where you left off.]"
            }
            messages.append(trunc_msg)
            sub_pending_delta += estimate_messages_tokens([trunc_msg])
            continue

        if not has_tool_calls:
            return collected_content or "(subagent completed with no output)"

        # Execute tools
        tool_results = execute_tools_parallel(
            tool_calls_list=tool_calls_list,
            dispatch_fn=lambda name, args: execute_tool(name, args, skip_permission_check=True),
        )
        user_msg = {"role": "user", "content": tool_results}
        messages.append(user_msg)
        sub_pending_delta += estimate_messages_tokens([user_msg])

    partial = collected_content[:500]
    return (
        f"[Subagent hit iteration limit ({max_iterations}). "
        f"Partial result: {partial}]"
    )


def run_subagent_with_tools(
    client: anthropic.Anthropic,
    prompt: str,
    max_iterations: int = 20,
    tools: list[dict] | None = None,
    system_prompt: str | None = None,
    tool_dispatcher=None,
) -> str:
    """Run a subagent with explicit tools/prompt/dispatcher (used by Agent class)."""
    _tools = tools or SUBAGENT_TOOLS
    _system_prompt = system_prompt or SUBAGENT_SYSTEM_PROMPT
    _dispatcher = tool_dispatcher or dispatcher

    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    sub_last_input_tokens = 0
    sub_pending_delta = estimate_messages_tokens(messages)

    for iteration in range(max_iterations):
        if needs_compaction(sub_last_input_tokens, sub_pending_delta):
            messages[:] = llm_compact_messages(
                messages, client, MODEL_ID, max_tokens=MAX_CONTEXT_TOKENS
            )
            sub_last_input_tokens = estimate_messages_tokens(messages)
            sub_pending_delta = 0

        collected_content = ""
        has_tool_calls = False
        was_truncated = False
        tool_calls_list = []

        for retry in range(MAX_API_RETRIES):
            try:
                for event_type, data in stream_response(
                    client, messages,
                    system_prompt=_system_prompt,
                    tools=_tools,
                ):
                    if event_type == "text_delta":
                        collected_content += data
                    elif event_type == "truncated":
                        was_truncated = True
                    elif event_type == "tool_calls":
                        has_tool_calls = True
                        tool_calls_list = data
                    elif event_type == "usage":
                        sub_last_input_tokens = data
                        sub_pending_delta = 0
                break
            except anthropic.APIStatusError as e:
                if e.status_code in (429, 503, 529) and retry < MAX_API_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** retry))
                    continue
                return f"[Subagent error] API status {e.status_code}: {e.message}"
            except anthropic.APIConnectionError as e:
                if retry < MAX_API_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** retry))
                    continue
                return f"[Subagent error] Connection failed: {e}"

        assistant_content: list[dict[str, Any]] = []
        if collected_content:
            assistant_content.append({"type": "text", "text": collected_content})
        for tc in tool_calls_list:
            assistant_content.append({
                "type": "tool_use",
                "id": tc["id"],
                "name": tc["name"],
                "input": tc["input"],
            })
        assistant_msg = {"role": "assistant", "content": assistant_content}
        messages.append(assistant_msg)
        sub_pending_delta += estimate_messages_tokens([assistant_msg])

        if was_truncated:
            trunc_msg = {
                "role": "user",
                "content": "[System: Response truncated. Continue from where you left off.]"
            }
            messages.append(trunc_msg)
            sub_pending_delta += estimate_messages_tokens([trunc_msg])
            continue

        if not has_tool_calls:
            return collected_content or "(subagent completed with no output)"

        tool_results = execute_tools_parallel(
            tool_calls_list=tool_calls_list,
            dispatch_fn=lambda name, args: _dispatcher.dispatch(name, args, skip_permission_check=True),
        )
        user_msg = {"role": "user", "content": tool_results}
        messages.append(user_msg)
        sub_pending_delta += estimate_messages_tokens([user_msg])

    partial = collected_content[:500]
    return (
        f"[Subagent hit iteration limit ({max_iterations}). "
        f"Partial result: {partial}]"
    )


# Re-export for backward compatibility — cli.py imports this from agent_loop
__all__ = ["register_delegate_tool"]


def agent_loop(
    client: anthropic.Anthropic,
    user_message: str,
    max_iterations: int = 100,
    on_content: ContentCallback | None = None,
    on_tool_start: ToolStartCallback | None = None,
    on_tool_result: ToolResultCallback | None = None,
    confirm_callback: Callable[[str, dict, str], bool] | None = None,
    messages: list[dict[str, Any]] | None = None,
    rounds_since_todo: int = 0,
    tools: list[dict] | None = None,
    system_prompt: str | None = None,
    tool_dispatcher=None,
    parallel_enabled: bool = True,
    parallel_max_workers: int = 4,
) -> tuple[str, list[dict[str, Any]]]:
    if messages is None:
        messages = []

    # Use provided dispatcher or fall back to global
    _dispatcher = tool_dispatcher or dispatcher
    _tools = tools or TOOL_DEFINITIONS
    _system_prompt = system_prompt or SYSTEM_PROMPT
    _dispatcher.set_confirm_callback(confirm_callback)
    user_msg = {"role": "user", "content": user_message}
    messages.append(user_msg)
    usage_stats["pending_delta"] += estimate_messages_tokens([user_msg])

    recovery_state = _RecoveryState()
    current_max_tokens = MAX_OUTPUT_TOKENS

    for iteration in range(max_iterations):
        if needs_compaction(
            usage_stats["last_input_tokens"], usage_stats["pending_delta"]
        ):
            messages[:] = llm_compact_messages(
                messages, client, MODEL_ID, max_tokens=MAX_CONTEXT_TOKENS
            )
            usage_stats["last_input_tokens"] = estimate_messages_tokens(messages)
            usage_stats["pending_delta"] = 0

        remaining = max_iterations - iteration
        iteration_system = (
            f"[System: Iteration {iteration + 1}/{max_iterations}. "
            f"You have {remaining} iterations remaining. "
            f"{'Keep working — do not stop until the task is complete.' if remaining <= 5 else ''}]"
        )

        # ── Memory hook 1: inject relevant memories into system prompt ──
        # Do this BEFORE the LLM call so the model can use memories for its decision
        memory_context = memory_store.build_iteration_context(messages)
        if memory_context:
            _iter_system_prompt = _system_prompt + f"\n\n<active_memories>\n{memory_context}\n</active_memories>"
        else:
            _iter_system_prompt = _system_prompt

        # Inner loop: truncation escalation / reactive-compact recovery
        while True:
            collected_content = ""
            has_tool_calls = False
            was_truncated = False
            tool_calls_list = []
            prompt_too_long = False

            for retry in range(MAX_API_RETRIES):
                try:
                    for event_type, data in stream_response(
                        client, messages,
                        system_prompt=_iter_system_prompt, tools=_tools,
                        max_tokens=current_max_tokens,
                    ):
                        if event_type == "text_delta":
                            collected_content += data
                            if on_content:
                                on_content(data)
                        elif event_type == "truncated":
                            was_truncated = True
                        elif event_type == "tool_calls":
                            has_tool_calls = True
                            tool_calls_list = data
                        elif event_type == "usage":
                            usage_stats["last_input_tokens"] = data
                            usage_stats["pending_delta"] = 0
                    break
                except anthropic.APIStatusError as e:
                    # Path 2: context too long — reactive compact
                    if _is_prompt_too_long_error(e):
                        if not recovery_state.has_attempted_reactive_compact:
                            logger.warning("Prompt too long, triggering reactive compact")
                            messages[:] = reactive_compact(messages)
                            recovery_state.has_attempted_reactive_compact = True
                            prompt_too_long = True
                            break
                        logger.error("Context too long even after reactive compact")
                        return "Context too long even after reactive compact.", messages
                    if e.status_code in (429, 503, 529) and retry < MAX_API_RETRIES - 1:
                        delay = RETRY_BASE_DELAY * (2 ** retry)
                        logger.warning("API rate limit/error (status %d), retrying in %.1fs", e.status_code, delay)
                        time.sleep(delay)
                        continue
                    error_msg = f"API error (status {e.status_code}): {e.message}"
                    logger.error(error_msg)
                    return error_msg, messages
                except anthropic.APIConnectionError as e:
                    if retry < MAX_API_RETRIES - 1:
                        delay = RETRY_BASE_DELAY * (2 ** retry)
                        logger.warning("API connection error, retrying in %.1fs", delay)
                        time.sleep(delay)
                        continue
                    error_msg = f"API connection error after retries: {e}"
                    logger.error(error_msg)
                    return error_msg, messages

            if prompt_too_long:
                continue  # retry after reactive compact

            # Path 1: output truncated — escalate or continuation
            if was_truncated:
                if not recovery_state.has_escalated:
                    current_max_tokens = ESCALATED_MAX_TOKENS
                    recovery_state.has_escalated = True
                    logger.warning(
                        "Response truncated at %d tokens, escalating to %d",
                        MAX_OUTPUT_TOKENS, ESCALATED_MAX_TOKENS,
                    )
                    continue  # messages unchanged, retry same request with more tokens

                # Already escalated: append truncated output + continuation prompt
                assistant_content: list[dict[str, Any]] = []
                if collected_content:
                    assistant_content.append({"type": "text", "text": collected_content})
                for tc in tool_calls_list:
                    assistant_content.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "input": tc["input"],
                    })
                messages.append({"role": "assistant", "content": assistant_content})

                if recovery_state.recovery_count < MAX_RECOVERY_RETRIES:
                    cont_msg = {
                        "role": "user",
                        "content": (
                            "Output token limit hit. Resume directly — "
                            "no apology, no recap. Pick up mid-thought."
                        ),
                    }
                    messages.append(cont_msg)
                    recovery_state.recovery_count += 1
                    logger.warning(
                        "Still truncated at %d tokens, continuation %d/%d",
                        ESCALATED_MAX_TOKENS,
                        recovery_state.recovery_count, MAX_RECOVERY_RETRIES,
                    )
                    continue  # retry with continuation

                # Max continuations exceeded
                logger.error(
                    "Still truncated after %d continuations, giving up",
                    MAX_RECOVERY_RETRIES,
                )
                return collected_content, messages

            break  # success — not truncated, exit inner loop

        # Normal: append complete assistant message
        assistant_content: list[dict[str, Any]] = []
        if collected_content:
            assistant_content.append({"type": "text", "text": collected_content})
        for tc in tool_calls_list:
            assistant_content.append(
                {
                    "type": "tool_use",
                    "id": tc["id"],
                    "name": tc["name"],
                    "input": tc["input"],
                }
            )

        assistant_msg = {"role": "assistant", "content": assistant_content}
        messages.append(assistant_msg)
        usage_stats["pending_delta"] += estimate_messages_tokens([assistant_msg])

        if not has_tool_calls:
            return collected_content, messages

        tool_results: list[dict[str, Any]] = []

        # Inject iteration awareness so the model can plan its work
        tool_results.append(
            {
                "type": "text",
                "text": iteration_system,
            }
        )

        tool_results.extend(
            execute_tools_parallel(
                tool_calls_list=tool_calls_list,
                dispatch_fn=lambda name, args: _dispatcher.dispatch(name, args),
                on_tool_start=on_tool_start,
                on_tool_result=on_tool_result,
                max_workers=parallel_max_workers,
                enabled=parallel_enabled,
            )
        )

        # Inject background task completions into this iteration's context
        bg_notifs = BG.drain_notifications()
        if bg_notifs:
            notif_lines = []
            for n in bg_notifs:
                notif_lines.append(f"[bg:{n['task_id']}] {n['status']}: {n['result']}")
            tool_results.append({
                "type": "text",
                "text": f"<background-results>\n" + "\n".join(notif_lines) + "\n</background-results>",
            })
        if rounds_since_todo >= 3:
            current_tasks = task_manager.list_all()
            reminder = f"\n\n<reminder>Update your task list. Current tasks:\n{current_tasks}</reminder>"
            tool_results.append(
                {
                    "type": "text",
                    "text": reminder,
                }
            )
        user_msg = {"role": "user", "content": tool_results}
        messages.append(user_msg)
        usage_stats["pending_delta"] += estimate_messages_tokens([user_msg])

        # ── Memory hook 2: extract memories from this turn (async) ──
        if iteration > 0:
            try:
                _last_assistant = None
                _last_user = None
                for m in reversed(messages):
                    if m.get("role") == "assistant" and _last_assistant is None:
                        _last_assistant = m
                    elif m.get("role") == "user" and _last_user is None:
                        _last_user = m
                    if _last_assistant and _last_user:
                        break
                if _last_assistant and _last_user:
                    _la, _lu = _last_assistant, _last_user
                    def _extract_worker():
                        try:
                            memory_store.extract_from_turn(_lu, _la, client, MODEL_ID)
                        except Exception:
                            logger.warning("Async memory extraction failed (non-critical)")
                    threading.Thread(target=_extract_worker, daemon=True).start()
            except Exception:
                pass

        # ── Memory hook 3: threshold check → consolidate ──
        if memory_store.count() > memory_store.CONSOLIDATE_THRESHOLD:
            def _consolidate_worker():
                try:
                    memory_store.consolidate(client, MODEL_ID)
                except Exception:
                    logger.warning("Async memory consolidation failed (non-critical)")
            threading.Thread(target=_consolidate_worker, daemon=True).start()

    return "Agent reached maximum iterations without completing the task.", messages
