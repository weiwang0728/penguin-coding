"""Real-API verification of the truncation backfill format (src/agent_loop.py).

Uses MODEL_ID / BASE_URL from .env; credential from ANTHROPIC_AUTH_TOKEN env
(.env's API_KEY currently holds a URL, not a key).

Checks:
  A. Smoke: plain message round-trip.
  B. Forced text truncation via stream_response(max_tokens=300) + fixed-format
     continuation (assistant text-only backfill + user resume prompt) -> 200.
  C. tool_use pairing contract on this endpoint:
     C1 assistant[tool_use] + user[tool_result "not executed"]  -> expect 200
     C2 assistant[tool_use] + user[text only]  (old buggy format) -> expect 400
  D. Fixed recovery path: assistant[text] + user[re-issue prompt] -> 200.
"""

import os
import sys

from dotenv import dotenv_values

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

env = dotenv_values(os.path.join(ROOT, ".env"))
MODEL_ID = env.get("MODEL_ID")
BASE_URL = env.get("BASE_URL")
API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN") or env.get("API_KEY")

# Must be set before importing src._constants: load_dotenv() does not override
# existing env vars, so this wins over the bogus .env API_KEY.
os.environ["API_KEY"] = API_KEY or ""
os.environ["BASE_URL"] = BASE_URL or ""

from anthropic import Anthropic

from src.agent_loop import stream_response

client = Anthropic(api_key=API_KEY, base_url=BASE_URL, timeout=120)

ECHO_TOOL = {
    "name": "echo",
    "description": "Echo the given text back.",
    "input_schema": {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "Text to echo"}},
        "required": ["text"],
    },
}

results = []


def check(name: str, ok: bool, detail: str) -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# --- A. Smoke ---------------------------------------------------------------
resp = client.messages.create(
    model=MODEL_ID, max_tokens=64,
    messages=[{"role": "user", "content": "Reply with exactly: OK"}],
)
smoke = "".join(b.text for b in resp.content if b.type == "text")
check("A_smoke", resp.stop_reason == "end_turn" and "OK" in smoke,
      f"stop_reason={resp.stop_reason}, text={smoke[:40]!r}")

# --- B. Forced truncation + fixed-format continuation ------------------------
messages = [{"role": "user",
             "content": "Write a detailed 1200-word essay on the history of "
                        "operating systems. Plain text only, no tools."}]
collected, truncated = "", False
for ev, data in stream_response(client, messages, max_tokens=300):
    if ev == "text_delta":
        collected += data
    elif ev == "truncated":
        truncated = True
check("B_truncated", truncated, f"stream_response reported truncated={truncated}, "
                                f"partial text len={len(collected)}")

messages.append({"role": "assistant",
                 "content": [{"type": "text", "text": collected}] if collected else []})
messages.append({"role": "user",
                 "content": "Output token limit hit. Resume directly — no apology, "
                            "no recap. Pick up mid-thought."})
cont = client.messages.create(model=MODEL_ID, max_tokens=800, messages=messages)
cont_text = "".join(b.text for b in cont.content if b.type == "text")
cont_any_output = len(getattr(cont, "content", [])) > 0
check("B_continuation_200", cont_any_output and cont_text != "",
      f"status=200, stop={cont.stop_reason}, blocks={[b.type for b in cont.content]}, "
      f"text len={len(cont_text)}, head={cont_text[:60]!r}")

# --- C. tool_use pairing contract --------------------------------------------
resp2 = client.messages.create(
    model=MODEL_ID, max_tokens=1024, tools=[ECHO_TOOL],
    messages=[{"role": "user", "content": "Call the echo tool with text='hello'."}],
)
tool_use = next((b for b in resp2.content if b.type == "tool_use"), None)
if tool_use is None:
    check("C_tool_call_obtained", False, f"model did not call tool; stop={resp2.stop_reason}")
else:
    check("C_tool_call_obtained", True, f"tool_use id={tool_use.id} input={tool_use.input}")

    # C1: tool_use followed by matching tool_result ("not executed")
    m_c1 = [
        {"role": "user", "content": "Call the echo tool with text='hello'."},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_use.id, "name": tool_use.name,
             "input": tool_use.input},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_use.id,
             "content": "[Tool call interrupted by output limit — not executed]"},
        ]},
    ]
    try:
        r_c1 = client.messages.create(model=MODEL_ID, max_tokens=512, tools=[ECHO_TOOL], messages=m_c1)
        check("C1_tool_result_pairing_200", True, f"stop={r_c1.stop_reason}")
    except Exception as e:
        check("C1_tool_result_pairing_200", False, f"error: {e}")

    # C2: old buggy format — tool_use followed by plain text user message
    m_c2 = m_c1[:2] + [{"role": "user", "content": "Output token limit hit. Continue."}]
    try:
        r_c2 = client.messages.create(model=MODEL_ID, max_tokens=512, tools=[ECHO_TOOL], messages=m_c2)
        check("C2_old_format_rejected", False,
              f"endpoint ACCEPTED old buggy format (stop={r_c2.stop_reason}) — "
              f"bug not reproducible on this endpoint")
    except Exception as e:
        check("C2_old_format_rejected", True, f"rejected as expected: {str(e)[:120]}")

# --- D. Fixed recovery path: drop tool_use, text-only backfill ---------------
m_d = [
    {"role": "user", "content": "Call the echo tool with text='hello'."},
    {"role": "assistant", "content": [{"type": "text",
        "text": "I'll echo that for you."}]},  # tool_use dropped
    {"role": "user", "content": "Output token limit hit mid tool call. The call was "
                                "NOT executed. Re-issue the complete tool call."},
]
try:
    r_d = client.messages.create(model=MODEL_ID, max_tokens=512, tools=[ECHO_TOOL], messages=m_d)
    r_d_text = "".join(b.text for b in r_d.content if b.type == "text")
    reissued = any(b.type == "tool_use" for b in r_d.content)
    check("D_fixed_recovery_200", True,
          f"status=200, stop={r_d.stop_reason}, reissued_tool_call={reissued}, "
          f"text={r_d_text[:60]!r}")
except Exception as e:
    check("D_fixed_recovery_200", False, f"error: {e}")

print("\n=== Summary ===")
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
fails = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} passed" + (f"; failed: {fails}" if fails else ""))
sys.exit(1 if fails else 0)
