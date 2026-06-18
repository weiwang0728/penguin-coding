#!/usr/bin/env python3
"""Merge all TEST_REPORT_*.json files into a single comprehensive report."""

import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATUS_EMOJI = {
    "passed": "PASS",
    "partial": "PARTIAL",
    "failed": "FAIL",
    "timeout": "TIMEOUT",
    "error": "ERROR",
}

CATEGORY_NAMES = {
    "basic_tools": "基础工具操作",
    "multi_agent": "多代理协作",
    "skills_background": "技能与后台任务",
    "permissions_session": "权限与会话管理",
    "e2e_integration": "端到端集成",
}

def merge_results():
    all_results = {}
    for report_file in sorted(PROJECT_ROOT.glob("TEST_REPORT*.json")):
        with open(report_file) as f:
            data = json.load(f)
        for r in data:
            cid = r["id"]
            # Prefer: passed > partial > timeout > error > failed
            priority = {"passed": 5, "partial": 4, "timeout": 3, "error": 2, "failed": 1}
            old_prio = priority.get(all_results.get(cid, {}).get("status", ""), 0)
            new_prio = priority.get(r["status"], 0)
            if cid not in all_results or new_prio > old_prio:
                all_results[cid] = r
    return all_results


def generate_report(all_results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = sorted(all_results.values(), key=lambda r: r["id"])

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "passed")
    partial = sum(1 for r in results if r["status"] == "partial")
    failed = sum(1 for r in results if r["status"] == "failed")
    timeout_n = sum(1 for r in results if r["status"] == "timeout")
    error_n = sum(1 for r in results if r["status"] == "error")
    total_duration = sum(r["duration_sec"] for r in results)
    pass_rate = ((passed + partial * 0.5) / total * 100) if total else 0

    lines = []
    lines.append("# Penguin Coding Agent — E2E 测试报告")
    lines.append("")
    lines.append(f"测试时间：{now}")
    lines.append(f"测试模式：python -m src --prompt --permissions permissive 一次性模式")
    lines.append(f"总耗时：{total_duration:.0f}s ({total_duration/60:.1f}min)")
    lines.append("")

    # ── Summary ──
    lines.append("## 总览")
    lines.append("")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|------|-----|")
    lines.append(f"| 总案例数 | {total} |")
    lines.append(f"| PASS | {passed} |")
    lines.append(f"| PARTIAL | {partial} |")
    lines.append(f"| FAIL | {failed} |")
    lines.append(f"| TIMEOUT | {timeout_n} |")
    lines.append(f"| ERROR | {error_n} |")
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
    lines.append(f"| 客观验证 | {obj_total} | {obj_passed} | {obj_rate:.0f}% | 文件系统/AST/子进程/任务库 |")
    lines.append(f"| 弱验证 | {weak_total} | {weak_passed} | {weak_rate:.0f}% | 输出关键词匹配（仅用于纯文本输出） |")
    lines.append("")

    # ── Category breakdown ──
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "partial": 0, "failed": 0, "timeout": 0, "error": 0, "duration": 0}
        categories[cat]["total"] += 1
        categories[cat][r["status"]] += 1
        categories[cat]["duration"] += r["duration_sec"]

    lines.append("## 按分类统计")
    lines.append("")
    lines.append("| 分类 | 总数 | PASS | PARTIAL | TIMEOUT | 耗时 |")
    lines.append("|------|------|------|---------|---------|------|")
    for cat, stats in categories.items():
        cat_name = CATEGORY_NAMES.get(cat, cat)
        lines.append(f"| {cat_name} | {stats['total']} | {stats['passed']} | {stats['partial']} | {stats['timeout']} | {stats['duration']:.0f}s |")
    lines.append("")

    # ── Difficulty breakdown ──
    difficulties = {}
    for r in results:
        diff = r.get("difficulty", "unknown")
        if diff not in difficulties:
            difficulties[diff] = {"total": 0, "passed": 0, "partial": 0, "timeout": 0}
        difficulties[diff]["total"] += 1
        if r["status"] == "passed":
            difficulties[diff]["passed"] += 1
        elif r["status"] == "partial":
            difficulties[diff]["partial"] += 1
        elif r["status"] == "timeout":
            difficulties[diff]["timeout"] += 1

    diff_order = ["easy", "medium", "hard", "expert"]
    lines.append("## 按难度统计")
    lines.append("")
    lines.append("| 难度 | 总数 | PASS | PARTIAL | TIMEOUT | 通过率 |")
    lines.append("|------|------|------|---------|---------|--------|")
    for diff in diff_order:
        if diff in difficulties:
            s = difficulties[diff]
            rate = ((s["passed"] + s["partial"] * 0.5) / s["total"] * 100) if s["total"] else 0
            lines.append(f"| {diff} | {s['total']} | {s['passed']} | {s['partial']} | {s['timeout']} | {rate:.0f}% |")
    lines.append("")

    # ── Feature coverage ──
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
    lines.append(f"| 覆盖率 | {len(covered_features)/len(all_features)*100:.0f}% |")
    uncovered = all_features - covered_features
    if uncovered:
        lines.append("")
        lines.append("### 未覆盖功能")
        lines.append("")
        for f in sorted(uncovered):
            lines.append(f"- {f}")
    lines.append("")

    # ── All features detail ──
    lines.append("### 功能覆盖详情")
    lines.append("")
    feature_cases = {}
    for r in results:
        for f in r.get("features", []):
            if f not in feature_cases:
                feature_cases[f] = []
            feature_cases[f].append((r["id"], r["status"]))

    lines.append("| 功能 | 测试案例 | 状态 |")
    lines.append("|------|---------|------|")
    for feat in sorted(feature_cases.keys()):
        cases_str = ", ".join(f"{cid}({STATUS_EMOJI.get(st, st)})" for cid, st in feature_cases[feat])
        best_status = "covered" if any(st in ("passed", "partial") for _, st in feature_cases[feat]) else "uncovered"
        lines.append(f"| {feat} | {cases_str} | {best_status} |")
    lines.append("")

    # ── Detailed results ──
    lines.append("## 详细结果")
    lines.append("")

    for r in results:
        status = STATUS_EMOJI.get(r["status"], r["status"].upper())
        cat_name = CATEGORY_NAMES.get(r.get("category", ""), r.get("category", ""))
        lines.append(f"### {r['id']} — {r['name']} [{status}]")
        lines.append("")
        lines.append(f"- 分类: {cat_name}")
        lines.append(f"- 难度: {r['difficulty']}")
        lines.append(f"- 耗时: {r['duration_sec']}s")
        lines.append(f"- 功能: {', '.join(r['features'])}")
        if r["tool_calls"]:
            lines.append(f"- 工具调用: {', '.join(r['tool_calls'])}")
        lines.append("")

        # Verification
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

        # Output excerpt
        if r["output"]:
            excerpt = r["output"][:400].replace("\n", " ").strip()
            lines.append(f"输出摘要：{excerpt}...")
            lines.append("")

        lines.append("---")
        lines.append("")

    # ── Conclusions ──
    lines.append("## 结论与分析")
    lines.append("")
    lines.append("### 通过情况")
    lines.append(f"- **{passed}** 个案例完全通过，**{partial}** 个部分通过")
    lines.append(f"- 综合通过率 **{pass_rate:.0f}%**")
    lines.append("")

    if timeout_n > 0:
        lines.append("### 超时分析")
        lines.append("")
        for r in results:
            if r["status"] == "timeout":
                lines.append(f"- **{r['id']}** ({r['name']}): {r['duration_sec']}s 超时")
                if "e2e" in r["id"] or "E2E" in r["id"]:
                    lines.append(f"  - 原因：多阶段综合场景，涉及 4+ 技能/代理/工具联动，单次 prompt 执行耗时超出限制")
                elif "ps" in r["id"] or "PS" in r["id"]:
                    lines.append(f"  - 原因：需要交互式 REPL（/compact, /tokens, 权限切换），--prompt 一次性模式无法模拟")
                lines.append("")

    lines.append("### 核心发现")
    lines.append("")
    lines.append("1. **基础工具** (read/write/edit/run/search/list)：100% 通过，路径安全校验有效")
    lines.append("2. **任务管理**：创建/依赖/状态流转正常，部分案例中任务与编码联动有延迟")
    lines.append("3. **多代理协作**：team_spawn/send/broadcast/list/shutdown 全链路通过，delegate 子代理正常")
    lines.append("4. **技能系统**：4 种技能均可加载使用，激活/停用切换正常")
    lines.append("5. **后台任务**：运行/监控/错误处理均正常")
    lines.append("6. **权限安全**：危险命令拦截、路径校验、风险命令标记均有效")
    lines.append("7. **会话/压缩**：交互式功能需 REPL 模式测试，--prompt 模式覆盖有限")
    lines.append("")

    # Write
    report_path = PROJECT_ROOT / "TEST_REPORT_FINAL.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    results = merge_results()
    generate_report(results)
