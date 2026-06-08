import json
import logging
import os
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
)
from .tools import (
    ALLOWED_BASE_DIR,
    TOOL_DEFINITIONS,
    _truncate_for_context,
    dispatcher,
    execute_tool,
    register_delegate_tool,
)
from .task_system import (
    task_manager
)
from .skill_loader import SKILL_LOADER
from ._constants import client

load_dotenv()
MODEL_ID = os.getenv("MODEL_ID")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

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

def _validate_config() -> None:
    missing = []
    if not MODEL_ID:
        missing.append("MODEL_ID")
    if not API_KEY:
        missing.append("API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them in .env or export them before running."
        )

MAX_OUTPUT_TOKENS = 16384

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
        max_tokens=MAX_OUTPUT_TOKENS,
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
        tool_results: list[dict[str, Any]] = []
        for tc in tool_calls_list:
            result = execute_tool(tc["name"], tc["input"], skip_permission_check=True)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc["id"],
                "content": _truncate_for_context(result),
            })
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
    rounds_since_todo: int = 0
) -> tuple[str, list[dict[str, Any]]]:
    if messages is None:
        messages = []
    dispatcher.set_confirm_callback(confirm_callback)
    user_msg = {"role": "user", "content": user_message}
    messages.append(user_msg)
    usage_stats["pending_delta"] += estimate_messages_tokens([user_msg])

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

        collected_content = ""
        has_tool_calls = False
        was_truncated = False
        tool_calls_list = []

        for retry in range(MAX_API_RETRIES):
            try:
                for event_type, data in stream_response(client, messages):
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

        # 输出被截断时，跳过不完整的 tool_calls，提示模型继续
        if was_truncated:
            truncate_hint = (
                "[System: Your previous response was truncated due to output length limit. "
                "Please continue. If you were writing a file, try again with smaller chunks "
                "or split the content across multiple write_file calls.]"
            )
            trunc_msg = {"role": "user", "content": truncate_hint}
            messages.append(trunc_msg)
            usage_stats["pending_delta"] += estimate_messages_tokens([trunc_msg])
            continue

        if not has_tool_calls:
            return collected_content, messages

        used_todo = False
        tool_results: list[dict[str, Any]] = []

        # Inject iteration awareness so the model can plan its work
        tool_results.append(
            {
                "type": "text",
                "text": iteration_system,
            }
        )

        for tc in tool_calls_list:
            fn_name = tc["name"]
            fn_args = tc["input"]

            if fn_name == "task":
                used_todo = True
            rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
            if on_tool_start:
                on_tool_start(fn_name, fn_args)

            result = execute_tool(fn_name, fn_args)

            if on_tool_result:
                on_tool_result(fn_name, result)

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tc["id"],
                    "content": _truncate_for_context(result),
                }
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

    return "Agent reached maximum iterations without completing the task.", messages
