#!/usr/bin/env python3
"""
Run Test Coverage Check Complete Process
This script demonstrates how to execute the "2.1b Automated Unit Testing - Test Coverage" test
"""

import subprocess
import sys
import json
from pathlib import Path

def run_command(command, description):
    """Run command and return result"""
    print(f"\n{'='*50}")
    print(f"Executing: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print("Standard output:")
            print(result.stdout)
        if result.stderr:
            print("Standard error:")
            print(result.stderr)

        return result.returncode == 0, result
    except Exception as e:
        print(f"Execution error: {e}")
        return False, None

def main():
    """Main function - execute complete test coverage check process"""
    print("Starting test coverage check...")

    # Step 1: Generate actual test coverage report
    success1, result1 = run_command(
        "python evaluation/test_coverage_analyzer.py src/tests evaluation/actual_test_coverage_report.json",
        "Generate actual test coverage report"
    )

    if not success1:
        print("[ERROR] Failed to generate test coverage report")
        return False

    # Step 2: Verify generated file exists
    actual_report_path = Path("evaluation/actual_test_coverage_report.json")
    expected_report_path = Path("evaluation/expected_test_coverage_report.json")

    if not actual_report_path.exists():
        print(f"[ERROR] Actual report file does not exist: {actual_report_path}")
        return False

    if not expected_report_path.exists():
        print(f"[ERROR] Expected report file does not exist: {expected_report_path}")
        return False

    print("[OK] Both report files exist")

    # Step 3: Compare file contents
    success2, result2 = run_command(
        f"python evaluation/file_comparator.py {expected_report_path} {actual_report_path}",
        "Compare expected and actual reports"
    )

    if not success2:
        print("[ERROR] File comparison failed")
        return False

    # Step 4: Parse comparison result
    try:
        comparison_result = json.loads(result2.stdout)
        if comparison_result.get('files_match', False):
            print("[SUCCESS] File contents match! Test coverage check passed")

            # Display coverage details
            with open(actual_report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            print(f"\n[STATS] Test coverage statistics:")
            stats = report_data.get('overall_stats', {})
            print(f"  Total functions: {stats.get('total_functions', 'N/A')}")
            print(f"  Fully covered functions: {stats.get('fully_covered_functions', 'N/A')}")
            print(f"  Coverage percentage: {stats.get('coverage_percentage', 'N/A')}%")
            print(f"  Total test files: {stats.get('total_test_files', 'N/A')}")
            print(f"  Total test methods: {stats.get('total_test_methods', 'N/A')}")

            return True
        else:
            print("[ERROR] File contents do not match! Test coverage check failed")
            return False

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse comparison result: {e}")
        return False

if __name__ == '__main__':
    success = main()

    print(f"\n{'='*50}")
    if success:
        print("[SUCCESS] Test coverage check completed - All passed!")
    else:
        print("[FAILED] Test coverage check completed - Issues found!")
    print(f"{'='*50}")

    sys.exit(0 if success else 1)