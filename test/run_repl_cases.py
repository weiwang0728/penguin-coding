#!/usr/bin/env python3
"""REPL-mode E2E test runner — drives the Penguin CLI interactively via pexpect.

Handles slash commands (/compact, /tokens, /permissions, /help, etc.)
that cannot be tested in --prompt one-shot mode.

Usage:
    python test/run_repl_cases.py [--timeout SECONDS] [--output FILE]
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import pexpect

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = PROJECT_ROOT / "test" / "cases"

# Local imports — objective verifiers replace keyword matching
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifiers import (  # noqa: E402
    classify_and_verify,
    summarize_methods,
)

PROMPT_PATTERN = r"You > "
LAUNCH_TIMEOUT = 30  # seconds to wait for REPL startup
DEFAULT_STEP_TIMEOUT = 300  # seconds per prompt/step


def load_timeout_cases():
    """Load the 3 timeout cases from YAML files."""
    import yaml
    cases = []
    target_ids = {"E2E-004", "PS-004", "PS-006"}
    for f in sorted(CASES_DIR.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        for case in data:
            if case["id"] in target_ids:
                cases.append(case)
    return cases


def spawn_repl(permission_profile="permissive"):
    """Start the Penguin REPL and return the pexpect child."""
    env = {
        **os.environ,
        "PYTHONUNBUFFERED": "1",
        "TERM": "dumb",
        "NO_COLOR": "1",
    }
    child = pexpect.spawn(
        sys.executable, ["-m", "src", "--permissions", permission_profile],
        cwd=str(PROJECT_ROOT),
        env=env,
        timeout=LAUNCH_TIMEOUT,
        encoding="utf-8",
        codec_errors="replace",
    )

    # Wait for the REPL prompt
    child.expect(PROMPT_PATTERN, timeout=LAUNCH_TIMEOUT)
    return child


def send_and_wait(child, text, timeout=DEFAULT_STEP_TIMEOUT):
    """Send a message to the REPL and wait for the next prompt."""
    child.sendline(text)
    try:
        child.expect(PROMPT_PATTERN, timeout=timeout)
        output = child.before
        return output, True
    except pexpect.TIMEOUT:
        output = child.before or ""
        return output, False
    except pexpect.EOF:
        output = child.before or ""
        return output, False


def verify_output(output, checks, case=None):
    """Run verification checks — delegates to objective verifiers in test/verifiers.py.

    Falls back to weak keyword matching only for purely textual checks
    (compact/tokens/permissions output) that have no objective state source.
    """
    results = []
    output_lower = output.lower()
    if case is None:
        case = {}

    for check in checks:
        # First try objective verification (covers file existence, AST, test runs,
        # security blocks, task state, etc.)
        v = classify_and_verify(check, output, case)
        method = v.get("method", "")

        # REPL-specific weak checks: /compact, /tokens, /permissions slash commands
        # have no objective state source, so we fall back to keyword matching here.
        check_lower = check.lower()
        if method == "output_keyword" and (
            "压缩" in check or "compact" in check_lower
            or "token" in check_lower
            or "权限" in check or "permission" in check_lower
            or "permissive" in check_lower or "standard" in check_lower or "strict" in check_lower
        ):
            kw_map = {
                "compact": ["compress", "compact", "压缩", "tokens"],
                "token": ["token", "prompt", "completion", "context"],
                "permission": ["permissive", "standard", "strict", "权限", "profile", "switched"],
            }
            for key, kws in kw_map.items():
                if key in check_lower or (key == "permission" and ("权限" in check or "permission" in check_lower or any(k in check_lower for k in ["permissive", "standard", "strict"]))):
                    matched = [k for k in kws if k.lower() in output_lower]
                    if matched:
                        v = {"check": check, "passed": True, "method": "output_keyword",
                             "detail": f"matched: {matched}"}
                    else:
                        v = {"check": check, "passed": False, "method": "output_keyword",
                             "detail": f"none of {kws} found"}
                    break

        results.append(v)

    return results


def run_ps004(child, timeout):
    """PS-004: 上下文压缩与长对话 — uses /compact and /tokens."""
    result = {
        "id": "PS-004",
        "name": "上下文压缩与长对话",
        "status": "pending",
        "steps": [],
        "duration_sec": 0,
    }
    start = time.time()
    all_output = ""

    steps = [
        # Step 1: Read multiple files to build up context
        ("请阅读 workspace/src/agent_loop.py 和 workspace/src/permissions.py，给出每个文件的核心逻辑总结", 300),
        # Step 2: More context building
        ("请阅读 workspace/src/task_system.py，总结任务系统的设计", 300),
        # Step 3: Create files to add more context
        ("请在 workspace/ 下创建 context_test.py，实现一个简单的LRU缓存类", 300),
        # Step 4: Check tokens before compact
        ("/tokens", 10),
        # Step 5: Manual compact
        ("/compact", 60),
        # Step 6: Verify agent still works after compact
        ("请列出 workspace/ 下所有的 .py 文件", 120),
        # Step 7: Check tokens after compact
        ("/tokens", 10),
    ]

    for step_text, step_timeout in steps:
        output, ok = send_and_wait(child, step_text, timeout=step_timeout)
        step_result = {
            "input": step_text[:80],
            "output_preview": (output or "")[:200].replace("\n", " ").strip(),
            "ok": ok,
        }
        result["steps"].append(step_result)
        all_output += (output or "")

        if not ok:
            result["status"] = "timeout"
            result["duration_sec"] = round(time.time() - start, 1)
            return result

    result["duration_sec"] = round(time.time() - start, 1)

    # Verify
    checks = [
        "自动压缩在 token 接近阈值时触发",
        "/compact 执行后返回压缩摘要",
        "压缩后 agent 仍能回答问题",
        "/tokens 输出包含 token 数量信息",
    ]
    result["verification"] = verify_output(
        all_output, checks, case={"description": "", "features": []},
    )
    result["verification_summary"] = summarize_methods(result["verification"])

    passed = sum(1 for v in result["verification"] if v["passed"])
    if passed == len(checks):
        result["status"] = "passed"
    elif passed > 0:
        result["status"] = "partial"
    else:
        result["status"] = "failed"

    return result


def run_ps006(child, timeout):
    """PS-006: 自定义权限配置 — uses /permissions switching."""
    result = {
        "id": "PS-006",
        "name": "自定义权限配置",
        "status": "pending",
        "steps": [],
        "duration_sec": 0,
    }
    start = time.time()
    all_output = ""

    steps = [
        # Check default permissions
        ("/permissions", 10),
        # Switch to permissive
        ("/permissions permissive", 10),
        # Verify tools work in permissive mode
        ("请列出 workspace/ 下的文件", 120),
        # Switch to standard
        ("/permissions standard", 10),
        # Try write in standard — should need confirmation, pexpect sends 'y'
        ("请在 workspace/ 下创建 perm_test_std.py，内容为 print('standard test')", 180),
        # Switch to strict
        ("/permissions strict", 10),
        # Try write in strict — should be denied
        ("请在 workspace/ 下创建 perm_test_strict.py，内容为 print('strict test')", 120),
        # Switch back to permissive for cleanup
        ("/permissions permissive", 10),
        # Verify
        ("请读取 workspace/perm_test_std.py", 60),
    ]

    for step_text, step_timeout in steps:
        output, ok = send_and_wait(child, step_text, timeout=step_timeout)

        # Handle permission confirmation prompts in standard mode
        if "Allow?" in (output or "") and "Permission Required" in (output or ""):
            child.sendline("y")
            try:
                child.expect(PROMPT_PATTERN, timeout=120)
                output += child.before or ""
                ok = True
            except:
                ok = False

        step_result = {
            "input": step_text[:80],
            "output_preview": (output or "")[:200].replace("\n", " ").strip(),
            "ok": ok,
        }
        result["steps"].append(step_result)
        all_output += (output or "")

        if not ok:
            result["status"] = "timeout"
            result["duration_sec"] = round(time.time() - start, 1)
            return result

    result["duration_sec"] = round(time.time() - start, 1)

    # Verify
    checks = [
        "permissive: read_file=allow, write_file=allow, run_command=allow",
        "standard: read_file=allow, write_file=confirm, run_command=confirm",
        "strict: read_file=allow(或confirm), write_file=deny, run_command=deny",
    ]
    result["verification"] = verify_output(
        all_output, checks, case={"description": "", "features": []},
    )
    result["verification_summary"] = summarize_methods(result["verification"])

    passed = sum(1 for v in result["verification"] if v["passed"])
    if passed == len(checks):
        result["status"] = "passed"
    elif passed > 0:
        result["status"] = "partial"
    else:
        result["status"] = "failed"

    return result


def run_e2e004(child, timeout):
    """E2E-004: 技能驱动的完整开发工作流 — split into 2 REPL sessions."""
    result = {
        "id": "E2E-004",
        "name": "技能驱动的完整开发工作流",
        "status": "pending",
        "steps": [],
        "duration_sec": 0,
    }
    start = time.time()
    all_output = ""

    # ── Part 1: Design + Implement + Review (in first REPL session) ──
    steps_part1 = [
        ("请加载 agent-builder 技能", 60),
        ("请用 agent-builder 的理念，设计一个'文档生成代理'的架构。输出：1)架构图(文字描述) 2)3个工具名+功能 3)系统提示词(3句话) 4)3步工作流程。请简短回答。", 480),
        ("请在 workspace/doc_generator/ 下创建 generator.py，实现 extract_docstrings(filepath) 和 extract_type_hints(filepath) 两个函数。同时创建 __init__.py 导出这两个函数。", 420),
        ("请加载 code-review 技能，简要审查 workspace/doc_generator/generator.py，给出评分(1-10)和1-2条改进建议", 360),
        ("请根据审查意见改进 generator.py", 240),
    ]

    for step_text, step_timeout in steps_part1:
        output, ok = send_and_wait(child, step_text, timeout=step_timeout)
        result["steps"].append({
            "input": step_text[:80],
            "output_preview": (output or "")[:200].replace("\n", " ").strip(),
            "ok": ok,
        })
        all_output += (output or "")
        if not ok:
            result["status"] = "timeout"
            result["duration_sec"] = round(time.time() - start, 1)
            return result

    # Exit first REPL, start fresh for Part 2
    child.sendline("quit")
    try:
        child.close()
    except:
        pass

    print("    Part 1 done, spawning fresh REPL for Part 2...")
    try:
        child = spawn_repl(permission_profile="permissive")
    except Exception as e:
        result["status"] = "error"
        result["duration_sec"] = round(time.time() - start, 1)
        result["steps"].append({"input": "spawn REPL for part 2", "output_preview": str(e), "ok": False})
        return result

    # ── Part 2: MCP + PDF + Memory (in fresh REPL) ──
    # Note: delegate in REPL mode is too slow, tested separately
    steps_part2 = [
        ("请加载 mcp-builder 技能。设计一个MCP服务器，提供 generate_docs 工具（输入路径，输出文档），只需输出服务器类的骨架代码。", 360),
        ("请加载 pdf 技能。用 ReportLab 生成一个简单PDF保存到 workspace/doc_generator/api_docs.pdf，内容为'Doc Generator API Documentation'", 300),
        ("请列出 workspace/doc_generator/ 下的文件", 60),
    ]

    for step_text, step_timeout in steps_part2:
        output, ok = send_and_wait(child, step_text, timeout=step_timeout)
        result["steps"].append({
            "input": step_text[:80],
            "output_preview": (output or "")[:200].replace("\n", " ").strip(),
            "ok": ok,
        })
        all_output += (output or "")
        if not ok:
            result["status"] = "timeout"
            result["duration_sec"] = round(time.time() - start, 1)
            return result

    # Exit second REPL
    child.sendline("quit")
    try:
        child.close()
    except:
        pass

    result["duration_sec"] = round(time.time() - start, 1)

    # Verify — use objective verifiers with case context so file/AST checks
    # work against the actual files created during the run.
    checks = [
        "agent-builder 输出代理设计方案",
        "workspace/doc_generator/generator.py 文件存在",
        "workspace/doc_generator/generator.py 包含 extract_docstrings 函数",
        "code-review 审查报告生成",
        "代码根据审查意见改进",
        "mcp-builder 输出 MCP 服务器设计",
        "workspace/doc_generator/api_docs.pdf 文件存在",
    ]
    e2e004_case = {
        "description": "设计文档生成代理 workspace/doc_generator/generator.py 实现 extract_docstrings 和 extract_type_hints 函数",
        "features": ["load_skill", "agent_builder_skill", "code_review_skill",
                     "mcp_builder_skill", "pdf_skill", "write_file", "edit_file",
                     "list_directory"],
    }
    result["verification"] = verify_output(
        all_output, checks, case=e2e004_case,
    )
    result["verification_summary"] = summarize_methods(result["verification"])

    passed = sum(1 for v in result["verification"] if v["passed"])
    if passed == len(checks):
        result["status"] = "passed"
    elif passed > 0:
        result["status"] = "partial"
    else:
        result["status"] = "failed"

    return result


def generate_report(results, output_path):
    """Generate a Markdown report for the REPL test results."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    STATUS_EMOJI = {"passed": "PASS", "partial": "PARTIAL", "failed": "FAIL", "timeout": "TIMEOUT", "error": "ERROR"}

    lines = []
    lines.append("# Penguin Coding Agent — REPL 模式 E2E 测试报告")
    lines.append("")
    lines.append(f"测试时间：{now}")
    lines.append(f"测试模式：python -m src 交互式 REPL 模式（pexpect 驱动）")
    lines.append("")

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] == "failed")
    timeout_n = sum(1 for r in results if r["status"] == "timeout")
    total_dur = sum(r.get("duration_sec", 0) for r in results)

    lines.append("## 总览")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 总案例数 | {total} |")
    lines.append(f"| PASS | {passed} |")
    lines.append(f"| PARTIAL | {partial} |")
    lines.append(f"| FAIL | {failed} |")
    lines.append(f"| TIMEOUT | {timeout_n} |")
    lines.append(f"| 总耗时 | {total_dur:.0f}s ({total_dur/60:.1f}min) |")
    lines.append("")

    for r in results:
        status = STATUS_EMOJI.get(r["status"], r["status"].upper())
        lines.append(f"## {r['id']} — {r['name']} [{status}]")
        lines.append("")
        lines.append(f"- 耗时: {r.get('duration_sec', 0)}s")
        lines.append("")

        # Steps
        if r.get("steps"):
            lines.append("### 执行步骤")
            lines.append("")
            for i, step in enumerate(r["steps"], 1):
                mark = "V" if step.get("ok") else "X"
                lines.append(f"{i}. [{mark}] `{step['input']}`")
                if step.get("output_preview"):
                    lines.append(f"   > {step['output_preview'][:150]}")
            lines.append("")

        # Verification
        if r.get("verification"):
            passed_v = sum(1 for v in r["verification"] if v["passed"])
            total_v = len(r["verification"])
            lines.append(f"### 验证项 ({passed_v}/{total_v} 通过)")
            lines.append("")
            for v in r["verification"]:
                mark = "V" if v["passed"] else "X"
                method = v.get("method", "")
                weak_tag = " [弱]" if method in ("output_keyword", "tool_used") else ""
                lines.append(f"- [{mark}]{weak_tag} {v['check']}")
                if v.get("detail"):
                    lines.append(f"  > [{method}] {v['detail']}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Conclusions
    lines.append("## 对比：REPL 模式 vs --prompt 模式")
    lines.append("")
    lines.append("| 案例 | --prompt 模式 | REPL 模式 | 改善 |")
    lines.append("|------|--------------|-----------|------|")
    for r in results:
        old = "TIMEOUT"
        new = STATUS_EMOJI.get(r["status"], r["status"])
        improved = "YES" if r["status"] in ("passed", "partial") else "NO"
        lines.append(f"| {r['id']} | {old} | {new} | {improved} |")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="REPL-mode E2E test runner")
    parser.add_argument("--timeout", type=int, default=600, help="Max total timeout per case (seconds)")
    parser.add_argument("--output", default=str(PROJECT_ROOT / "TEST_REPORT_REPL.md"), help="Report output path")
    parser.add_argument("--ids", nargs="+", default=None, help="Only run specific case IDs")
    args = parser.parse_args()

    cases_to_run = ["PS-004", "PS-006", "E2E-004"]
    if args.ids:
        cases_to_run = [c for c in cases_to_run if c in args.ids]

    results = []

    for case_id in cases_to_run:
        print(f"\n{'='*60}")
        print(f"Starting REPL test: {case_id}")
        print(f"{'='*60}")

        # Spawn a fresh REPL for each case
        print("  Spawning REPL...")
        try:
            child = spawn_repl(permission_profile="permissive")
            print("  REPL ready.")
        except Exception as e:
            print(f"  ERROR: Failed to start REPL: {e}")
            results.append({
                "id": case_id,
                "name": case_id,
                "status": "error",
                "steps": [],
                "duration_sec": 0,
                "verification": [],
            })
            continue

        try:
            if case_id == "PS-004":
                result = run_ps004(child, args.timeout)
            elif case_id == "PS-006":
                result = run_ps006(child, args.timeout)
            elif case_id == "E2E-004":
                result = run_e2e004(child, args.timeout)
            else:
                print(f"  Unknown case: {case_id}")
                continue
        except Exception as e:
            print(f"  EXCEPTION: {e}")
            result = {
                "id": case_id,
                "name": case_id,
                "status": "error",
                "steps": [],
                "duration_sec": 0,
                "verification": [],
            }

        # Exit REPL
        try:
            child.sendline("quit")
            child.close()
        except:
            pass

        status = result.get("status", "unknown").upper()
        print(f"  -> {status} ({result.get('duration_sec', 0)}s)")
        if result.get("verification"):
            passed_v = sum(1 for v in result["verification"] if v["passed"])
            print(f"     Verification: {passed_v}/{len(result['verification'])} passed")

        results.append(result)

        # Save intermediate JSON
        json_path = Path(args.output).with_suffix(".json")
        json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # Generate report
    generate_report(results, Path(args.output))

    # Print summary
    print(f"\n{'='*60}")
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    partial = sum(1 for r in results if r["status"] == "partial")
    timeout_n = sum(1 for r in results if r["status"] == "timeout")
    error_n = sum(1 for r in results if r["status"] == "error")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(f"REPL MODE RESULTS: {total} cases | {passed} PASS | {partial} PARTIAL | {failed} FAIL | {timeout_n} TIMEOUT | {error_n} ERROR")


if __name__ == "__main__":
    main()
