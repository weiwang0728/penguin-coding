#!/usr/bin/env python3
"""PRDBench adapter end-to-end test — verify each layer works before full evaluation.

Usage:
    # 层级1: 工具层测试（不需要 LLM API）
    python -m src.prdbench.test_adapter --layer tools

    # 层级2: Agent Loop 测试（需要 LLM API，用简单任务验证）
    python -m src.prdbench.test_adapter --layer agent

    # 层级3: 单项目 DEV 端到端测试（需要 LLM API，完整开发一个项目）
    python -m src.prdbench.test_adapter --layer dev

    # 层级3b: 单项目 EVAL 端到端测试（需要先完成 dev）
    python -m src.prdbench.test_adapter --layer eval

    # 全部运行
    python -m src.prdbench.test_adapter --layer all
"""

import argparse
import json
import os
import sys
import tempfile
import time


def test_tools():
    """Layer 1: Test all PRDBench-specific tools without LLM."""
    print("=" * 60)
    print("  Layer 1: Tool Layer Test")
    print("=" * 60)

    from src.prdbench.tools import (
        JudgeTool, StartInteractiveShellTool, RunInteractiveShellTool,
        KillShellSessionTool, ListWorkspaceTool, ExitLoopTool,
    )

    passed = 0
    failed = 0

    # Test 1: judge tool
    print("\n[1/6] Judge tool...", end=" ")
    try:
        j = JudgeTool()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello\nworld\n")
            input_file = f.name
        result = j.execute(
            context="echo test",
            entry_command="cat",
            input_file=input_file,
        )
        data = json.loads(result)
        os.unlink(input_file)
        assert data["status"] == "success", f"Unexpected status: {data['status']}"
        assert "hello" in data["log"], f"Output missing 'hello': {data['log'][:100]}"
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1

    # Test 2: judge with Python script
    print("[2/6] Judge tool with Python...", end=" ")
    try:
        j = JudgeTool()
        # Create a simple Python script
        script_dir = tempfile.mkdtemp()
        script_path = os.path.join(script_dir, "test_app.py")
        with open(script_path, "w") as f:
            f.write("name = input('Enter name: ')\nprint(f'Hello, {name}!')\n")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Alice\n")
            input_file = f.name
        result = j.execute(
            context="Greet the user",
            entry_command=f"python {script_path}",
            input_file=input_file,
            cwd=script_dir,
        )
        data = json.loads(result)
        os.unlink(input_file)
        assert "Hello, Alice" in data["log"], f"Missing greeting: {data['log'][:200]}"
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1

    # Test 3: list_workspace
    print("[3/6] ListWorkspace tool...", end=" ")
    try:
        lw = ListWorkspaceTool()
        result = lw.execute(workspace_name="/tmp")
        assert len(result) > 0, "Empty result"
        assert "[DIR]" in result or "[FILE]" in result, f"No entries: {result[:100]}"
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1

    # Test 4: start + kill interactive shell
    print("[4/6] Interactive shell (start + kill)...", end=" ")
    try:
        start = StartInteractiveShellTool()
        kill = KillShellSessionTool()
        result = start.execute(cmd="echo ready")
        data = json.loads(result)
        session_id = data["session_id"]
        assert data["status"] == "started"
        kill_result = kill.execute(session_id=session_id)
        assert "terminated" in kill_result
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1

    # Test 5: exit_loop
    print("[5/6] ExitLoop tool...", end=" ")
    try:
        el = ExitLoopTool()
        result = el.execute()
        assert "complete" in result.lower()
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1

    # Test 6: run_command with cwd
    print("[6/6] RunCommand with cwd...", end=" ")
    try:
        from src.tools.run_command import RunCommandTool
        rc = RunCommandTool()
        result = rc.execute(command="pwd", cwd="/tmp")
        assert "/tmp" in result, f"Unexpected cwd: {result[:100]}"
        print("PASS")
        passed += 1
    except Exception as e:
        print(f"FAIL: {e}")
        failed += 1

    print(f"\n{'=' * 60}")
    print(f"  Tool Layer: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")
    return failed == 0


def test_agent():
    """Layer 2: Test agent loop with a simple task (requires LLM API)."""
    print("\n" + "=" * 60)
    print("  Layer 2: Agent Loop Test (requires LLM API)")
    print("=" * 60)

    from src.prdbench.adapter import run_prdbench_agent, session_manager

    # Simple task: create a hello world file
    test_dir = tempfile.mkdtemp(prefix="prdbench_test_")
    prompt = f"""Please create a file called hello.py in {test_dir} with the following content:
print("Hello from penguin-coding!")

After creating the file, run it with python to verify it works."""

    session = session_manager.create("test_agent", "test", "test_app")

    print(f"\nSending prompt to LLM...")
    print(f"Test directory: {test_dir}")
    start_time = time.time()

    result = run_prdbench_agent(
        user_message=prompt,
        session=session,
        mode="dev",
        max_iterations=10,
    )

    elapsed = time.time() - start_time
    session_manager.delete("test_agent")

    print(f"\nResult: status={result.get('status')}, elapsed={elapsed:.1f}s")

    # Verify file was created
    hello_path = os.path.join(test_dir, "hello.py")
    if os.path.exists(hello_path):
        content = open(hello_path).read()
        print(f"File created: {hello_path}")
        print(f"Content: {content[:100]}")
        print("PASS: Agent successfully created and ran the file")
        return True
    else:
        print(f"FAIL: File not created at {hello_path}")
        print(f"Agent output: {result.get('content', '')[:500]}")
        return False


def test_dev():
    """Layer 3: Full DEV stage test on a single PRDBench project."""
    print("\n" + "=" * 60)
    print("  Layer 3: Single-Project DEV Test (requires LLM API)")
    print("=" * 60)

    from src.prdbench.run_evaluation import run_dev_project

    source_dir = "/tmp/prdbench/PRDbench"
    if not os.path.exists(source_dir):
        print(f"FAIL: PRDBench data not found at {source_dir}")
        print("Run: git clone https://github.com/southalone/PRDbench.git /tmp/prdbench")
        return False

    output_dir = tempfile.mkdtemp(prefix="prdbench_dev_test_")
    print(f"Output directory: {output_dir}")
    print(f"Source directory: {source_dir}")
    print(f"Project: 1")

    start_time = time.time()
    success = run_dev_project(
        project_id=1,
        source_dir=source_dir,
        root_path=output_dir,
        max_iterations=50,
    )
    elapsed = time.time() - start_time

    # Verify output
    project_dir = os.path.join(output_dir, "1")
    src_dir = os.path.join(project_dir, "src")

    print(f"\n--- Verification ---")
    print(f"Project dir: {project_dir}")
    print(f"DEV status: {'success' if success else 'failed'}")
    print(f"Elapsed: {elapsed:.1f}s ({elapsed/60:.1f}min)")

    if os.path.exists(src_dir):
        files = []
        for root, dirs, filenames in os.walk(src_dir):
            for f in filenames:
                rel = os.path.relpath(os.path.join(root, f), src_dir)
                files.append(rel)
        print(f"Files generated ({len(files)}):")
        for f in sorted(files):
            size = os.path.getsize(os.path.join(src_dir, f))
            print(f"  {f} ({size} bytes)")
    else:
        print("No src/ directory generated!")

    # Check if PRD.md was preserved
    prd_path = os.path.join(src_dir, "PRD.md")
    if os.path.exists(prd_path):
        print(f"PRD.md preserved: YES")
    else:
        print(f"PRD.md preserved: NO")

    return success


def test_eval():
    """Layer 3b: EVAL stage test on a previously developed project."""
    print("\n" + "=" * 60)
    print("  Layer 3b: Single-Project EVAL Test (requires LLM API + prior DEV)")
    print("=" * 60)

    from src.prdbench.run_evaluation import run_eval_project

    # Use the output from test_dev if available, otherwise look for any existing output
    import glob
    candidates = glob.glob("/tmp/prdbench_dev_test_*")
    if not candidates:
        # Try workspace
        candidates = glob.glob("workspace/penguin_dev_output")

    if not candidates:
        print("FAIL: No DEV output found. Run --layer dev first.")
        return False

    root_path = sorted(candidates)[-1]  # Use most recent
    print(f"Using DEV output: {root_path}")

    if not os.path.exists(os.path.join(root_path, "1", "evaluation", "detailed_test_plan.json")):
        print("FAIL: No detailed_test_plan.json found in project 1")
        return False

    start_time = time.time()
    success = run_eval_project(
        project_id=1,
        root_path=root_path,
        retry_round=0,
        max_iterations=30,
    )
    elapsed = time.time() - start_time

    # Verify reports
    report_dir = os.path.join(root_path, "1", "reports")
    print(f"\n--- Verification ---")
    print(f"EVAL status: {'success' if success else 'failed'}")
    print(f"Elapsed: {elapsed:.1f}s ({elapsed/60:.1f}min)")

    if os.path.exists(report_dir):
        json_files = [f for f in os.listdir(report_dir) if f.endswith(".json")]
        print(f"Report files ({len(json_files)}):")
        for f in sorted(json_files):
            path = os.path.join(report_dir, f)
            try:
                data = json.load(open(path))
                score = data.get("score", "?")
                metric = data.get("metric", "?")[:50]
                print(f"  {f}: score={score}, metric={metric}")
            except Exception:
                print(f"  {f}: (invalid JSON)")
    else:
        print("No reports/ directory generated!")

    return success


def main():
    parser = argparse.ArgumentParser(description="PRDBench adapter test suite")
    parser.add_argument(
        "--layer", type=str, default="tools",
        choices=["tools", "agent", "dev", "eval", "all"],
        help="Test layer to run",
    )
    args = parser.parse_args()

    results = {}

    if args.layer in ("tools", "all"):
        results["tools"] = test_tools()

    if args.layer in ("agent", "all"):
        results["agent"] = test_agent()

    if args.layer in ("dev", "all"):
        results["dev"] = test_dev()

    if args.layer in ("eval", "all"):
        results["eval"] = test_eval()

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for layer, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {layer}: {status}")

    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
