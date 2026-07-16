"""Metric-based scorers for E2E test cases.

Each metric has a `type` field that routes it to a specific scorer:
  - file_artifact     → deterministic: file existence + AST/structure checks
  - shell_interaction → deterministic: run command + stdin, normalize, match expected_output
  - unit_test         → deterministic: run pytest, parse PASSED/FAILED counts
  - semantic          → LLM-as-judge (INDEPENDENT call, not the agent under test)

Each scorer returns:
  {name, type, score (0|1|2), weight, method, detail, confidence}

Scoring rubric (aligned with PRDBench):
  2 = fully passed, 1 = partially passed, 0 = not passed

Case-level aggregation normalizes to [0,1]:
  normalized = Σ(score_i * weight_i) / (2 * Σ weight_i)
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Reuse constants/helpers from verifiers.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifiers import PROJECT_ROOT, WORKSPACE  # noqa: E402

# Anthropic client for LLM judge — same client as the agent, but INDEPENDENT call
sys.path.insert(0, str(PROJECT_ROOT))
from src._constants import client, MODEL_ID  # noqa: E402


# ═══════════════════════════════════════════════════════════════
# Utility: output normalization
# ═══════════════════════════════════════════════════════════════

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _normalize_output(text: str) -> str:
    """Strip ANSI escapes and collapse whitespace runs for tolerant matching."""
    if not text:
        return ""
    text = ANSI_ESCAPE.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _match(expected: str, actual: str, mode: str) -> bool:
    """Match expected against actual per mode: contains | exact | regex."""
    if mode == "regex":
        return re.search(expected, actual) is not None
    if mode == "exact":
        return _normalize_output(expected) == _normalize_output(actual)
    # default: contains (normalized)
    return _normalize_output(expected) in _normalize_output(actual)


def _resolve_path(p: str) -> Path:
    """Resolve a metric path to absolute. workspace/-prefixed → PROJECT_ROOT/...,
    otherwise treat as relative to PROJECT_ROOT."""
    if os.path.isabs(p):
        return Path(p)
    if p.startswith("workspace/"):
        return PROJECT_ROOT / p
    return PROJECT_ROOT / p


# ═══════════════════════════════════════════════════════════════
# Scorer: file_artifact
# ═══════════════════════════════════════════════════════════════

def score_file_artifact(metric: dict, ctx: dict) -> dict:
    """Check file existence + AST structure.

    metric.checks supports:
      exists: bool
      has_function: str
      has_main_block: bool
      has_class: str
      size_min: int (bytes)
    """
    name = metric.get("name", "file_artifact")
    path_str = metric.get("path", "")
    checks = metric.get("checks", {}) or {}
    target = _resolve_path(path_str)

    results = []
    if checks.get("exists"):
        results.append(("exists", target.exists()))
        if not target.exists():
            return {
                "name": name, "type": "file_artifact", "score": 0,
                "weight": metric.get("weight", 1.0),
                "method": "file_exists",
                "detail": f"file not found: {path_str}",
                "confidence": "high",
            }

    if not target.exists():
        return {
            "name": name, "type": "file_artifact", "score": 0,
            "weight": metric.get("weight", 1.0),
            "method": "file_exists",
            "detail": f"file not found: {path_str}",
            "confidence": "high",
        }

    size = target.stat().st_size
    if "size_min" in checks:
        results.append(("size_min", size >= checks["size_min"]))

    # AST-based checks (Python files only)
    ast_checks = {"has_function", "has_main_block", "has_class"}
    if any(k in checks for k in ast_checks) and target.suffix == ".py":
        try:
            tree = ast.parse(target.read_text(encoding="utf-8"))
        except SyntaxError as e:
            return {
                "name": name, "type": "file_artifact", "score": 0,
                "weight": metric.get("weight", 1.0),
                "method": "file_ast",
                "detail": f"SyntaxError: {e}",
                "confidence": "high",
            }

        if "has_function" in checks:
            want = checks["has_function"]
            funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            results.append((f"has_function:{want}", want in funcs))

        if "has_class" in checks:
            want = checks["has_class"]
            classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
            results.append((f"has_class:{want}", want in classes))

        if checks.get("has_main_block"):
            found_main = False
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    t = node.test
                    if (isinstance(t, ast.Compare)
                            and isinstance(t.left, ast.Name)
                            and t.left.id == "__name__"
                            and any(isinstance(c, ast.Constant) and c.value == "__main__"
                                    for c in t.comparators)):
                        found_main = True
                        break
            results.append(("has_main_block", found_main))

    passed_count = sum(1 for _, ok in results if ok)
    total = len(results) if results else 1
    ratio = passed_count / total

    if ratio == 1.0:
        score = 2
    elif ratio >= 0.5:
        score = 1
    else:
        score = 0

    detail = "; ".join(f"{k}={'Y' if v else 'N'}" for k, v in results) or "no checks"
    return {
        "name": name, "type": "file_artifact", "score": score,
        "weight": metric.get("weight", 1.0),
        "method": "file_ast" if any(k in checks for k in ast_checks) else "file_exists",
        "detail": f"{detail} | size={size}B",
        "confidence": "high",
    }


# ═══════════════════════════════════════════════════════════════
# Scorer: shell_interaction
# ═══════════════════════════════════════════════════════════════

def score_shell_interaction(metric: dict, ctx: dict) -> dict:
    """Run test_command with optional stdin, match expected_output."""
    name = metric.get("name", "shell_interaction")
    cmd = metric.get("test_command", "")
    if not cmd:
        return _error_metric(name, "shell_interaction", metric, "no test_command")

    test_input = metric.get("test_input")
    stdin_data: str | None = None
    if test_input:
        # If it's a path that exists, read file content; else treat as literal stdin
        p = _resolve_path(test_input) if isinstance(test_input, str) else None
        if p and p.exists():
            stdin_data = p.read_text(encoding="utf-8")
        else:
            stdin_data = str(test_input)

    expected = metric.get("expected_output", "")
    match_mode = metric.get("match_mode", "contains")
    timeout = metric.get("timeout", 60)

    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=str(PROJECT_ROOT),
            env={**os.environ, "NO_COLOR": "1", "PYTHONUNBUFFERED": "1"},
            input=stdin_data,
        )
    except subprocess.TimeoutExpired:
        return {
            "name": name, "type": "shell_interaction", "score": 0,
            "weight": metric.get("weight", 1.0),
            "method": "shell_timeout",
            "detail": f"timed out after {timeout}s",
            "confidence": "high",
        }
    except Exception as e:
        return _error_metric(name, "shell_interaction", metric, str(e))

    combined = (proc.stdout or "") + (proc.stderr or "")
    ok = _match(expected, combined, match_mode) if expected else proc.returncode == 0

    if ok:
        score = 2
        detail = f"matched (mode={match_mode}) exit={proc.returncode}"
    elif proc.returncode == 0:
        score = 1
        detail = f"ran ok but output mismatch (mode={match_mode}) exit={proc.returncode}"
    else:
        score = 0
        detail = f"exit={proc.returncode} | output: {combined[-200:].strip()!r}"

    return {
        "name": name, "type": "shell_interaction", "score": score,
        "weight": metric.get("weight", 1.0),
        "method": "shell_run",
        "detail": detail,
        "confidence": "high",
    }


# ═══════════════════════════════════════════════════════════════
# Scorer: unit_test
# ═══════════════════════════════════════════════════════════════

def score_unit_test(metric: dict, ctx: dict) -> dict:
    """Run pytest, parse PASSED/FAILED counts.

    metric.test_command should be a pytest invocation.
    Score: 2 = all pass, 1 = pytest runs but some fail, 0 = pytest errors/no tests.
    """
    name = metric.get("name", "unit_test")
    cmd = metric.get("test_command", "")
    if not cmd:
        return _error_metric(name, "unit_test", metric, "no test_command")

    timeout = metric.get("timeout", 120)
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=str(PROJECT_ROOT),
            env={**os.environ, "NO_COLOR": "1", "PYTHONUNBUFFERED": "1"},
        )
    except subprocess.TimeoutExpired:
        return {
            "name": name, "type": "unit_test", "score": 0,
            "weight": metric.get("weight", 1.0),
            "method": "pytest_timeout",
            "detail": f"timed out after {timeout}s",
            "confidence": "high",
        }
    except Exception as e:
        return _error_metric(name, "unit_test", metric, str(e))

    out = (proc.stdout or "") + (proc.stderr or "")
    passed = re.findall(r"(\d+) passed", out)
    failed = re.findall(r"(\d+) failed", out)
    errors = re.findall(r"(\d+) error", out)
    n_pass = int(passed[0]) if passed else 0
    n_fail = int(failed[0]) if failed else 0
    n_err = int(errors[0]) if errors else 0

    if proc.returncode == 0 and n_pass > 0:
        score = 2
        detail = f"all passed: {n_pass}"
    elif n_pass > 0 and n_fail == 0 and n_err == 0:
        score = 1
        detail = f"pytest ran, {n_pass} passed (exit {proc.returncode})"
    elif n_fail > 0 or n_err > 0:
        # Has failures — partial if at least some passed
        score = 1 if n_pass > 0 else 0
        detail = f"{n_pass} passed / {n_fail} failed / {n_err} errors (exit {proc.returncode})"
    else:
        score = 0
        tail = out[-200:].replace("\n", " ")
        detail = f"no tests parsed, exit={proc.returncode} | tail: {tail}"

    return {
        "name": name, "type": "unit_test", "score": score,
        "weight": metric.get("weight", 1.0),
        "method": "pytest_run",
        "detail": detail,
        "confidence": "high",
    }


# ═══════════════════════════════════════════════════════════════
# Scorer: semantic (LLM judge, INDEPENDENT)
# ═══════════════════════════════════════════════════════════════

JUDGE_PROMPT_TEMPLATE = """You are an INDEPENDENT quality judge. Score the agent's work against the rubric below.

### Metric
{name}

### Rubric (select ONE score)
- 2: {r2}
- 1: {r1}
- 0: {r0}

### Evidence
{evidence}

### Instructions
- Output STRICT JSON only, no prose, no markdown fences.
- Schema: {{"score": <0|1|2>, "rationale": "<one short sentence>"}}
"""


def _build_evidence(metric: dict, ctx: dict) -> str:
    """Assemble evidence text for the judge from agent_output / file / both."""
    ji = metric.get("judge_input", {}) or {}
    source = ji.get("from", "agent_output")
    parts = []

    if source in ("agent_output", "both"):
        out = (ctx.get("output") or "")[:8000]
        parts.append(f"### Agent output (truncated to 8000 chars)\n{out}")

    if source in ("file", "both"):
        fpath = ji.get("file")
        if fpath:
            p = _resolve_path(fpath)
            if p.exists():
                try:
                    content = p.read_text(encoding="utf-8")[:8000]
                    parts.append(f"### File: {fpath} (truncated to 8000 chars)\n{content}")
                except Exception as e:
                    parts.append(f"### File: {fpath} (read error: {e})")
            else:
                parts.append(f"### File: {fpath} (NOT FOUND)")

    return "\n\n".join(parts) if parts else "(no evidence available)"


def _call_judge(prompt: str) -> dict | None:
    """One LLM judge call. Returns {score, rationale} or None on failure."""
    try:
        resp = client.messages.create(
            model=MODEL_ID,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = ""
        for block in resp.content:
            if hasattr(block, "text"):
                text += block.text
        text = text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        obj = json.loads(text)
        if isinstance(obj, dict) and "score" in obj:
            s = obj["score"]
            if s in (0, 1, 2):
                return {"score": int(s), "rationale": str(obj.get("rationale", ""))[:200]}
        return None
    except Exception:
        return None


def score_semantic_llm(metric: dict, ctx: dict) -> dict:
    """LLM-as-judge with rubric + 2x consistency check.

    Runs the judge TWICE; if scores disagree, marks confidence=low.
    """
    name = metric.get("name", "semantic")
    rubric = metric.get("rubric", {}) or {}
    r2 = rubric.get("2", "(fully met)")
    r1 = rubric.get("1", "(partially met)")
    r0 = rubric.get("0", "(not met)")
    evidence = _build_evidence(metric, ctx)

    prompt = JUDGE_PROMPT_TEMPLATE.format(
        name=name, r2=r2, r1=r1, r0=r0, evidence=evidence,
    )

    # First call
    j1 = _call_judge(prompt)
    if j1 is None:
        return _error_metric(name, "semantic", metric, "LLM judge call failed")

    # Second call for consistency
    j2 = _call_judge(prompt)
    if j2 is None:
        # Single-call fallback — mark low confidence
        return {
            "name": name, "type": "semantic", "score": j1["score"],
            "weight": metric.get("weight", 1.0),
            "method": "llm_judge",
            "detail": f"single call (consistency check skipped): {j1['rationale']}",
            "confidence": "low",
        }

    if j1["score"] == j2["score"]:
        return {
            "name": name, "type": "semantic", "score": j1["score"],
            "weight": metric.get("weight", 1.0),
            "method": "llm_judge",
            "detail": f"agreed x2: {j1['rationale']}",
            "confidence": "high",
        }

    # Disagreement — average and mark low confidence
    avg = (j1["score"] + j2["score"]) / 2
    score = 2 if avg >= 1.5 else (1 if avg >= 0.5 else 0)
    return {
        "name": name, "type": "semantic", "score": score,
        "weight": metric.get("weight", 1.0),
        "method": "llm_judge",
        "detail": f"disagreed ({j1['score']} vs {j2['score']}): {j1['rationale']} | {j2['rationale']}",
        "confidence": "low",
    }


# ═══════════════════════════════════════════════════════════════
# Dispatch + aggregation
# ═══════════════════════════════════════════════════════════════

def _error_metric(name: str, mtype: str, metric: dict, detail: str) -> dict:
    return {
        "name": name, "type": mtype, "score": 0,
        "weight": metric.get("weight", 1.0),
        "method": "error",
        "detail": detail,
        "confidence": "high",
    }


SCORERS = {
    "file_artifact": score_file_artifact,
    "shell_interaction": score_shell_interaction,
    "unit_test": score_unit_test,
    "semantic": score_semantic_llm,
}


def run_metric(metric: dict, ctx: dict) -> dict:
    """Dispatch a single metric to its scorer. ctx must contain 'output' (agent stdout)."""
    mtype = metric.get("type", "semantic")
    scorer = SCORERS.get(mtype)
    if scorer is None:
        return _error_metric(
            metric.get("name", "unknown"), mtype, metric,
            f"unknown metric type: {mtype}",
        )
    try:
        return scorer(metric, ctx)
    except Exception as e:
        return _error_metric(
            metric.get("name", "unknown"), mtype, metric,
            f"scorer exception: {e!r}",
        )


def aggregate_case_scores(metric_results: list[dict]) -> dict:
    """Aggregate per-metric scores into a case-level normalized score in [0,1].

    Returns:
      {
        "normalized": float in [0,1],
        "status": "passed" | "partial" | "failed",
        "total": int,
        "fully_passed": int,
        "low_confidence_count": int,
        "by_type": {type: {total, score_sum, max_score}},
      }
    """
    if not metric_results:
        return {
            "normalized": 0.0, "status": "failed", "total": 0,
            "fully_passed": 0, "low_confidence_count": 0, "by_type": {},
        }

    total_weight = 0.0
    weighted_score = 0.0
    fully_passed = 0
    low_conf = 0
    by_type: dict[str, dict] = {}

    for m in metric_results:
        w = float(m.get("weight", 1.0))
        s = int(m.get("score", 0))
        total_weight += w
        weighted_score += s * w
        if s == 2:
            fully_passed += 1
        if m.get("confidence") == "low":
            low_conf += 1

        t = m.get("type", "unknown")
        if t not in by_type:
            by_type[t] = {"total": 0, "score_sum": 0, "max_score": 0}
        by_type[t]["total"] += 1
        by_type[t]["score_sum"] += s
        by_type[t]["max_score"] += 2

    normalized = (weighted_score / (2 * total_weight)) if total_weight > 0 else 0.0

    if fully_passed == len(metric_results):
        status = "passed"
    elif fully_passed == 0:
        status = "failed"
    else:
        status = "partial"

    return {
        "normalized": round(normalized, 4),
        "status": status,
        "total": len(metric_results),
        "fully_passed": fully_passed,
        "low_confidence_count": low_conf,
        "by_type": by_type,
    }
