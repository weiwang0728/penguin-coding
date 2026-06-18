import json
import logging
import unicodedata
from typing import Any

MAX_CONTEXT_TOKENS = 100_000
MAX_TOOL_RESULT_TOKENS = 3_000
MAX_TEXT_BLOCK_TOKENS = 15_000
COMPACT_THRESHOLD = 0.80

logger = logging.getLogger("penguin")

def needs_compaction(
    last_input_tokens: int,
    pending_delta: int,
    max_tokens: int = MAX_CONTEXT_TOKENS,
) -> bool:
    """Fast check whether to run the full compaction pipeline.

    Uses the API-reported input_tokens as the exact baseline and adds
    an estimate of tokens appended since the last API call.  When no
    API data is available (new / resumed session without persisted
    usage), falls back to a full estimate of all messages.

    Args:
        last_input_tokens: input_tokens from the most recent API response.
        pending_delta:     estimated tokens of messages added since that
                           API call (assistant turn + tool results).
        max_tokens:        context window budget.
    """
    if last_input_tokens <= 0:
        return True
    estimated = last_input_tokens + pending_delta
    return estimated > max_tokens * COMPACT_THRESHOLD


COMPACT_SYSTEM_PROMPT = """You are a conversation compactor. Summarize the conversation history between a user and a coding assistant.

Your summary MUST preserve:
1. Tasks requested and their completion status
2. Key decisions and their rationale
3. File paths that were read, written, or edited (with brief description of changes)
4. Errors encountered and how they were resolved
5. Current work in progress and next steps

Format the summary as structured bullet points. Be concise but complete — this summary replaces the original conversation, so any lost information is permanently lost."""

COLLAPSE_SYSTEM_PROMPT = """You are a conversation archivist. The conversation is too long and must be collapsed into a compact structured log.

Group the conversation into logical phases (each phase spans several turns). For each phase, output ONE line with:
- Turn range (e.g. Turn 1-5)
- What was done (actions taken)
- Key conclusion or outcome

At the end, list:
- Files modified (with brief description of changes)
- Current state (what's done, what's pending)

Rules:
- Each phase line must be under 80 characters
- Omit all code details, file contents, and tool output — only preserve decisions and outcomes
- Preserve error/success outcomes so the model doesn't repeat work already done
- If a phase had no meaningful outcome, skip it

Example output format:

[Context collapsed - 30 turns summarized]

Turn 1-5: Read auth module, identified 3 functions without error handling
Turn 6-12: Added try/except to verify_token(), refresh_token(), decode_payload()
Turn 13-15: Ran tests, found regression in test_expired_token
Turn 16-20: Fixed test, all 47 tests passing
Turn 21-25: Updated API documentation for new error responses
Turn 26-30: Code review suggestions applied

Files modified: src/auth.py, tests/test_auth.py, docs/api.md
Current state: All changes committed, ready for PR"""

def estimate_tokens(text: str) -> int:
    """Token estimation: CJK chars ~1.5 tokens each, others ~4 chars/token."""
    if not text:
        return 0
    cjk_count = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ('W', 'F'):
            cjk_count += 1
    non_cjk_len = len(text) - cjk_count
    return max(1, int(cjk_count * 1.5 + non_cjk_len / 4))


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


def _head_tail_truncate(text: str, max_chars: int) -> str:
    """Head+tail truncation: preserve beginning and end, drop the middle."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return (
        text[:half]
        + f"\n... [Truncated: {len(text)} chars total, showing first and last {half} chars] ...\n"
        + text[-half:]
    )


def _strip_old_thinking(
    messages: list[dict[str, Any]], keep_recent: int = 1
) -> list[dict[str, Any]]:
    """移除旧的 thinking block，最近 keep_recent 轮 assistant 完整保留 thinking。"""
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
            result.append(msg)
    return result


def _compact_oversized_blocks(msg: dict[str, Any]) -> dict[str, Any]:
    """只截断 tool_result block（head+tail），其他类型不截断，thinking 交给 _strip_old_thinking。"""
    content = msg.get("content")

    if not isinstance(content, list):
        return msg

    changed = False
    new_blocks = []
    for block in content:
        if not isinstance(block, dict):
            new_blocks.append(block)
            continue

        block_type = block.get("type")

        # tool_result — head+tail 截断
        if block_type == "tool_result":
            rc = block.get("content", "")
            if isinstance(rc, str) and estimate_tokens(rc) > MAX_TOOL_RESULT_TOKENS:
                truncated = _head_tail_truncate(rc, MAX_TOOL_RESULT_TOKENS * 4)
                new_blocks.append({
                    "type": "tool_result",
                    "tool_use_id": block.get("tool_use_id", ""),
                    "content": truncated,
                })
                changed = True
                continue
            elif isinstance(rc, list):
                new_sub_blocks = []
                sub_changed = False
                for sub in rc:
                    if isinstance(sub, dict):
                        if sub.get("type") == "text" and estimate_tokens(sub.get("text", "")) > MAX_TOOL_RESULT_TOKENS:
                            truncated = _head_tail_truncate(sub["text"], MAX_TOOL_RESULT_TOKENS * 4)
                            new_sub_blocks.append({"type": "text", "text": truncated})
                            sub_changed = True
                            continue
                        elif sub.get("type") == "image":
                            new_sub_blocks.append({"type": "text", "text": "[Image removed due to size]"})
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

        # text / tool_use / thinking — 不截断
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


def _context_collapse(
    messages: list[dict[str, Any]],
    client: Any,
    model_id: str,
    max_tokens: int,
    collapse_max_tokens: int = 1000,
) -> list[dict[str, Any]]:
    """CONTEXT_COLLAPSE: replace entire conversation with a structured log.

    Unlike L2 summarization which preserves conversation structure, this
    collapses everything into a Git-log-style archive — each phase on one
    line, no code details, only decisions and outcomes.
    """
    if len(messages) <= 1:
        return messages

    total_turns = len([m for m in messages if m.get("role") == "assistant"])
    old_text = _serialize_messages(messages[:-1])  # exclude last user message

    try:
        collapse_response = client.messages.create(
            model=model_id,
            max_tokens=collapse_max_tokens,
            system=COLLAPSE_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Collapsing {total_turns} turns of conversation:\n\n{old_text}"}
            ],
        )
        collapse_text = ""
        for block in collapse_response.content:
            if block.type == "text":
                collapse_text += block.text
    except Exception:
        logger.warning("Context collapse LLM call failed")
        return messages

    collapse_msg = {
        "role": "user",
        "content": f"[Context collapsed - {total_turns} turns summarized]\n{collapse_text}",
    }
    ack_msg = {
        "role": "assistant",
        "content": "[Context collapsed. Continuing from current state.]",
    }

    result = [collapse_msg, ack_msg]

    if estimate_messages_tokens(result) <= max_tokens:
        return result

    return result  # best effort — still better than nothing


def _verify_tokens_within_budget(
    messages: list[dict[str, Any]],
    client: Any,
    model_id: str,
    max_tokens: int,
) -> bool:
    """Use count_tokens API for precise budget check. Returns True if within budget."""
    try:
        resp = client.messages.count_tokens(
            model=model_id,
            messages=messages,
        )
        actual = resp.input_tokens
        if actual > max_tokens:
            logger.info("count_tokens verification: %d > %d", actual, max_tokens)
            return False
        return True
    except Exception:
        # API unavailable — trust the estimate
        return True


def llm_compact_messages(
    messages: list[dict[str, Any]],
    client: Any,
    model_id: str,
    max_tokens: int = MAX_CONTEXT_TOKENS,
    keep_recent: int = 4,
    summary_max_tokens: int = 2000,
) -> list[dict[str, Any]]:
    """Compact messages using LLM summarization.

    Flow:
      1. Preprocess: normalize oversized blocks + strip old thinking
      2. If within budget, return immediately
      3. L2: LLM summarization of old messages (preserves conversation structure)
      4. If L2 over budget, retry with fewer recent messages
      5. L3: CONTEXT_COLLAPSE — structured archive replacing entire conversation

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
    normalized = [_compact_oversized_blocks(msg) for msg in messages]
    normalized = _strip_old_thinking(normalized)

    # Step 2: If already within budget, no compacting needed
    if estimate_messages_tokens(normalized) <= max_tokens:
        return normalized

    # Step 3: LLM summarization with progressive reduction
    for attempt_keep in (keep_recent, max(2, keep_recent // 2), 0):
        try:
            split_idx = max(1, len(normalized) - attempt_keep)
            while split_idx < len(normalized) and normalized[split_idx].get("role") != "assistant":
                split_idx += 1

            first_msg = normalized[0]
            old_messages = normalized[1:split_idx]
            recent_messages = normalized[split_idx:]

            if not old_messages:
                # Nothing to summarize — keep recent as-is
                return normalized

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

            summary_msg = {
                "role": "user",
                "content": f"[Conversation Summary]\n{summary_text}",
            }
            ack_msg = {
                "role": "assistant",
                "content": "[Prior context acknowledged. Continuing from here.]",
            }

            result = [first_msg, summary_msg, ack_msg] + recent_messages

            if estimate_messages_tokens(result) <= max_tokens:
                if _verify_tokens_within_budget(result, client, model_id, max_tokens):
                    return result

            # Over budget — try with fewer recent messages
            logger.info(
                "Compaction over budget with keep_recent=%d, retrying with %d",
                attempt_keep, max(2, attempt_keep // 2),
            )
        except Exception:
            logger.warning("LLM compact failed (attempt keep_recent=%d)", attempt_keep)
            if attempt_keep == 0:
                break

    # Step 4: CONTEXT_COLLAPSE — structured archive (last resort)
    logger.info("L2 compaction insufficient, attempting CONTEXT_COLLAPSE")
    collapsed = _context_collapse(normalized, client, model_id, max_tokens)
    if estimate_messages_tokens(collapsed) <= max_tokens:
        return collapsed

    # Even collapse didn't fit — return best effort
    return collapsed


def trim_messages(
    messages: list[dict[str, Any]], max_tokens: int = MAX_CONTEXT_TOKENS
) -> list[dict[str, Any]]:
    """Preprocessing-only trim: normalize oversized blocks + strip old thinking.

    Does not call LLM. If still over budget after preprocessing, returns
    preprocessed result — caller should use llm_compact_messages for full compaction.
    """
    if not messages:
        return messages

    normalized = [_compact_oversized_blocks(msg) for msg in messages]
    normalized = _strip_old_thinking(normalized)

    if estimate_messages_tokens(normalized) <= max_tokens:
        return normalized

    # Over budget after preprocessing — return preprocessed, caller handles full compaction
    logger.warning("trim_messages: still over budget after preprocessing")
    return normalized


def reactive_compact(
    messages: list[dict[str, Any]],
    keep_recent: int = 5,
) -> list[dict[str, Any]]:
    """Aggressive reactive compact: keep only the last N messages.

    Used when the LLM rejects the request due to context overflow even after
    the normal (proactive) compaction pipeline has run.  This is a teaching
    implementation — a production version would call the LLM to generate a
    compact summary instead of simply discarding older messages.
    """
    kept = messages if len(messages) <= keep_recent else messages[-keep_recent:]
    # Ensure the first kept message is a user message (API requires user-first)
    if kept and kept[0].get("role") != "user":
        for i, msg in enumerate(kept):
            if msg.get("role") == "user":
                kept = kept[i:]
                break
        else:
            kept.insert(0, {
                "role": "user",
                "content": "[Earlier context removed due to length.]",
            })
    return kept
