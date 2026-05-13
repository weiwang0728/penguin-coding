import json
import logging
from typing import Any

MAX_CONTEXT_TOKENS = 100_000
MAX_SINGLE_MESSAGE_TOKENS = 5_000

logger = logging.getLogger("penguin")

COMPACT_SYSTEM_PROMPT = """You are a conversation compactor. Summarize the conversation history between a user and a coding assistant.

Your summary MUST preserve:
1. Tasks requested and their completion status
2. Key decisions and their rationale
3. File paths that were read, written, or edited (with brief description of changes)
4. Errors encountered and how they were resolved
5. Current work in progress and next steps

Format the summary as structured bullet points. Be concise but complete — this summary replaces the original conversation, so any lost information is permanently lost."""


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def estimate_messages_tokens(messages: list[dict[str, Any]]) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, str):
            total += estimate_tokens(content)
        elif isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                block_type = block.get("type")
                if block_type == "text":
                    total += estimate_tokens(block.get("text", ""))
                elif block_type == "tool_use":
                    total += estimate_tokens(json.dumps(block.get("input", {}))) + 20
                elif block_type == "tool_result":
                    rc = block.get("content", "")
                    if isinstance(rc, str):
                        total += estimate_tokens(rc)
                    elif isinstance(rc, list):
                        for sub in rc:
                            if isinstance(sub, dict):
                                total += estimate_tokens(sub.get("text", ""))
                    total += 10
    return total


_WRITE_TOOLS = {"write_file", "edit_file"}
_EXPLORE_TOOLS = {"list_directory", "search_files"}


def _classify_tool(tool_name: str) -> str:
    if tool_name in _WRITE_TOOLS:
        return "write"
    if tool_name in _EXPLORE_TOOLS:
        return "explore"
    return "read"


def _extract_tool_info(block: dict) -> tuple[str, str, str]:
    """从 tool_use block 提取 (name, path, input_summary)。"""
    name = block.get("name", "unknown")
    inp = block.get("input", {})
    path = inp.get("path", inp.get("directory", ""))
    if name == "run_command" and inp.get("command"):
        path = inp["command"][:120]
    brief = json.dumps(inp, ensure_ascii=False)[:150] if inp else ""
    return name, path, brief


def _is_error_result(block: dict) -> bool:
    """判断 tool_result 是否为错误结果。"""
    if block.get("is_error"):
        return True
    rc = block.get("content", "")
    if isinstance(rc, str):
        low = rc.lower()
        return any(kw in low for kw in ("error", "traceback", "exception", "failed", "permission denied"))
    return False


def _compact_tool_round(
    assistant_msg: dict, user_msg: dict
) -> tuple[dict, dict]:
    assistant_content = assistant_msg.get("content", [])
    user_content = user_msg.get("content", [])

    # 收集 assistant 侧信息
    tool_calls: list[tuple[str, str, str]] = []  # (name, path, brief)
    text_parts: list[str] = []
    if isinstance(assistant_content, list):
        for block in assistant_content:
            if isinstance(block, dict):
                if block.get("type") == "tool_use":
                    tool_calls.append(_extract_tool_info(block))
                elif block.get("type") == "text":
                    t = block.get("text", "")
                    if t:
                        text_parts.append(t[:80])

    # 收集 user 侧 tool_result，按 index 与 tool_calls 对齐
    tool_results: list[dict] = []
    if isinstance(user_content, list):
        for block in user_content:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                tool_results.append(block)

    # 按工具类型差异化生成摘要
    call_summaries = []
    result_parts = []

    for idx, (name, path, brief) in enumerate(tool_calls):
        category = _classify_tool(name)
        result_block = tool_results[idx] if idx < len(tool_results) else None
        is_error = _is_error_result(result_block) if result_block else False

        # assistant 侧摘要
        if category == "write":
            call_summaries.append(f"{name}({path})" if path else f"{name}")
        elif category == "read":
            call_summaries.append(f"read({path})" if path else name)
        else:
            call_summaries.append(name)

        # user 侧摘要 — 按重要性分级
        if is_error:
            rc = result_block.get("content", "")
            preview = rc[:300] if isinstance(rc, str) else "[error]"
            result_parts.append(f"ERROR({name}): {preview}")
        elif category == "write":
            result_parts.append(f"OK({name}: {path})" if path else f"OK({name})")
        elif category == "read":
            rc = result_block.get("content", "")
            if isinstance(rc, str) and rc:
                head = rc[:100]
                result_parts.append(f"{name}({path}): {head}" if path else f"{name}: {head}")
            else:
                result_parts.append(f"{name}({path}): [done]" if path else f"{name}: [done]")
        else:  # explore
            rc = result_block.get("content", "")
            if isinstance(rc, str) and rc:
                first_lines = "\n".join(rc.split("\n")[:5])[:100]
                result_parts.append(f"{name}: {first_lines}")
            else:
                result_parts.append(f"{name}: [done]")

    # 组装 assistant 消息
    parts = []
    if text_parts:
        parts.append("Text: " + "; ".join(text_parts))
    if call_summaries:
        parts.append("Called: " + ", ".join(call_summaries))
    a_text = "[Compacted] " + " | ".join(parts) if parts else "[Compacted]"

    # 组装 user 消息
    if result_parts:
        u_text = "[Compacted results] " + " | ".join(result_parts)
        u_text = u_text[:500]
    else:
        u_text = "[Compacted tool results]"

    return (
        {"role": "assistant", "content": a_text},
        {"role": "user", "content": u_text},
    )


def _strip_old_thinking(
    messages: list[dict[str, Any]], keep_recent: int = 2
) -> list[dict[str, Any]]:
    """移除旧的 thinking block，最近 keep_recent 轮 assistant 保留截断尾部。"""
    assistant_indices = [
        i for i, m in enumerate(messages) if m.get("role") == "assistant"
    ]
    recent_set = set(assistant_indices[-keep_recent:]) if assistant_indices else set()

    result = []
    for i, msg in enumerate(messages):
        content = msg.get("content")
        if msg.get("role") != "assistant" or not isinstance(content, list):
            result.append(msg)
            continue
        if i not in recent_set:
            new_blocks = [b for b in content if not (isinstance(b, dict) and b.get("type") == "thinking")]
            if len(new_blocks) == len(content):
                result.append(msg)
            else:
                result.append({"role": "assistant", "content": new_blocks})
        else:
            new_blocks = []
            changed = False
            for b in content:
                if isinstance(b, dict) and b.get("type") == "thinking":
                    text = b.get("thinking", "")
                    if estimate_tokens(text) > 100:
                        new_blocks.append({"type": "thinking", "thinking": text[-200:]})
                        changed = True
                    else:
                        new_blocks.append(b)
                else:
                    new_blocks.append(b)
            if changed:
                result.append({"role": "assistant", "content": new_blocks})
            else:
                result.append(msg)
    return result


def _compact_oversized_blocks(
    msg: dict[str, Any], max_tokens: int = MAX_SINGLE_MESSAGE_TOKENS
) -> dict[str, Any]:
    if estimate_messages_tokens([msg]) <= max_tokens:
        return msg

    content = msg.get("content")

    # 情况 1: content 是纯字符串 — 直接截断
    if isinstance(content, str):
        if estimate_tokens(content) > max_tokens:
            truncated = content[: max_tokens * 4]
            return {
                "role": msg.get("role", "user"),
                "content": truncated + f"\n... [Truncated: {len(content)} chars total]",
            }
        return msg

    # 情况 2: content 不是 list — 无法处理
    if not isinstance(content, list):
        return msg

    # 情况 3: content 是 block 列表 — 逐 block 检查
    changed = False
    new_blocks = []
    for block in content:
        if not isinstance(block, dict):
            new_blocks.append(block)
            continue

        block_type = block.get("type")

        # 3a: text block 过大 → 截断
        if block_type == "text":
            text = block.get("text", "")
            if estimate_tokens(text) > max_tokens:
                truncated = text[: max_tokens * 4]
                new_blocks.append({
                    "type": "text",
                    "text": truncated + f"\n... [Truncated: {len(text)} chars total]",
                })
                changed = True
                continue

        # 3c: tool_result — content 为 str 或 list 都要处理
        elif block_type == "tool_result":
            rc = block.get("content", "")
            if isinstance(rc, str) and estimate_tokens(rc) > max_tokens:
                truncated = rc[: max_tokens * 4]
                new_blocks.append({
                    "type": "tool_result",
                    "tool_use_id": block.get("tool_use_id", ""),
                    "content": truncated + f"\n... [Truncated: {len(rc)} chars total]",
                })
                changed = True
                continue
            elif isinstance(rc, list):
                # 嵌套 content blocks 中可能有 text/image
                new_sub_blocks = []
                sub_changed = False
                for sub in rc:
                    if isinstance(sub, dict):
                        if sub.get("type") == "text" and estimate_tokens(sub.get("text", "")) > max_tokens:
                            truncated = sub["text"][: max_tokens * 4]
                            new_sub_blocks.append({
                                "type": "text",
                                "text": truncated + f"\n... [Truncated]",
                            })
                            sub_changed = True
                            continue
                        elif sub.get("type") == "image":
                            # 图片太大无法压缩，直接移除占位标记
                            new_sub_blocks.append({
                                "type": "text",
                                "text": "[Image removed due to size]",
                            })
                            sub_changed = True
                            continue
                    new_sub_blocks.append(sub)
                if sub_changed:
                    new_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": block.get("tool_use_id", ""),
                        "content": new_sub_blocks,
                    })
                    changed = True
                    continue

        # 3d: thinking block 过大 → 截断
        elif block_type == "thinking":
            thinking = block.get("thinking", "")
            if estimate_tokens(thinking) > max_tokens:
                new_blocks.append({
                    "type": "thinking",
                    "thinking": thinking[: max_tokens * 4] + "\n... [Truncated]",
                })
                changed = True
                continue

        # 其他类型原样保留
        new_blocks.append(block)

    if changed:
        return {"role": msg.get("role", "user"), "content": new_blocks}
    return msg


def _serialize_messages(messages: list[dict[str, Any]]) -> str:
    """Convert messages to readable text for LLM summarization."""
    parts = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content")
        if isinstance(content, str):
            parts.append(f"[{role}]: {content}")
        elif isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                block_type = block.get("type")
                if block_type == "text":
                    parts.append(f"[{role}]: {block.get('text', '')}")
                elif block_type == "tool_use":
                    name = block.get("name", "")
                    inp = block.get("input", {})
                    parts.append(
                        f"[{role}/tool_use]: {name}({json.dumps(inp, ensure_ascii=False)[:200]})"
                    )
                elif block_type == "tool_result":
                    rc = block.get("content", "")
                    if isinstance(rc, str):
                        parts.append(f"[{role}/tool_result]: {rc[:500]}")
                    elif isinstance(rc, list):
                        for sub in rc:
                            if isinstance(sub, dict) and sub.get("type") == "text":
                                parts.append(
                                    f"[{role}/tool_result]: {sub.get('text', '')[:500]}"
                                )
    return "\n\n".join(parts)


def _rule_based_trim(
    messages: list[dict[str, Any]], max_tokens: int
) -> list[dict[str, Any]]:
    """Rule-based trimming: keep first message + as many recent pairs as fit."""
    first_msg = messages[0]
    first_tokens = estimate_messages_tokens([first_msg])
    budget = max_tokens - first_tokens

    tail_reversed = []
    used = 0
    i = len(messages) - 1

    while i > 0:
        if (
            i > 1
            and messages[i].get("role") == "user"
            and messages[i - 1].get("role") == "assistant"
        ):
            pair = [messages[i - 1], messages[i]]
            pair_tokens = estimate_messages_tokens(pair)

            if used + pair_tokens <= budget:
                tail_reversed.append(pair[1])
                tail_reversed.append(pair[0])
                used += pair_tokens
                i -= 2
            else:
                compacted_a, compacted_u = _compact_tool_round(pair[0], pair[1])
                compacted_tokens = estimate_messages_tokens([compacted_a, compacted_u])
                if used + compacted_tokens <= budget:
                    tail_reversed.append(compacted_u)
                    tail_reversed.append(compacted_a)
                    used += compacted_tokens
                i -= 2
        else:
            single_tokens = estimate_messages_tokens([messages[i]])
            if used + single_tokens <= budget:
                tail_reversed.append(messages[i])
                used += single_tokens
            i -= 1

    return [first_msg] + list(reversed(tail_reversed))


def llm_compact_messages(
    messages: list[dict[str, Any]],
    client: Any,
    model_id: str,
    max_tokens: int = MAX_CONTEXT_TOKENS,
    keep_recent: int = 4,
    summary_max_tokens: int = 2000,
) -> list[dict[str, Any]]:
    """Compact messages using LLM summarization, with rule-based fallback.

    Flow:
      1. Preprocess: normalize oversized blocks + strip old thinking
      2. If within budget, return immediately
      3. Try LLM summarization of old messages
      4. On failure, fall back to rule-based trimming

    Args:
        messages: The conversation messages to compact.
        client: An anthropic.Anthropic client instance.
        model_id: The model ID to use for summarization.
        max_tokens: Maximum token budget for the compacted messages.
        keep_recent: Number of recent messages to preserve intact.
        summary_max_tokens: Max tokens for the LLM summary output.
    """
    if not messages:
        return messages

    # Step 1: Preprocess — normalize oversized blocks and strip old thinking
    normalized = [_compact_oversized_blocks(messages[0])]
    for msg in messages[1:]:
        normalized.append(_compact_oversized_blocks(msg))
    normalized = _strip_old_thinking(normalized)

    # Step 2: If already within budget, no compacting needed
    if estimate_messages_tokens(normalized) <= max_tokens:
        return normalized

    # Step 3: Try LLM summarization
    try:
        # Split: first message + old messages to summarize + recent messages to keep
        split_idx = max(1, len(normalized) - keep_recent)
        # Ensure recent messages start with assistant for proper user→assistant alternation
        while split_idx < len(normalized) and normalized[split_idx].get("role") != "assistant":
            split_idx += 1

        first_msg = normalized[0]
        old_messages = normalized[1:split_idx]
        recent_messages = normalized[split_idx:]

        if old_messages:
            old_text = _serialize_messages(old_messages)
            summary_response = client.messages.create(
                model=model_id,
                max_tokens=summary_max_tokens,
                system=COMPACT_SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": f"Summarize this conversation:\n\n{old_text}"}
                ],
            )
            summary_text = ""
            for block in summary_response.content:
                if block.type == "text":
                    summary_text += block.text

            # Merge summary into first message to maintain alternation
            first_content = first_msg.get("content", "")
            summary_section = f"\n\n[Conversation Summary]\n{summary_text}"
            if isinstance(first_content, str):
                enhanced_content = first_content + summary_section
            elif isinstance(first_content, list):
                enhanced_content = first_content + [
                    {"type": "text", "text": summary_section}
                ]
            else:
                enhanced_content = summary_section

            result = [{"role": "user", "content": enhanced_content}] + recent_messages

            if estimate_messages_tokens(result) <= max_tokens:
                return result

            # LLM compact didn't fit — fall through to rule-based trim
    except Exception:
        logger.warning("LLM compact failed, falling back to rule-based trim")

    # Step 4: Fallback to rule-based trimming
    return _rule_based_trim(normalized, max_tokens)


def trim_messages(
    messages: list[dict[str, Any]], max_tokens: int = MAX_CONTEXT_TOKENS
) -> list[dict[str, Any]]:
    """Rule-based-only trim (backward compatible, no LLM call)."""
    if not messages:
        return messages

    normalized = [_compact_oversized_blocks(messages[0])]
    for msg in messages[1:]:
        normalized.append(_compact_oversized_blocks(msg))

    normalized = _strip_old_thinking(normalized)

    if estimate_messages_tokens(normalized) <= max_tokens:
        return normalized

    return _rule_based_trim(normalized, max_tokens)
