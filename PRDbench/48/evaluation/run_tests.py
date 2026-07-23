#!/usr/bin/env python3
"""
Maze Project Test Execution Script
Run all tests and generate test report
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run command and return result"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        print(result.stdout)
        if result.stderr:
            print("Error Information:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Execution Failed: {e}")
        return False

def main():
    """Main test function"""
    print("🏰 Maze Project Test Suite Execution")
    print("="*60)

    # Environment Check
    print("\n📋 1. Environment Verification Test")
    success1 = run_command("python -c \"import numpy; print(f'✅ NumPy Version: {numpy.__version__}')\"",
                          "Check numpy dependency")

    # Unit Test
    print("\n📋 2. Unit Test (pytest)")
    success2 = run_command("pytest evaluation/tests/ -v --tb=short",
                          "Run all unit tests")

    # Shell Interactive Test Examples
    print("\n📋 3. Shell Interactive Test Examples")
    test_cases = [
        ("cd src && python main.py < ../evaluation/inputs/dfs_basic_generate.in",
         "DFS Basic Generation Functional Test"),
        ("cd src && python main.py < ../evaluation/inputs/performance_compare.in",
         "Performance Comparison Functional Test"),
        ("cd src && python main.py < ../evaluation/inputs/validate_connectivity.in",
         "Connectivity Verification Functional Test")
    ]

    shell_success = True
    for cmd, desc in test_cases:
        success = run_command(cmd, desc)
        shell_success = shell_success and success

    # Test Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)

    print(f"Environment Verification: {'✅ Pass' if success1 else '❌ Failed'}")
    print(f"Unit Tests: {'✅ Pass' if success2 else '❌ Failed'}")
    print(f"Shell Interactive Tests: {'✅ Pass' if shell_success else '❌ Failed'}")

    overall_success = success1 and success2 and shell_success
    print(f"\nOverall Result: {'✅ All Tests Passed' if overall_success else '❌ Some Tests Failed'}")

    if not overall_success:
        print("\n💡 Recommendations:")
        print("- Check dependency installation: pip install numpy pytest")
        print("- Check if generated code implementation is complete")
        print("- View detailed error information for troubleshooting")
    else:
        print("\n🎉 Congratulations! All tests passed, project functionality is complete!")

    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())
