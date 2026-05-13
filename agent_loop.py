import json
import logging
import os
from typing import Any, Callable, Generator

import anthropic
from dotenv import load_dotenv

from compact import (
    MAX_CONTEXT_TOKENS,
    llm_compact_messages,
)
from tools import (
    ALLOWED_BASE_DIR,
    TOOL_DEFINITIONS,
    _truncate_for_context,
    dispatcher,
    execute_tool,
)
from todo_write import (
    TodoManager
)

load_dotenv()
MODEL_ID = os.getenv("MODEL_ID")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

SYSTEM_PROMPT = f"""You are a helpful coding assistant at {ALLOWED_BASE_DIR}. You can help users with software engineering tasks.
When writing code, always provide complete and correct implementations.
Think step by step and explain your reasoning clearly."""

logger = logging.getLogger("penguin")

# Callback type aliases
ContentCallback = Callable[[str], None]
ToolStartCallback = Callable[[str, dict], None]
ToolResultCallback = Callable[[str, str], None]

MAX_API_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # seconds
KEEP_RECENT_TOOLS = 5
PRESERVE_RESULT_TOOLS = []
TODO = TodoManager()

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

def stream_response(
    client: anthropic.Anthropic, messages: list[dict[str, Any]]
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
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=TOOL_DEFINITIONS,
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

    if was_truncated:
        yield ("truncated", True)
    if tool_calls_list:
        yield ("tool_calls", tool_calls_list)


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


def agent_loop(
    client: anthropic.Anthropic,
    user_message: str,
    max_iterations: int = 10,
    on_content: ContentCallback | None = None,
    on_tool_start: ToolStartCallback | None = None,
    on_tool_result: ToolResultCallback | None = None,
    messages: list[dict[str, Any]] | None = None,
    rounds_since_todo: int = 0
) -> tuple[str, list[dict[str, Any]]]:
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": user_message})

    for iteration in range(max_iterations):
        messages[:] = llm_compact_messages(
            messages, client, MODEL_ID, max_tokens=MAX_CONTEXT_TOKENS
        )

        collected_content = ""
        has_tool_calls = False
        was_truncated = False
        tool_calls_list = []

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
        except anthropic.APIStatusError as e:
            error_msg = f"API error (status {e.status_code}): {e.message}"
            logger.error(error_msg)
            return error_msg, messages
        except anthropic.APIConnectionError as e:
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

        messages.append({"role": "assistant", "content": assistant_content})

        # 输出被截断时，跳过不完整的 tool_calls，提示模型继续
        if was_truncated:
            truncate_hint = (
                "[System: Your previous response was truncated due to output length limit. "
                "Please continue. If you were writing a file, try again with smaller chunks "
                "or split the content across multiple write_file calls.]"
            )
            messages.append({"role": "user", "content": truncate_hint})
            continue

        if not has_tool_calls:
            return collected_content, messages

        used_todo = False
        tool_results: list[dict[str, Any]] = []
        for tc in tool_calls_list:
            fn_name = tc["name"]
            fn_args = tc["input"]

            if fn_name == "todo":
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
        if rounds_since_todo >= 3:
            messages.append({"type": "text", "text": "<reminder>Update your todos.</reminder>"})
        messages.append({"role": "user", "content": tool_results})

    return "Agent reached maximum iterations without completing the task.", messages


def main():
    _validate_config()

    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    client = anthropic.Anthropic(
        api_key=API_KEY,
        base_url=BASE_URL,
    )

    print(f"Penguin Coding Agent (working directory: {ALLOWED_BASE_DIR})")
    print("-" * 50)
    print(f"Available tools: {', '.join(dispatcher.list_tools())}")
    print(f"Context budget: ~{MAX_CONTEXT_TOKENS} tokens")
    print("-" * 50)

    conversation_history: list[dict[str, Any]] = []
    rounds_since_todo = 0
    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        print("\nAgent: ", end="", flush=True)

        def on_content(text: str):
            print(text, end="", flush=True)

        def on_tool_start(name: str, args: dict):
            print(
                f"\n[Tool: {name}({json.dumps(args, ensure_ascii=False)})]", flush=True
            )

        def on_tool_result(name: str, result: str):
            preview = result[:200] + "..." if len(result) > 200 else result
            print(f"[Result: {preview}]", flush=True)
            print("\nAgent: ", end="", flush=True)

        final_response, conversation_history = agent_loop(
            client,
            user_input,
            max_iterations=10,
            on_content=on_content,
            on_tool_start=on_tool_start,
            on_tool_result=on_tool_result,
            messages=conversation_history,
            rounds_since_todo=rounds_since_todo
        )

        print()


if __name__ == "__main__":
    main()
