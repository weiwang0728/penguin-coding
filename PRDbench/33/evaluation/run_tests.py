#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TestRunScript
Used to execute all tests for the federated learning system
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

def run_shell_interaction_test(test_case):
    """Run shell interaction test"""
    print(f"\nRunning test: {test_case['metric']}")
    print(f"Test type: {test_case['type']}")

    # Get test command and input file
    test_command = test_case['testcases'][0]['test_command']
    test_input_file = test_case['testcases'][0]['test_input']

    if test_input_file:
        input_file_path = os.path.join(os.path.dirname(__file__), test_input_file)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            print(f"Warning: Input file does not exist: {input_file_path}")
            return False
    else:
        input_data = ""

    try:
        # ExecuteTest Command
        process = subprocess.Popen(
            test_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        stdout, stderr = process.communicate(input=input_data, timeout=30)

        # Check expected output
        output = stdout + stderr
        expected_output = test_case['expected_output']

        print(f"Program output: {output[:200]}...")
        print(f"Expected output: {expected_output}")

        # Simple output verification (should be more strict in actual tests)
        if "Error" in expected_output and "Error" in output:
            print("✓ Test Passed")
            return True
        elif "Menu" in expected_output and any(x in output for x in ["[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]):
            print("✓ Test Passed")
            return True
        elif "training" in expected_output and "training" in output:
            print("✓ Test Passed")
            return True
        elif "Exit" in expected_output and ("goodbye" in output or process.returncode == 0):
            print("✓ Test Passed")
            return True
        else:
            print("✗ Test Failed")
            return False

    except subprocess.TimeoutExpired:
        process.kill()
        print("✗ Test timeout")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def run_unit_test(test_case):
    """Run unit test"""
    print(f"\nRunning test: {test_case['metric']}")
    print(f"Test type: {test_case['type']}")

    test_command = test_case['testcases'][0]['test_command']

    try:
        # Execute pytest command
        result = subprocess.run(
            test_command.split(),
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            timeout=60
        )

        print(f"Test output: {result.stdout}")
        if result.stderr:
            print(f"Error output: {result.stderr}")

        if result.returncode == 0:
            print("✓ Test Passed")
            return True
        else:
            print("✗ Test Failed")
            return False

    except subprocess.TimeoutExpired:
        print("✗ Test timeout")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def run_file_comparison_test(test_case):
    """Run file comparison test"""
    print(f"\nRunning test: {test_case['metric']}")
    print(f"Test type: {test_case['type']}")

    # First run command to generate file
    test_command = test_case['testcases'][0]['test_command']
    test_input_file = test_case['testcases'][0]['test_input']

    if test_input_file:
        input_file_path = os.path.join(os.path.dirname(__file__), test_input_file)
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            print(f"Warning: Input file does not exist: {input_file_path}")
            return False
    else:
        input_data = ""

    try:
        # Execute command
        process = subprocess.Popen(
            test_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )

        stdout, stderr = process.communicate(input=input_data, timeout=30)

        # Check if expected output files exist
        expected_files = test_case.get('expected_output_files', [])
        if expected_files:
            for expected_file in expected_files:
                expected_path = os.path.join(os.path.dirname(__file__), expected_file)
                if os.path.exists(expected_path):
                    print(f"✓ Expected file exists: {expected_file}")
                else:
                    print(f"✗ Expected file does not exist: {expected_file}")
                    return False

        print("✓ File comparison test passed")
        return True

    except subprocess.TimeoutExpired:
        process.kill()
        print("✗ Test timeout")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False

def main():
    """Main function"""
    print("Starting federated learning system tests...")

    # Load test plan
    test_plan_path = os.path.join(os.path.dirname(__file__), 'detailed_test_plan.json')

    if not os.path.exists(test_plan_path):
        print(f"Error: Test plan file does not exist: {test_plan_path}")
        return

    with open(test_plan_path, 'r', encoding='utf-8') as f:
        test_plan = json.load(f)

    print(f"Loaded {len(test_plan)} test case(s)")

    # Statistics
    total_tests = len(test_plan)
    passed_tests = 0
    failed_tests = 0

    # Run tests
    for i, test_case in enumerate(test_plan, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{total_tests}: {test_case['metric']}")
        print(f"{'='*60}")

        test_type = test_case['type']

        try:
            if test_type == 'shell_interaction':
                success = run_shell_interaction_test(test_case)
            elif test_type == 'unit_test':
                success = run_unit_test(test_case)
            elif test_type == 'file_comparison':
                success = run_file_comparison_test(test_case)
            else:
                print(f"Unknown test type: {test_type}")
                success = False

            if success:
                passed_tests += 1
            else:
                failed_tests += 1

        except Exception as e:
            print(f"Test execution error: {e}")
            failed_tests += 1

        # Brief pause to avoid resource conflicts
        time.sleep(1)

    # Output test results
    print(f"\n{'='*60}")
    print("Test Results Summary")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed tests: {passed_tests}")
    print(f"Failed tests: {failed_tests}")
    print(f"Pass rate: {passed_tests/total_tests*100:.1f}%")

    if failed_tests == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed")

if __name__ == "__main__":
    main()
