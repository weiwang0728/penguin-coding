"""Objective verifiers for E2E test cases.

Replaces keyword-matching with actual state checks:
- File system (existence, content, AST structure)
- Subprocess (real test runs)
- Memory store (count, search)
- Task store (JSON file state)
- Security (path should NOT exist as proof of block)

Each verifier returns (passed, method, detail). `method` is one of:
  file_exists, file_ast, test_run, security_block,
  task_state, file_size, output_keyword (weak), tool_used (weak)

Only output_keyword and tool_used fall back to keyword matching on agent
output — everything else checks objective state.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = PROJECT_ROOT / "workspace"
TASKS_DIR = WORKSPACE / ".penguin_tasks"

# Path patterns to extract from verification point text
PATH_PATTERNS = [
    re.compile(r"workspace/[\w/.\-]+\.py"),
    re.compile(r"workspace/[\w/.\-]+\.pdf"),
    re.compile(r"workspace/[\w/.\-]+\.txt"),
    re.compile(r"workspace/[\w/.\-]+\.md"),
    re.compile(r"workspace/[\w/.\-]+/"),
]

# Blocked paths that should NOT exist (proof of security enforcement)
BLOCKED_PATHS = [
    "/tmp/outside.py",
    "/tmp/nonexistent.py",
]


def _extract_paths(text: str) -> list[Path]:
    """Extract workspace-relative paths from verification text."""
    paths = []
    seen = set()
    for pat in PATH_PATTERNS:
        for m in pat.finditer(text):
            p_str = m.group(0).rstrip("/")
            if p_str not in seen:
                seen.add(p_str)
                # Resolve to project root
                paths.append(PROJECT_ROOT / p_str)
    return paths


def _extract_func_name(text: str) -> str | None:
    """Extract function name from text like '包含 def binary_search 函数'."""
    m = re.search(r"def\s+(\w+)", text)
    if m:
        return m.group(1)
    # Chinese: "包含 binary_search 函数"
    m = re.search(r"包含\s+(\w+)\s+函数", text)
    if m:
        return m.group(1)
    return None


def _extract_class_name(text: str) -> str | None:
    m = re.search(r"class\s+(\w+)", text)
    if m:
        return m.group(1)
    m = re.search(r"包含\s+(\w+)\s+(?:类|数据类)", text)
    if m:
        return m.group(1)
    return None


def _extract_test_target(text: str, case_description: str = "") -> Path | None:
    """Find a test file path to run pytest against."""
    # From verification text
    for pat in PATH_PATTERNS:
        m = pat.search(text)
        if m:
            p = m.group(0).rstrip("/")
            if "test" in p.lower():
                return PROJECT_ROOT / p
    # From case description
    for pat in PATH_PATTERNS:
        m = pat.search(case_description)
        if m:
            p = m.group(0).rstrip("/")
            if "test" in p.lower():
                return PROJECT_ROOT / p
    return None


# ═══════════════════════════════════════════════════════════════
# Individual objective checkers
# ═══════════════════════════════════════════════════════════════

def check_file_exists(check_text: str) -> tuple[bool, str, str]:
    """Verify that workspace files mentioned in check_text actually exist."""
    paths = _extract_paths(check_text)
    if not paths:
        return False, "file_exists", "no path extracted from check text"
    missing = [p for p in paths if not p.exists()]
    if missing:
        return False, "file_exists", f"missing: {[str(p.relative_to(PROJECT_ROOT)) for p in missing]}"
    sizes = [f"{p.relative_to(PROJECT_ROOT)}({p.stat().st_size}B)" for p in paths]
    return True, "file_exists", f"exists: {sizes}"


def check_file_has_main_block(check_text: str, fallback_path: Path | None = None) -> tuple[bool, str, str]:
    """Verify a Python file has an `if __name__ == '__main__':` block via AST."""
    paths = [p for p in _extract_paths(check_text) if p.suffix == ".py"]
    if not paths and fallback_path is not None:
        paths = [fallback_path]
    if not paths:
        return False, "file_ast", "no path extracted"
    target = paths[0]
    if not target.exists():
        return False, "file_ast", f"file not found: {target.relative_to(PROJECT_ROOT)}"
    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return False, "file_ast", f"SyntaxError: {e}"
    # Walk for `if __name__ == "__main__":` — compare node is ast.Compare with
    # ast.Name(id="__name__") and ast.Constant(value="__main__")
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            if (isinstance(test, ast.Compare)
                    and isinstance(test.left, ast.Name)
                    and test.left.id == "__name__"
                    and any(isinstance(c, ast.Constant) and c.value == "__main__" for c in test.comparators)):
                return True, "file_ast", f"found __main__ block in {target.relative_to(PROJECT_ROOT)}"
    return False, "file_ast", f"no __main__ block in {target.relative_to(PROJECT_ROOT)}"


def check_file_has_func(check_text: str, fallback_path: Path | None = None) -> tuple[bool, str, str]:
    """Verify a Python file contains a function via AST parsing."""
    paths = [p for p in _extract_paths(check_text) if p.suffix == ".py"]
    if not paths and fallback_path is not None:
        paths = [fallback_path]
    func_name = _extract_func_name(check_text)
    if not paths or not func_name:
        return False, "file_ast", "no path or function name extracted"
    target = paths[0]
    if not target.exists():
        return False, "file_ast", f"file not found: {target.relative_to(PROJECT_ROOT)}"
    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return False, "file_ast", f"SyntaxError: {e}"
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if func_name in funcs:
        return True, "file_ast", f"found '{func_name}' in {target.relative_to(PROJECT_ROOT)} (funcs: {funcs[:5]})"
    return False, "file_ast", f"'{func_name}' not in funcs {funcs[:5]}"


def check_file_has_class(check_text: str, fallback_path: Path | None = None) -> tuple[bool, str, str]:
    """Verify a Python file contains a class via AST parsing."""
    paths = [p for p in _extract_paths(check_text) if p.suffix == ".py"]
    if not paths and fallback_path is not None:
        paths = [fallback_path]
    class_name = _extract_class_name(check_text)
    if not paths or not class_name:
        return False, "file_ast", "no path or class name extracted"
    target = paths[0]
    if not target.exists():
        return False, "file_ast", f"file not found: {target.relative_to(PROJECT_ROOT)}"
    try:
        tree = ast.parse(target.read_text(encoding="utf-8"))
    except SyntaxError as e:
        return False, "file_ast", f"SyntaxError: {e}"
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    if class_name in classes:
        return True, "file_ast", f"found class '{class_name}' (classes: {classes})"
    return False, "file_ast", f"'{class_name}' not in classes {classes}"


def check_run_output_contains(
    check_text: str,
    case_description: str = "",
    fallback_path: Path | None = None,
) -> tuple[bool, str, str]:
    """Run a Python script and check if its stdout contains an expected keyword.

    Used for verification points like "运行输出包含 'All tests passed'".
    """
    # Extract expected keyword from quotes in check_text
    kw_match = re.search(r"[\"']([^\"']+)[\"']", check_text)
    expected = kw_match.group(1) if kw_match else None

    # Find the script to run: prefer check_text path, fall back to last mentioned
    paths = [p for p in _extract_paths(check_text) if p.suffix == ".py"]
    if not paths:
        paths = [p for p in _extract_paths(case_description) if p.suffix == ".py"]
    if not paths and fallback_path is not None:
        paths = [fallback_path]
    if not paths:
        return False, "test_run", "no script path found to run"

    target = paths[0]
    if not target.exists():
        return False, "test_run", f"script not found: {target.relative_to(PROJECT_ROOT)}"

    try:
        result = subprocess.run(
            [sys.executable, str(target)],
            capture_output=True, text=True, timeout=30, cwd=str(PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        return False, "test_run", "script timed out (30s)"

    stdout_lower = result.stdout.lower()
    if expected is None:
        # No expected keyword — just check exit 0 and non-empty stdout
        if result.returncode == 0 and result.stdout.strip():
            return True, "test_run", f"exit=0, stdout len={len(result.stdout)}"
        return False, "test_run", f"exit={result.returncode}, stdout empty"

    if expected.lower() in stdout_lower:
        excerpt = result.stdout.strip().split("\n")[-1][:100]
        return True, "test_run", f"stdout contains '{expected}' | tail: {excerpt}"
    err_tail = (result.stdout + result.stderr).strip().split("\n")[-1][:100]
    return False, "test_run", f"stdout missing '{expected}' | exit={result.returncode} | tail: {err_tail}"


def check_test_passes(check_text: str, case_description: str = "") -> tuple[bool, str, str]:
    target = _extract_test_target(check_text, case_description)
    if not target:
        return False, "test_run", "no test file path found in check/description"
    if not target.exists():
        return False, "test_run", f"test file not found: {target.relative_to(PROJECT_ROOT)}"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(target), "-v", "--tb=short"],
            capture_output=True, text=True, timeout=60, cwd=str(PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        return False, "test_run", "pytest timed out (60s)"
    if result.returncode == 0:
        # Count passed tests from output
        passed = re.findall(r"(\d+) passed", result.stdout)
        n = passed[0] if passed else "?"
        return True, "test_run", f"pytest exit=0, {n} passed"
    # Failed — extract failure summary
    failed = re.findall(r"(\d+) failed", result.stdout)
    n = failed[0] if failed else "?"
    err_excerpt = (result.stdout + result.stderr)[-200:].replace("\n", " ")
    return False, "test_run", f"pytest exit={result.returncode}, {n} failed | tail: {err_excerpt}"


def check_security_block(check_text: str) -> tuple[bool, str, str]:
    """Verify security block by checking that blocked paths do NOT exist."""
    # Find which path is mentioned
    mentioned_blocked = []
    for blocked in BLOCKED_PATHS:
        if blocked in check_text or Path(blocked).name in check_text:
            mentioned_blocked.append(blocked)
    # Also check /etc/passwd write attempts — these should fail (path outside workspace)
    if "/etc/passwd" in check_text or "etc/passwd" in check_text:
        mentioned_blocked.append("/etc/passwd")

    if not mentioned_blocked:
        # Generic security block — check that no /tmp file was created
        tmp_files = list(Path("/tmp").glob("outside*.py")) + list(Path("/tmp").glob("nonexistent*.py"))
        if tmp_files:
            return False, "security_block", f"blocked file was created: {tmp_files[:2]}"
        return True, "security_block", "no blocked files in /tmp (negative proof)"

    # For each mentioned blocked path, verify it does NOT exist (proving write was blocked)
    created = [p for p in mentioned_blocked if Path(p).exists()]
    if created:
        return False, "security_block", f"blocked path was created (security failed): {created}"
    return True, "security_block", f"blocked paths correctly absent: {mentioned_blocked}"



def check_task_state(check_text: str) -> tuple[bool, str, str]:
    """Verify task state by reading the task JSON files directly."""
    if not TASKS_DIR.exists():
        return False, "task_state", f"tasks dir not found: {TASKS_DIR.relative_to(PROJECT_ROOT)}"

    task_files = sorted(TASKS_DIR.glob("task_*.json"))
    if not task_files:
        return False, "task_state", "no task files found"

    tasks = []
    for f in task_files:
        try:
            tasks.append(json.loads(f.read_text()))
        except Exception:
            continue

    if not tasks:
        return False, "task_state", "no valid task JSON"

    statuses = [t.get("status", "unknown") for t in tasks]
    completed = sum(1 for s in statuses if s == "completed")
    total = len(tasks)

    if "所有任务" in check_text or "all" in check_text.lower():
        if all(s == "completed" for s in statuses):
            return True, "task_state", f"all {total} tasks completed"
        return False, "task_state", f"{completed}/{total} completed, statuses: {statuses}"

    if completed > 0:
        return True, "task_state", f"{completed}/{total} tasks completed"
    return False, "task_state", f"no tasks completed, statuses: {statuses}"


def check_file_size(check_text: str) -> tuple[bool, str, str]:
    """Verify file size > 0."""
    paths = _extract_paths(check_text)
    if not paths:
        return False, "file_size", "no path extracted"
    target = paths[0]
    if not target.exists():
        return False, "file_size", f"file not found: {target.relative_to(PROJECT_ROOT)}"
    size = target.stat().st_size
    if size > 0:
        return True, "file_size", f"{target.relative_to(PROJECT_ROOT)} = {size} bytes"
    return False, "file_size", f"{target.relative_to(PROJECT_ROOT)} is empty (0 bytes)"


def check_output_contains(check_text: str, output: str, keywords: list[str]) -> tuple[bool, str, str]:
    """Weak verification: keyword match against agent output. Used only for
    text-only outputs (review reports, design docs, MCP schemas)."""
    output_lower = output.lower()
    matched = [kw for kw in keywords if kw.lower() in output_lower]
    if matched:
        return True, "output_keyword", f"matched: {matched}"
    return False, "output_keyword", f"none of {keywords} found in output"


def check_tool_used(check_text: str, output: str, expected_tool: str) -> tuple[bool, str, str]:
    """Weak verification: tool name appears in agent output."""
    if expected_tool in output:
        return True, "tool_used", f"'{expected_tool}' found in output"
    return False, "tool_used", f"'{expected_tool}' not in output"


# ═══════════════════════════════════════════════════════════════
# Dispatcher
# ═══════════════════════════════════════════════════════════════

# Map: feature name → expected tool name (for tool_used checks)
FEATURE_TOOL_MAP = {
    "read_file": "read_file", "write_file": "write_file", "edit_file": "edit_file",
    "run_command": "run_command", "search_files": "search_files",
    "list_directory": "list_directory",
    "task_create": "task", "task_update": "task", "task_list": "task",
    "team_spawn": "team_spawn", "team_send": "team_send", "team_broadcast": "team_broadcast",
    "team_list": "team_list", "team_shutdown": "team_shutdown",
    "delegate": "delegate", "load_skill": "load_skill",
    "background_run": "background_run", "check_background": "check_background",
}


def classify_and_verify(
    check_text: str,
    output: str,
    case: dict,
    last_file_path: Path | None = None,
) -> dict:
    """Dispatch a single verification point to the appropriate objective checker.

    Returns: {check, passed, method, detail}
    """
    ct = check_text
    ct_lower = ct.lower()
    case_desc = case.get("description", "")
    features = case.get("features", [])

    # ── Objective checks (preferred) ──

    # Security block — by proof of absence
    if any(kw in ct for kw in ["被拦截", "被拒绝", "路径校验", "blocked"]) or "outside the allowed" in ct_lower:
        passed, method, detail = check_security_block(ct)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # File existence
    if any(kw in ct for kw in ["文件存在", "文件创建", "文件成功创建", "文件存在且"]) and _extract_paths(ct):
        passed, method, detail = check_file_exists(ct)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # File contains function (AST) — also fall back to last mentioned file
    if "包含" in ct and ("函数" in ct or "def " in ct_lower):
        passed, method, detail = check_file_has_func(ct, fallback_path=last_file_path)
        if method == "file_ast" and "no path or function" not in detail:
            return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # __main__ block (AST)
    if "__main__" in ct_lower or "main" in ct_lower and "测试块" in ct:
        passed, method, detail = check_file_has_main_block(ct, fallback_path=last_file_path)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # File contains class (AST) — also fall back to last mentioned file
    if "包含" in ct and ("类" in ct or "class " in ct_lower):
        passed, method, detail = check_file_has_class(ct, fallback_path=last_file_path)
        if method == "file_ast" and "no path or class" not in detail:
            return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Test passes — actually run pytest
    if any(kw in ct for kw in ["测试通过", "pytest 运行通过", "运行通过", "测试全部通过"]):
        passed, method, detail = check_test_passes(ct, case_desc)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # "运行输出包含 X" — actually run the script and check stdout
    if "运行输出包含" in ct:
        passed, method, detail = check_run_output_contains(ct, case_desc, last_file_path)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # File size > 0
    if "文件大小" in ct or "> 0" in ct:
        passed, method, detail = check_file_size(ct)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Task state
    if any(kw in ct for kw in ["任务", "task", "completed", "状态"]) and ("completed" in ct_lower or "任务" in ct):
        passed, method, detail = check_task_state(ct)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # ── Weak checks (output keyword matching, explicitly marked) ──

    # Tool used — for "Feature 'X' → tool 'Y' used" checks
    if "Feature" in ct and "tool" in ct_lower and "used" in ct_lower:
        # Extract expected tool from features
        for feat in features:
            if feat in FEATURE_TOOL_MAP and feat in ct:
                passed, method, detail = check_tool_used(ct, output, FEATURE_TOOL_MAP[feat])
                return {"check": ct, "passed": passed, "method": method, "detail": detail}
        # Generic: any tool name in output
        return {"check": ct, "passed": True, "method": "tool_used", "detail": "feature check skipped (no mapping)"}

    # Search results
    if any(kw in ct for kw in ["搜索结果", "找到", "search result"]):
        keywords = ["found", "match", "result", "找到", "搜索结果", "matches"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Review content
    if any(kw in ct for kw in ["审查", "review", "评分", "评分和改进"]):
        keywords = ["review", "score", "rating", "审查", "评分", "建议", "recommendation", "improvement"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Design content
    if "设计" in ct and ("方案" in ct or "架构" in ct):
        keywords = ["design", "architecture", "设计", "架构", "component", "模块", "工具定义", "提示词"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # MCP content
    if "mcp" in ct_lower:
        keywords = ["mcp", "server", "tool", "schema"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # PDF content
    if "pdf" in ct_lower:
        keywords = ["pdf", "reportlab", "pymupdf"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Delegate / subagent
    if "delegate" in ct_lower or "子代理" in ct or "委派" in ct:
        keywords = ["delegate", "sub-agent", "子代理", "委派", "subagent"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Team operations
    if "team" in ct_lower or ("代理" in ct and ("spawn" in ct_lower or "创建" in ct)):
        keywords = ["team", "agent", "代理", "spawn", "teammate"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Parallel execution
    if "并行" in ct or "parallel" in ct_lower:
        # Objective: check that multiple tool calls appear in output
        tool_call_pattern = re.compile(r"> (\w+)\(")
        calls = tool_call_pattern.findall(output)
        if len(calls) >= 2:
            return {"check": ct, "passed": True, "method": "output_keyword",
                    "detail": f"multiple tool calls in output: {calls[:3]}"}
        return {"check": ct, "passed": False, "method": "output_keyword",
                "detail": f"only {len(calls)} tool calls found"}

    # List output
    if "列表" in ct or "list" in ct_lower:
        keywords = ["list", "entries", "项目", "found", "目录", "files"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Op success
    if any(kw in ct for kw in ["返回成功", "保存成功", "激活成功", "创建成功"]):
        keywords = ["saved", "created", "activated", "success", "成功", "ok"]
        passed, method, detail = check_output_contains(ct, output, keywords)
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # not found
    if "not found" in ct_lower:
        passed, method, detail = check_output_contains(ct, output, ["not found"])
        return {"check": ct, "passed": passed, "method": method, "detail": detail}

    # Generic fallback — weak
    if output and "error" not in output.lower()[:200]:
        return {"check": ct, "passed": True, "method": "output_keyword",
                "detail": "no error in output (generic weak pass)"}
    return {"check": ct, "passed": False, "method": "output_keyword",
            "detail": "no matching verifier and output empty/errored"}


def verify_case(
    case: dict,
    result: dict,
) -> list[dict]:
    """Verify a case result using objective checks where possible.

    Args:
        case: the YAML case dict (with description, features, verification)
        result: the run result dict (with output, tool_calls)
    """
    output = result.get("output", "")
    verifications = []
    verify_points = case.get("verification", [])

    # Seed last_file_path from case description (in case verification points
    # don't mention paths explicitly but the case description does)
    last_file_path: Path | None = None
    desc_paths = _extract_paths(case.get("description", ""))
    py_paths = [p for p in desc_paths if p.suffix == ".py"]
    if py_paths:
        last_file_path = py_paths[0]

    for vp in verify_points:
        v = classify_and_verify(vp, output, case, last_file_path)
        verifications.append(v)
        # Update last_file_path if this check mentions a workspace file
        vp_paths = _extract_paths(vp)
        vp_py = [p for p in vp_paths if p.suffix == ".py"]
        if vp_py:
            last_file_path = vp_py[0]

    # Feature-based tool usage checks (append)
    called_tools = set(result.get("tool_calls", []))
    for feat in case.get("features", []):
        if feat in FEATURE_TOOL_MAP:
            expected_tool = FEATURE_TOOL_MAP[feat]
            if expected_tool in output or expected_tool in called_tools:
                verifications.append({
                    "check": f"Feature '{feat}' → tool '{expected_tool}' used",
                    "passed": True,
                    "method": "tool_used",
                    "detail": "tool name found in output",
                })

    return verifications


def summarize_methods(verifications: list[dict]) -> dict:
    """Summarize verification methods used — objective vs weak."""
    summary = {"objective": {"total": 0, "passed": 0}, "weak": {"total": 0, "passed": 0}}
    WEAK_METHODS = {"output_keyword", "tool_used"}
    for v in verifications:
        method = v.get("method", "output_keyword")
        bucket = "weak" if method in WEAK_METHODS else "objective"
        summary[bucket]["total"] += 1
        if v["passed"]:
            summary[bucket]["passed"] += 1
    return summary
