"""Real-API smoke test for the subagent/delegate mechanism.

Uses MODEL_ID / BASE_URL from .env; credential from ANTHROPIC_AUTH_TOKEN env.

Checks:
  1. run_subagent end-to-end: multi-step task (list dir + read file) completes
     and returns a non-error summary.
  2. Delegate trigger: with the delegate tool offered, an explicit instruction
     makes the model emit a delegate tool_use; its prompt arg is then actually
     executed via run_subagent (full parent -> child path).
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
os.environ["API_KEY"] = API_KEY or ""
os.environ["BASE_URL"] = BASE_URL or ""

from anthropic import Anthropic

from src.agent_loop import SUBAGENT_TOOLS, SYSTEM_PROMPT, TOOL_DEFINITIONS, run_subagent
from src.tools import register_delegate_tool

client = Anthropic(api_key=API_KEY, base_url=BASE_URL, timeout=300)

results = []


def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


# --- 1. run_subagent end-to-end ------------------------------------------------
sub_prompt = (
    "List the files in the workspace root directory, then summarize in 2-3 "
    "sentences what kind of project this appears to be. Return only the summary."
)
sub_result = run_subagent(client, sub_prompt, max_iterations=6)
sub_ok = bool(sub_result.strip()) and not sub_result.startswith(("[Subagent error", "[Subagent hit"))
check("1_run_subagent_e2e", sub_ok, f"len={len(sub_result)} head={sub_result[:100]!r}")

# --- 2. delegate trigger + full parent->child path ------------------------------
register_delegate_tool(client)
assert "delegate" in [t["name"] for t in TOOL_DEFINITIONS]

parent_prompt = (
    "You MUST use the delegate tool to complete this task: "
    "'Count how many Python files are under test/ and report the number.' "
    "Do not use any other tool yourself. After delegation, report the sub-agent's answer."
)
resp = client.messages.create(
    model=MODEL_ID, max_tokens=4096, system=SYSTEM_PROMPT,
    tools=TOOL_DEFINITIONS,
    messages=[{"role": "user", "content": parent_prompt}],
)
delegate_call = next((b for b in resp.content if b.type == "tool_use" and b.name == "delegate"), None)
if delegate_call is None:
    check("2_delegate_triggered", False,
          f"model did not call delegate; blocks={[b.type for b in resp.content]}")
else:
    check("2_delegate_triggered", True,
          f"prompt arg len={len(delegate_call.input.get('prompt', ''))}, "
          f"max_iterations={delegate_call.input.get('max_iterations', 'default')}")

    # feed the delegate result back like the parent loop would
    delegated = run_subagent(client, delegate_call.input["prompt"],
                             max_iterations=int(delegate_call.input.get("max_iterations", 6)))
    child_ok = bool(delegated.strip()) and not delegated.startswith(("[Subagent error", "[Subagent hit"))
    check("3_child_execution", child_ok, f"child result head={delegated[:100]!r}")

    m_followup = [
        {"role": "user", "content": parent_prompt},
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": delegate_call.id, "name": "delegate",
             "input": delegate_call.input},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": delegate_call.id,
             "content": delegated[:2000]},
        ]},
    ]
    final = client.messages.create(model=MODEL_ID, max_tokens=1024, system=SYSTEM_PROMPT,
                                   tools=TOOL_DEFINITIONS, messages=m_followup)
    final_text = "".join(b.text for b in final.content if b.type == "text")
    check("4_parent_synthesizes", bool(final_text.strip()),
          f"final answer head={final_text[:100]!r}")

print("\n=== Summary ===")
for name, ok, detail in results:
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
fails = [n for n, ok, _ in results if not ok]
print(f"\n{len(results) - len(fails)}/{len(results)} passed" + (f"; failed: {fails}" if fails else ""))
sys.exit(1 if fails else 0)
