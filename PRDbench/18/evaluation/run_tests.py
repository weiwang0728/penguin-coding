#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Execution Script
Used to verify the correctness of all automated tests
"""

import subprocess
import sys
import os

def run_test(test_command):
    """Run a single test command"""
    print(f"\n{'='*60}")
    print(f"Running test: {test_command}")
    print('='*60)

    try:
        result = subprocess.run(test_command, shell=True, capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))

        if result.returncode == 0:
            print("✅ Test passed")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ Test failed")
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            if result.stderr:
                print("Error output:")
                print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Test execution exception: {e}")
        return False

def main():
    """Main function"""
    print("Starting automated tests for MatrixAnalysisFinal project")

    # Define all test commands
    test_commands = [
        # Robustness tests
        "python src/main.py --help",
        "python src/main.py --unknown-arg",
        "python src/main.py --model INVALIDMODEL --input src/data/LU.txt",
        "python src/main.py --model LU --input non_existent_file.txt",

        # Correctness tests
        "python -m pytest evaluation/tests/test_lu_correctness.py::test_lu_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_qr_correctness.py::test_qr_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_hr_correctness.py::test_hr_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_gr_correctness.py::test_gr_factorization_correctness -v",
        "python -m pytest evaluation/tests/test_urv_correctness.py::test_urv_factorization_correctness -v",

        # Output format tests
        "python -m pytest evaluation/tests/test_output_format.py::test_lu_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_qr_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_hr_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_gr_output_format -v",
        "python -m pytest evaluation/tests/test_output_format.py::test_urv_output_format -v",

        # Matrix rank calculation tests
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_lu_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_qr_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_hr_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_gr_matrix_rank -v",
        "python -m pytest evaluation/tests/test_matrix_rank.py::test_urv_matrix_rank -v",
    ]

    # Run all tests
    passed = 0
    failed = 0

    for cmd in test_commands:
        if run_test(cmd):
            passed += 1
        else:
            failed += 1

    # Output summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print('='*60)
    print(f"Total tests: {len(test_commands)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())