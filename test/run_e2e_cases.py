#!/usr/bin/env python3
"""E2E test runner — executes YAML test cases against the Penguin Coding Agent.

Usage:
    python test/run_e2e_cases.py [OPTIONS]

Options:
    --files FILE [FILE ...]   Only run specified YAML files
    --ids ID [ID ...]         Only run cases matching these IDs (prefix match)
    --category CAT            Only run cases in this category
    --difficulty DIFF         Only run cases at this difficulty
    --timeout SECONDS         Per-case timeout (default: 300)
    --output FILE             Report output path (default: TEST_REPORT.md)
    --dry-run                 Just list cases without executing
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

# Local imports — objective verifiers replace keyword matching
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifiers import (  # noqa: E402
    verify_case as objective_verify,
    summarize_methods,
)
from metric_scorer import (  # noqa: E402
    run_metric,
    aggregate_case_scores,
)

# ── Resolve paths ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = PROJECT_ROOT / "test" / "cases"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"


# ═══════════════════════════════════════════════════════════════
# Case loading
# ═══════════════════════════════════════════════════════════════

def load_all_cases() -> list[dict]:
    """Load all YAML test case files, return flat list of cases."""
    cases = []
    for f in sorted(CASES_DIR.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        for case in data:
            case["_source_file"] = f.name
            cases.append(case)
    return cases


def filter_cases(cases, *, files=None, ids=None, category=None, difficulty=None):
    """Apply filters to case list."""
    result = cases
    if files:
        file_set = set(files)
        result = [c for c in result if c["_source_file"] in file_set]
    if ids:
        result = [c for c in result if any(c["id"].startswith(i) for i in ids)]
    if category:
        result = [c for c in result if c.get("category") == category]
    if difficulty:
        result = [c for c in result if c.get("difficulty") == difficulty]
    return result


# ═══════════════════════════════════════════════════════════════
# Case execution
# ═══════════════════════════════════════════════════════════════

def run_case(case: dict, timeout: int = 300) -> dict:
    """Execute a single test case against the agent and return result dict."""
    case_id = case["id"]
    prompt = case["description"].strip()
    features = case.get("features", [])

    # Determine permission profile based on case category
    if "permission_strict" in features:
        perm_profile = "strict"
    elif "permission_permissive" in features or any(
        f.startswith("cli_") or f in ("session_autosave", "session_resume", "auto_compact", "manual_compact", "token_tracking", "context_compaction") for f in features
    ):
        perm_profile = "permissive"
    else:
        perm_profile = "permissive"

    # Build the command
    cmd = [
        sys.executable, "-m", "src",
        "--prompt", prompt,
        "--permissions", perm_profile,
    ]

    result = {
        "id": case_id,
        "name": case.get("name", ""),
        "category": case.get("category", ""),
        "difficulty": case.get("difficulty", ""),
        "features": features,
        "source_file": case.get("_source_file", ""),
        "permission_profile": perm_profile,
        "status": "pending",
        "output": "",
        "error": "",
        "duration_sec": 0,
        "verification": [],
        "tool_calls": [],
        "metric_results": [],
        "metric_score": None,
    }

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_ROOT),
            env={
                **os.environ,
                "PYTHONUNBUFFERED": "1",
                "NO_COLOR": "1",
            },
        )
        elapsed = time.time() - start
        result["duration_sec"] = round(elapsed, 1)
        result["output"] = proc.stdout
        result["error"] = proc.stderr

        if proc.returncode != 0:
            result["status"] = "error"
        else:
            result["status"] = "completed"

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        result["duration_sec"] = round(elapsed, 1)
        result["status"] = "timeout"
        result["error"] = f"Timed out after {timeout}s"
    except Exception as e:
        elapsed = time.time() - start
        result["duration_sec"] = round(elapsed, 1)
        result["status"] = "error"
        result["error"] = str(e)

    # Extract tool calls from output
    result["tool_calls"] = extract_tool_calls(result["output"])

    # Run objective verification checks
    result["verification"] = objective_verify(case, result)
    result["verification_summary"] = summarize_methods(result["verification"])

    # Run metric-based scoring (if case declares metrics)
    metrics = case.get("metrics", [])
    if metrics:
        ctx = {"output": result.get("output", ""), "case": case}
        metric_results = [run_metric(m, ctx) for m in metrics]
        result["metric_results"] = metric_results
        result["metric_score"] = aggregate_case_scores(metric_results)

    # Determine final pass/fail
    verifications = result["verification"]
    metric_agg = result.get("metric_score")

    if result["status"] == "timeout":
        result["status"] = "timeout"
    elif result["status"] == "error" and not result["output"]:
        result["status"] = "error"
    elif metric_agg:
        # Metric-driven status takes precedence when metrics are declared
        result["status"] = metric_agg["status"]
    elif all(v["passed"] for v in verifications):
        result["status"] = "passed"
    elif any(v["passed"] for v in verifications):
        result["status"] = "partial"
    else:
        result["status"] = "failed"

    return result


def extract_tool_calls(output: str) -> list[str]:
    """Extract tool names used from agent output."""
    tools = []
    # Match patterns like: "Using tool: read_file" or "[read_file]" or tool_use blocks
    patterns = [
        r"tool['\"_]?\s*(?:call|use|name)?[:\s]+['\"]?(\w+)['\"]?",
        r"\[(\w+_file|\w+_command|\w+_directory|\w+_files|task|delegate|team_\w+|background_\w+|check_\w+|load_skill)\]",
        r"Executing (\w+)",
    ]
    seen = set()
    # More reliable: look for the tool execution markers in the CLI output
    tool_marker_pattern = re.compile(r"┃\s*(\w+)\s*│|Tool:\s*(\w+)|running\s+(\w+)", re.IGNORECASE)
    for m in tool_marker_pattern.finditer(output):
        name = m.group(1) or m.group(2) or m.group(3)
        if name and name not in seen:
            seen.add(name)
            tools.append(name)

    # Also check for tool names in structured output
    for tool_name in [
        "read_file", "write_file", "edit_file", "run_command",
        "search_files", "list_directory", "task",
        "team_spawn", "team_send", "team_broadcast", "team_list", "team_shutdown",
        "delegate", "load_skill", "background_run", "check_background",
    ]:
        if tool_name in output and tool_name not in seen:
            seen.add(tool_name)
            tools.append(tool_name)

    return tools


def verify_case(case: dict, result: dict) -> list[dict]:
    """DEPRECATED stub — kept for backward compat. Now uses objective verifiers."""
    return objective_verify(case, result)


# ═══════════════════════════════════════════════════════════════
# Report generation
# ═══════════════════════════════════════════════════════════════

STATUS_EMOJI = {
    "passed": "PASS",
    "partial": "PARTIAL",
    "failed": "FAIL",
    "timeout": "TIMEOUT",
    "error": "ERROR",
    "completed": "DONE",
}


def generate_report(results: list[dict], output_path: Path):
    """Generate a Markdown test report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Stats
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] == "failed")
    timeout = sum(1 for r in results if r["status"] == "timeout")
    error = sum(1 for r in results if r["status"] == "error")
    total_duration = sum(r["duration_sec"] for r in results)

    lines = []
    lines.append("# Penguin Coding Agent — E2E 测试报告")
    lines.append("")
    lines.append(f"测试时间：{now}")
    lines.append(f"测试模式：--prompt 一次性模式 + --permissions permissive")
    lines.append(f"总耗时：{total_duration:.1f}s")
    lines.append("")

    # Summary table
    lines.append("## 总览")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 总案例数 | {total} |")
    lines.append(f"| PASS | {passed} |")
    lines.append(f"| PARTIAL | {partial} |")
    lines.append(f"| FAIL | {failed} |")
    lines.append(f"| TIMEOUT | {timeout} |")
    lines.append(f"| ERROR | {error} |")
    pass_rate = ((passed + partial * 0.5) / total * 100) if total else 0
    lines.append(f"| 通过率 | {pass_rate:.0f}% |")
    lines.append("")

    # Verification method breakdown
    obj_total = sum(r.get("verification_summary", {}).get("objective", {}).get("total", 0) for r in results)
    obj_passed = sum(r.get("verification_summary", {}).get("objective", {}).get("passed", 0) for r in results)
    weak_total = sum(r.get("verification_summary", {}).get("weak", {}).get("total", 0) for r in results)
    weak_passed = sum(r.get("verification_summary", {}).get("weak", {}).get("passed", 0) for r in results)
    lines.append("## 验证方法分布")
    lines.append("")
    lines.append("| 验证类型 | 总数 | 通过 | 通过率 | 说明 |")
    lines.append("|---------|------|------|--------|------|")
    obj_rate = (obj_passed / obj_total * 100) if obj_total else 0
    weak_rate = (weak_passed / weak_total * 100) if weak_total else 0
    lines.append(f"| 客观验证 | {obj_total} | {obj_passed} | {obj_rate:.0f}% | 文件系统/AST/子进程/记忆库/任务库 |")
    lines.append(f"| 弱验证 | {weak_total} | {weak_passed} | {weak_rate:.0f}% | 输出关键词匹配（仅用于纯文本输出） |")
    lines.append("")

    # Category breakdown
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "partial": 0, "failed": 0, "timeout": 0, "error": 0}
        categories[cat]["total"] += 1
        categories[cat][r["status"]] += 1

    lines.append("## 按分类统计")
    lines.append("")
    lines.append("| 分类 | 总数 | PASS | PARTIAL | FAIL | TIMEOUT | ERROR |")
    lines.append("|------|------|------|---------|------|---------|-------|")
    for cat, stats in categories.items():
        lines.append(f"| {cat} | {stats['total']} | {stats['passed']} | {stats['partial']} | {stats['failed']} | {stats['timeout']} | {stats['error']} |")
    lines.append("")

    # Feature coverage
    all_features = set()
    covered_features = set()
    for r in results:
        for f in r.get("features", []):
            all_features.add(f)
            if r["status"] in ("passed", "partial"):
                covered_features.add(f)

    lines.append("## 功能覆盖")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 总功能数 | {len(all_features)} |")
    lines.append(f"| 已覆盖 | {len(covered_features)} |")
    lines.append(f"| 覆盖率 | {len(covered_features)/len(all_features)*100:.0f}% |" if all_features else "| 覆盖率 | N/A |")
    uncovered = all_features - covered_features
    if uncovered:
        lines.append("")
        lines.append("未覆盖功能：")
        for f in sorted(uncovered):
            lines.append(f"- {f}")
    lines.append("")

    # Detailed results
    lines.append("## 详细结果")
    lines.append("")

    for r in results:
        status = STATUS_EMOJI.get(r["status"], r["status"].upper())
        lines.append(f"### {r['id']} — {r['name']} [{status}]")
        lines.append("")
        lines.append(f"- 分类: {r['category']}")
        lines.append(f"- 难度: {r['difficulty']}")
        lines.append(f"- 权限模式: {r['permission_profile']}")
        lines.append(f"- 耗时: {r['duration_sec']}s")
        lines.append(f"- 功能: {', '.join(r['features'])}")
        if r["tool_calls"]:
            lines.append(f"- 工具调用: {', '.join(r['tool_calls'])}")
        lines.append("")

        # Verification results
        if r["verification"]:
            passed_v = sum(1 for v in r["verification"] if v["passed"])
            total_v = len(r["verification"])
            lines.append(f"验证项 ({passed_v}/{total_v} 通过)：")
            for v in r["verification"]:
                mark = "V" if v["passed"] else "X"
                method = v.get("method", "")
                weak_tag = " [弱]" if method in ("output_keyword", "tool_used") else ""
                lines.append(f"- [{mark}]{weak_tag} {v['check']}")
                if v.get("detail"):
                    lines.append(f"  > [{method}] {v['detail']}")
            lines.append("")

        # Error info
        if r["status"] in ("error", "timeout") and r["error"]:
            lines.append(f"错误信息：`{r['error'][:200]}`")
            lines.append("")

        # Output excerpt
        if r["output"]:
            excerpt = r["output"][:500].replace("\n", " ").strip()
            lines.append(f"输出摘要：{excerpt}...")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Write report
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {output_path}")


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="E2E test runner for Penguin Coding Agent")
    parser.add_argument("--files", nargs="+", default=None, help="Only run specified YAML files")
    parser.add_argument("--ids", nargs="+", default=None, help="Only run cases matching these IDs")
    parser.add_argument("--category", default=None, help="Only run cases in this category")
    parser.add_argument("--difficulty", default=None, help="Only run cases at this difficulty")
    parser.add_argument("--timeout", type=int, default=300, help="Per-case timeout in seconds")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "TEST_REPORT.md"), help="Report output path")
    parser.add_argument("--dry-run", action="store_true", help="Just list cases without executing")
    args = parser.parse_args()

    # Load cases
    cases = load_all_cases()
    cases = filter_cases(cases, files=args.files, ids=args.ids, category=args.category, difficulty=args.difficulty)

    if not cases:
        print("No test cases match the given filters.")
        sys.exit(1)

    print(f"Found {len(cases)} test cases")

    if args.dry_run:
        for c in cases:
            print(f"  {c['id']:12s} {c.get('difficulty', '?'):8s} {c.get('name', '')}")
        sys.exit(0)

    # Execute cases
    results = []
    for i, case in enumerate(cases, 1):
        cid = case["id"]
        name = case.get("name", "")
        print(f"\n[{i}/{len(cases)}] {cid} — {name}")
        print(f"  Features: {', '.join(case.get('features', []))}")

        result = run_case(case, timeout=args.timeout)
        results.append(result)

        status = STATUS_EMOJI.get(result["status"], result["status"].upper())
        print(f"  -> {status} ({result['duration_sec']}s)")
        if result["tool_calls"]:
            print(f"     Tools: {', '.join(result['tool_calls'])}")

        # Save intermediate results
        json_path = Path(args.output).with_suffix(".json")
        json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Generate report
    generate_report(results, Path(args.output))

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] == "failed")
    timeout_n = sum(1 for r in results if r["status"] == "timeout")
    error_n = sum(1 for r in results if r["status"] == "error")

    print(f"\n{'='*60}")
    print(f"RESULTS: {total} cases | {passed} PASS | {partial} PARTIAL | {failed} FAIL | {timeout_n} TIMEOUT | {error_n} ERROR")
    if failed + timeout_n + error_n == 0:
        print("ALL CASES PASSED OR PARTIALLY PASSED!")
    else:
        print("Some cases need attention.")
    print(f"Report: {args.output}")


if __name__ == "__main__":
    main()
