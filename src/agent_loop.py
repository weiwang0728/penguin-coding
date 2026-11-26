import json
import logging
import os
import time
import uuid
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable, Generator
from .background_tasks import BG
import anthropic
from dotenv import load_dotenv

from .compact import (
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
from .observability import bind_context, observation, record_response, run_context
from .parallel_executor import execute_tools_parallel
from .task_system import (
    task_manager
)
from .skill_loader import SKILL_LOADER
from ._constants import client

load_dotenv()
MODEL_ID = os.getenv("MODEL_ID")

SYSTEM_PROMPT = """You are a helpful coding assistant at {base_dir}. You can help users with software engineering tasks.

Core principles:
- COMPLETE every task you start. Never stop mid-work to summarize or explain unless the user asks.
- When you encounter errors, fix them. Do not just report the error and stop.
- Prefer action over exploration. Read only what you need, then start writing code immediately.
- Use the task tool to track progress. Break large work into sub-tasks.
- Batch related tool calls in a single response when possible (e.g., read multiple files at once).
- If a task has multiple steps, complete ALL steps before responding to the user.
- For parallel work, use team_spawn to create teammate agents. Use team_send/team_broadcast to coordinate. Use team_shutdown when done.

When writing code, always provide complete and correct implementations.""".format(base_dir=ALLOWED_BASE_DIR)


def _build_default_system_prompt(include_skills: bool) -> str:
    """Base prompt, with the active-skills block appended only when requested.

    Skills are read at call time (not import time) so newly activated skills
    are reflected. Skill content itself always flows through the load_skill
    tool result, never through the system prompt.
    """
    if not include_skills:
        return SYSTEM_PROMPT
    skill_descs = SKILL_LOADER.get_descriptions()
    if not SKILL_LOADER.active_skills:
        return SYSTEM_PROMPT
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Skills available:\n{skill_descs}\n\n"
        f"Use load_skill when a task needs specialized instructions before you act."
    )

logger = logging.getLogger("penguin")

# Callback type aliases
ContentCallback = Callable[[str], None]
ToolStartCallback = Callable[[str, dict], None]
ToolResultCallback = Callable[[str, str], None]

MAX_API_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds
BUDGET_FINALIZE_RATIO = 0.85  # at >85% budget used, instruct the model to converge
KEEP_RECENT_TOOLS = 5
PRESERVE_RESULT_TOOLS = []
TODO = task_manager


def _budget_hint(remaining: int, max_iterations: int) -> str:
    """Iteration-prompt suffix for budget awareness.

    Turns "budget exhausted" from a hard cut-off into an explicit converge-now
    instruction, so the exported patch is a deliberate final state rather than
    whatever was in flight when the wall came down.
    """
    if remaining <= 5:
        return ("Budget exhausted: stop exploring. Verify once if needed, then "
                "call exit_loop now — current working-tree changes are exported "
                "as the final patch.")
    if remaining <= max_iterations * (1 - BUDGET_FINALIZE_RATIO):
        return (f"Budget nearly exhausted (~{remaining} iterations left): stop "
                f"starting new investigation. Finalize your current best fix, "
                f"run your verification once, and call exit_loop.")
    return "Keep working — do not stop until the task is complete."

usage_stats = {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "last_input_tokens": 0,
    "pending_delta": 0,
}

MAX_OUTPUT_TOKENS = 16384
# 64K default. Some providers cap max_tokens lower (e.g. kimi-k2.7-code: 32768); override via env.
ESCALATED_MAX_TOKENS = int(os.getenv("ESCALATED_MAX_TOKENS", "65536"))  # 64K — escalation when default output limit is insufficient
MAX_RECOVERY_RETRIES = 3


# Per-invocation state: concurrent and nested agents must not share exit status.
_active_run: ContextVar[dict | None] = ContextVar("penguin_active_run", default=None)


def _set_run_status(status: str, **metadata: Any) -> None:
    state = _active_run.get()
    if state is not None:
        state["status"] = status
        state["span"].set_status(status, **metadata)


def _observed_agent(name: str):
    """Trace one invocation without changing the existing public call contract."""
    def decorate(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            prompt = kwargs.get("user_message", kwargs.get("prompt"))
            if prompt is None and len(args) > 1:
                prompt = args[1]
            with run_context(name, metadata={"agent_kind": name, "agent_run_id": uuid.uuid4().hex}) as span:
                span.update(input=prompt)
                state = {"span": span, "status": None}
                token = _active_run.set(state)
                try:
                    result = fn(*args, **kwargs)
                    span.update(output=result[0] if isinstance(result, tuple) else result)
                    if state["status"] is None:
                        span.set_status("completed")
                    return result
                except (KeyboardInterrupt, GeneratorExit):
                    span.set_status("cancelled")
                    raise
                finally:
                    _active_run.reset(token)
        return wrapped
    return decorate


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
    model_id: str | None = None,
) -> Generator[tuple[str, Any], None, None]:
    """逐 token 流式消费 API 响应，实时 yield 事件。

    事件类型：
      ("text_delta", str)   — 文本增量，逐 token 产出，可用于打字机输出
      ("truncated", bool)   — 是否因 max_tokens 截断
      ("tool_calls", list)  — 完整的工具调用列表（流结束后一次性 yield）
    """
    with observation(
        "llm.generate", as_type="generation", model=model_id or MODEL_ID,
        input={"system": system_prompt or SYSTEM_PROMPT, "messages": messages,
               "tools": tools or TOOL_DEFINITIONS},
        model_parameters={"max_tokens": max_tokens},
    ) as generation:
        tool_use_blocks: dict[int, dict[str, Any]] = {}
        was_truncated = False

        with client.messages.stream(
            model=(model_id or MODEL_ID),
            max_tokens=max_tokens,
            system=system_prompt or SYSTEM_PROMPT,
            messages=messages,
            tools=tools or TOOL_DEFINITIONS,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        if event.delta.text:
                            generation.first_token()
                        yield ("text_delta", event.delta.text)

                    elif event.delta.type == "input_json_delta":
                        if event.delta.partial_json:
                            generation.first_token()
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
                                repaired = _repair_json(raw_json)
                                if repaired is None:
                                    # Unrepairable (stream cut off mid-argument):
                                    # mark the block so it gets dropped below
                                    # instead of executing garbage input.
                                    block["_parse_failed"] = True
                                    block["input"] = {}
                                else:
                                    block["input"] = repaired
                        else:
                            block["input"] = {}

            final_msg = stream.get_final_message()
            record_response(generation, final_msg)
            if final_msg.stop_reason == "max_tokens":
                was_truncated = True
                generation.set_status("truncated", stop_reason="max_tokens")
                logger.warning("Response truncated at max_tokens=%d", max_tokens)

        tool_calls_list = _collect_tool_calls(tool_use_blocks)

        usage = getattr(final_msg, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        if input_tokens is not None:
            usage_stats["prompt_tokens"] += input_tokens
        if output_tokens is not None:
            usage_stats["completion_tokens"] += output_tokens

    if was_truncated:
        yield ("truncated", True)
    if tool_calls_list:
        yield ("tool_calls", tool_calls_list)
    if input_tokens is not None:
        # Anthropic-convention providers report input_tokens as only the
        # un-cached, un-written delta; the cached prefix arrives separately
        # (cache_read = hit, cache_creation = written this turn).  Compaction
        # and usage tracking need the effective prompt size: sum all three.
        cache_read = getattr(usage, "cache_read_input_tokens", None) or 0
        cache_creation = getattr(usage, "cache_creation_input_tokens", None) or 0
        effective_input = input_tokens + cache_read + cache_creation
        yield ("usage", effective_input)


def _collect_tool_calls(tool_use_blocks: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Collect completed tool_use blocks, dropping unusable ones.

    Blocks whose content_block_stop never fired (stream truncated mid-JSON)
    and blocks with unparseable input are dropped: they have no input the
    dispatcher could execute, and including them would crash or poison history.
    """
    tool_calls_list = []
    for idx in sorted(tool_use_blocks):
        block = tool_use_blocks[idx]
        if not block.get("_complete"):
            logger.warning(
                "Dropping incomplete tool call %r (stream ended mid-JSON)", block["name"],
            )
            continue
        if block.get("_parse_failed"):
            logger.warning("Dropping tool call %r with unparseable input", block["name"])
            continue
        tool_calls_list.append(
            {
                "id": block["id"],
                "name": block["name"],
                "input": block.get("input", {}),
            }
        )
    return tool_calls_list


def _repair_json(raw: str) -> dict[str, Any] | None:
    """Best-effort repair of a truncated/partial tool-input JSON string.

    Returns the parsed dict, or None when the payload is beyond repair —
    callers must treat None as "no usable tool input" rather than {}.
    """
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
    logger.error("Could not repair JSON, giving up: %s", raw[:100])
    return None


@_observed_agent("agent.subagent")
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
        with bind_context(iteration=iteration + 1), observation(
            "agent.iteration", metadata={"iteration": iteration + 1, "max_iterations": max_iterations},
        ):
            if needs_compaction(sub_last_input_tokens, sub_pending_delta):
                messages[:] = llm_compact_messages(messages, client, MODEL_ID)
                sub_last_input_tokens = estimate_messages_tokens(messages)
                sub_pending_delta = 0

            collected_content = ""
            has_tool_calls = False
            was_truncated = False
            tool_calls_list = []

            for retry in range(MAX_API_RETRIES):
                try:
                    with bind_context(attempt=retry + 1):
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
                    _set_run_status("api_error", status_code=e.status_code)
                    return f"[Subagent error] API status {e.status_code}: {e.message}"
                except anthropic.APIConnectionError as e:
                    if retry < MAX_API_RETRIES - 1:
                        time.sleep(RETRY_BASE_DELAY * (2 ** retry))
                        continue
                    _set_run_status("api_error", error_type="connection")
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
                # Truncated tool calls were never executed — close them with
                # synthetic results so the tool_use/tool_result contract holds.
                trunc_results: list[dict[str, Any]] = [
                    {
                        "type": "tool_result",
                        "tool_use_id": tc["id"],
                        "content": (
                            "This tool call was cut off by the output token limit "
                            "and was NOT executed. Re-issue it if still needed."
                        ),
                        "is_error": True,
                    }
                    for tc in tool_calls_list
                ]
                trunc_text = "[System: Response truncated. Continue from where you left off.]"
                if trunc_results:
                    trunc_results.append({"type": "text", "text": trunc_text})
                    trunc_msg = {"role": "user", "content": trunc_results}
                else:
                    trunc_msg = {"role": "user", "content": trunc_text}
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

    _set_run_status("iteration_limit", max_iterations=max_iterations)
    partial = collected_content[:500]
    return (
        f"[Subagent hit iteration limit ({max_iterations}). "
        f"Partial result: {partial}]"
    )


@_observed_agent("agent.subagent")
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
        with bind_context(iteration=iteration + 1), observation(
            "agent.iteration", metadata={"iteration": iteration + 1, "max_iterations": max_iterations},
        ):
            if needs_compaction(sub_last_input_tokens, sub_pending_delta):
                messages[:] = llm_compact_messages(messages, client, MODEL_ID)
                sub_last_input_tokens = estimate_messages_tokens(messages)
                sub_pending_delta = 0

            collected_content = ""
            has_tool_calls = False
            was_truncated = False
            tool_calls_list = []

            for retry in range(MAX_API_RETRIES):
                try:
                    with bind_context(attempt=retry + 1):
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
                    _set_run_status("api_error", status_code=e.status_code)
                    return f"[Subagent error] API status {e.status_code}: {e.message}"
                except anthropic.APIConnectionError as e:
                    if retry < MAX_API_RETRIES - 1:
                        time.sleep(RETRY_BASE_DELAY * (2 ** retry))
                        continue
                    _set_run_status("api_error", error_type="connection")
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
                # Truncated tool calls were never executed — close them with
                # synthetic results so the tool_use/tool_result contract holds.
                trunc_results: list[dict[str, Any]] = [
                    {
                        "type": "tool_result",
                        "tool_use_id": tc["id"],
                        "content": (
                            "This tool call was cut off by the output token limit "
                            "and was NOT executed. Re-issue it if still needed."
                        ),
                        "is_error": True,
                    }
                    for tc in tool_calls_list
                ]
                trunc_text = "[System: Response truncated. Continue from where you left off.]"
                if trunc_results:
                    trunc_results.append({"type": "text", "text": trunc_text})
                    trunc_msg = {"role": "user", "content": trunc_results}
                else:
                    trunc_msg = {"role": "user", "content": trunc_text}
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

    _set_run_status("iteration_limit", max_iterations=max_iterations)
    partial = collected_content[:500]
    return (
        f"[Subagent hit iteration limit ({max_iterations}). "
        f"Partial result: {partial}]"
    )


# Re-export for backward compatibility — cli.py imports this from agent_loop
__all__ = ["register_delegate_tool"]


@_observed_agent("agent.run")
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
    include_skills_in_prompt: bool = False,
    tool_dispatcher=None,
    parallel_enabled: bool = True,
    parallel_max_workers: int = 4,
    model_id: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    if messages is None:
        messages = []

    _model_id = model_id or MODEL_ID

    # Use provided dispatcher or fall back to global
    _dispatcher = tool_dispatcher or dispatcher
    _tools = tools or TOOL_DEFINITIONS
    _system_prompt = system_prompt or _build_default_system_prompt(include_skills_in_prompt)
    _dispatcher.set_confirm_callback(confirm_callback)
    user_msg = {"role": "user", "content": user_message}
    messages.append(user_msg)
    usage_stats["pending_delta"] += estimate_messages_tokens([user_msg])

    recovery_state = _RecoveryState()
    current_max_tokens = MAX_OUTPUT_TOKENS

    for iteration in range(max_iterations):
        with bind_context(iteration=iteration + 1), observation(
            "agent.iteration", metadata={"iteration": iteration + 1, "max_iterations": max_iterations},
        ):
            if needs_compaction(
                usage_stats["last_input_tokens"], usage_stats["pending_delta"]
            ):
                messages[:] = llm_compact_messages(messages, client, _model_id)
                usage_stats["last_input_tokens"] = estimate_messages_tokens(messages)
                usage_stats["pending_delta"] = 0

            remaining = max_iterations - iteration
            iteration_system = (
                f"[System: Iteration {iteration + 1}/{max_iterations}. "
                f"You have {remaining} iterations remaining. "
                f"{_budget_hint(remaining, max_iterations)}]"
            )

            # ── Build iteration system prompt ──
            _iter_system_prompt = _system_prompt

            # Inner loop: truncation escalation / reactive-compact recovery
            while True:
                collected_content = ""
                has_tool_calls = False
                was_truncated = False
                tool_calls_list = []
                retry_unchanged = False

                for retry in range(MAX_API_RETRIES):
                    try:
                        with bind_context(
                            attempt=retry + 1,
                            recovery_count=recovery_state.recovery_count,
                            output_limit_escalated=recovery_state.has_escalated,
                            reactive_compact_attempted=recovery_state.has_attempted_reactive_compact,
                        ):
                            for event_type, data in stream_response(
                                client, messages,
                                system_prompt=_iter_system_prompt, tools=_tools,
                                max_tokens=current_max_tokens,
                                model_id=_model_id,
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
                        # Path 0: an escalated output budget can exceed the
                        # provider's own cap (e.g. kimi caps at 32K). Revert to
                        # the default limit and retry before anything else, so
                        # this never gets misread as a prompt-too-long error.
                        e_msg = (e.message or "").lower()
                        if (
                            e.status_code == 400
                            and current_max_tokens > MAX_OUTPUT_TOKENS
                            and ("max_tokens" in e_msg or "max tokens" in e_msg)
                        ):
                            logger.warning(
                                "Provider rejected max_tokens=%d (%s), reverting to %d",
                                current_max_tokens, e.message, MAX_OUTPUT_TOKENS,
                            )
                            current_max_tokens = MAX_OUTPUT_TOKENS
                            retry_unchanged = True
                            break
                        # Path 2: context too long — reactive compact
                        if _is_prompt_too_long_error(e):
                            if not recovery_state.has_attempted_reactive_compact:
                                logger.warning("Prompt too long, triggering reactive compact")
                                messages[:] = reactive_compact(messages)
                                recovery_state.has_attempted_reactive_compact = True
                                retry_unchanged = True
                                break
                            logger.error("Context too long even after reactive compact")
                            _set_run_status("context_limit")
                            return "Context too long even after reactive compact.", messages
                        if e.status_code in (429, 503, 529) and retry < MAX_API_RETRIES - 1:
                            delay = RETRY_BASE_DELAY * (2 ** retry)
                            logger.warning("API rate limit/error (status %d), retrying in %.1fs", e.status_code, delay)
                            time.sleep(delay)
                            continue
                        error_msg = f"API error (status {e.status_code}): {e.message}"
                        logger.error(error_msg)
                        _set_run_status("api_error", error_type=type(e).__name__)
                        return error_msg, messages
                    except anthropic.APIConnectionError as e:
                        if retry < MAX_API_RETRIES - 1:
                            delay = RETRY_BASE_DELAY * (2 ** retry)
                            logger.warning("API connection error, retrying in %.1fs", delay)
                            time.sleep(delay)
                            continue
                        error_msg = f"API connection error after retries: {e}"
                        logger.error(error_msg)
                        _set_run_status("api_error", error_type=type(e).__name__)
                        return error_msg, messages

                if retry_unchanged:
                    continue  # retry the same request (reactive compact / budget revert)

                # Path 1: output truncated — preserve the partial output and
                # continue, raising the budget on the first truncation.
                if was_truncated:
                    # Re-deriving tens of thousands of tokens from scratch costs
                    # minutes of wall clock; keep whatever completed and resume.
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
                    if not assistant_content:
                        assistant_content.append({
                            "type": "text",
                            "text": "(response cut off by output token limit before any content)",
                        })
                    truncated_msg = {"role": "assistant", "content": assistant_content}
                    messages.append(truncated_msg)
                    usage_stats["pending_delta"] += estimate_messages_tokens([truncated_msg])

                    # Truncated tool calls were never executed — close them with
                    # synthetic results so the tool_use/tool_result contract holds.
                    trunc_results: list[dict[str, Any]] = [
                        {
                            "type": "tool_result",
                            "tool_use_id": tc["id"],
                            "content": (
                                "This tool call was cut off by the output token limit "
                                "and was NOT executed. Re-issue it if still needed."
                            ),
                            "is_error": True,
                        }
                        for tc in tool_calls_list
                    ]

                    if not recovery_state.has_escalated:
                        current_max_tokens = ESCALATED_MAX_TOKENS
                        recovery_state.has_escalated = True
                        logger.warning(
                            "Response truncated at %d tokens, escalating to %d and resuming from partial output",
                            MAX_OUTPUT_TOKENS, ESCALATED_MAX_TOKENS,
                        )
                    elif recovery_state.recovery_count >= MAX_RECOVERY_RETRIES:
                        logger.error(
                            "Still truncated after %d continuations, giving up",
                            MAX_RECOVERY_RETRIES,
                        )
                        _set_run_status("truncated", recovery_count=recovery_state.recovery_count)
                        return collected_content, messages
                    else:
                        recovery_state.recovery_count += 1
                        logger.warning(
                            "Still truncated at max_tokens=%d, continuation %d/%d",
                            current_max_tokens,
                            recovery_state.recovery_count, MAX_RECOVERY_RETRIES,
                        )

                    cont_text = (
                        "Output token limit hit. Resume directly — "
                        "no apology, no recap. Pick up mid-thought."
                    )
                    if trunc_results:
                        trunc_results.append({"type": "text", "text": cont_text})
                        cont_msg = {"role": "user", "content": trunc_results}
                    else:
                        cont_msg = {"role": "user", "content": cont_text}
                    messages.append(cont_msg)
                    usage_stats["pending_delta"] += estimate_messages_tokens([cont_msg])
                    continue

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

            # Close every tool call before exiting so this history can be reused.
            if any(tc.get("name") == "exit_loop" for tc in tool_calls_list):
                tool_results = []
                for tc in tool_calls_list:
                    if tc["name"] == "exit_loop":
                        result = {
                            "type": "tool_result",
                            "tool_use_id": tc["id"],
                            "content": "Loop exit signaled. Task complete.",
                        }
                    else:
                        result = {
                            "type": "tool_result",
                            "tool_use_id": tc["id"],
                            "content": "Tool execution skipped because exit_loop was requested.",
                            "is_error": True,
                        }
                    # These calls bypass the dispatcher. Record the control-flow
                    # outcome without counting skipped tools as executions.
                    with observation(
                        "tool.control", as_type="tool",
                        metadata={"tool_name": tc["name"], "tool_use_id": tc["id"],
                                  "executed": tc["name"] == "exit_loop"},
                    ) as tool_span:
                        tool_span.set_status("completed" if tc["name"] == "exit_loop" else "skipped")
                    tool_results.append(result)

                result_msg = {"role": "user", "content": tool_results}
                messages.append(result_msg)
                usage_stats["pending_delta"] += estimate_messages_tokens([result_msg])

                logger.info("Agent signaled exit_loop, stopping agent_loop")
                return collected_content, messages

            # PRDBench mode: log tool calls for progress tracking
            if os.environ.get("PRDBENCH_MODE") == "true":
                tool_names = [tc["name"] for tc in tool_calls_list]
                logger.info(f"[PRDBench] Iteration {iteration + 1}: tool calls = {tool_names}")

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

    _set_run_status("iteration_limit", max_iterations=max_iterations)
    return "Agent reached maximum iterations without completing the task.", messages
