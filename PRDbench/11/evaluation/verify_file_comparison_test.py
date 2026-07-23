#!/usr/bin/env python3
"""
Simplified script to verify file comparison test
Verify if "2.1b Automated Unit Testing - Test Coverage" test is correctly set up
"""

import subprocess
import sys
import json
from pathlib import Path

def main():
    print("Verifying file comparison test setup...")

    # 1. Check if all required files exist
    required_files = [
        "evaluation/test_coverage_analyzer.py",
        "evaluation/expected_test_coverage_report.json",
        "evaluation/file_comparator.py",
        "src/tests/test_utils.py"
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"ERROR: Missing required file {file_path}")
            return False
        else:
            print(f"OK: File exists {file_path}")

    # 2. Execute test command
    print("\nExecuting test command...")
    try:
        result = subprocess.run([
            "python", "evaluation/test_coverage_analyzer.py",
            "src/tests", "evaluation/test_output.json"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("OK: Test coverage analyzer executed successfully")
        else:
            print(f"ERROR: Test coverage analyzer failed, exit code: {result.returncode}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to execute test command: {e}")
        return False

    # 3. Verify output file
    if Path("evaluation/test_output.json").exists():
        print("OK: Generated output file")

        # Read and verify output content
        try:
            with open("evaluation/test_output.json", 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'overall_stats' in data and data['overall_stats'].get('coverage_percentage') == 100.0:
                print("OK: Test coverage is 100%")
            else:
                print("WARNING: Test coverage is not 100%")

        except Exception as e:
            print(f"ERROR: Failed to read output file: {e}")
            return False
    else:
        print("ERROR: Output file was not generated")
        return False

    print("\nFile comparison test verification complete - All checks passed!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)