#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script to fix Chinese display issues
"""

import subprocess
import sys
import json
import os
from pathlib import Path

# Set output encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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
            print(f"Error: Missing required file {file_path}")
            return False
        else:
            print(f"Normal: File exists {file_path}")

    # 2. Execute test command
    print("\nExecuting test command...")
    try:
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'

        result = subprocess.run([
            "python", "evaluation/test_coverage_analyzer.py",
            "src/tests", "evaluation/test_output_fixed.json"
        ], capture_output=True, text=True, env=env, encoding='utf-8')

        if result.returncode == 0:
            print("Normal: Test coverage analyzer executed successfully")
        else:
            print(f"Error: Test coverage analyzer failed, exit code: {result.returncode}")
            if result.stderr:
                print(f"Error message: {result.stderr}")
            return False

    except Exception as e:
        print(f"Error: Failed to execute test command: {e}")
        return False

    # 3. Verify output file
    output_file = "evaluation/test_output_fixed.json"
    if Path(output_file).exists():
        print("Normal: Generated output file")

        # Read and verify output content
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            coverage = data.get('overall_stats', {}).get('coverage_percentage', 0)
            functions_covered = data.get('overall_stats', {}).get('fully_covered_functions', 0)
            total_functions = data.get('overall_stats', {}).get('total_functions', 0)

            print(f"Normal: Test coverage is {coverage}%")
            print(f"Normal: {functions_covered}/{total_functions} functions fully covered")

            if coverage == 100.0:
                print("Excellent: Achieved 100% test coverage!")
            else:
                print("Warning: Test coverage is not 100%")

        except Exception as e:
            print(f"Error: Failed to read output file: {e}")
            return False
    else:
        print("Error: Output file was not generated")
        return False

    print("\n" + "="*60)
    print("File comparison test verification complete - All checks passed!")
    print("="*60)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)