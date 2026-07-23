#!/usr/bin/env python3
"""
Test Execution Script - Run All Test Cases
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print test banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🧪 Enterprise Management Training & Skills Analysis    ║
║                                                              ║
║        Enterprise Management Training & Skills Analysis       ║
║                    Test Suite Runner                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

def load_test_plan():
    """Load test plan"""
    try:
        with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Load test plan failed: {e}")
        return []

def run_shell_interaction_test(test_case):
    """Run shell interaction test"""
    print(f"🔧 Executing shell interaction test...")

    for i, testcase in enumerate(test_case['testcases']):
        print(f"   Step {i+1}: {testcase['test_command']}")

        try:
            # Prepare input
            input_data = None
            if testcase['test_input']:
                input_file = testcase['test_input']
                if os.path.exists(input_file):
                    with open(input_file, 'r', encoding='utf-8') as f:
                        input_data = f.read()

            # Execute command
            result = subprocess.run(
                testcase['test_command'],
                shell=True,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"   ✅ Command executed successfully")
                if result.stdout:
                    print(f"   Output: {result.stdout[:200]}...")
            else:
                print(f"   ❌ Command execution failed (Exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Command execution timed out")
            return False
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            return False

    return True

def run_unit_test(test_case):
    """Run unit test"""
    print(f"🧪 Executing unit test...")

    for testcase in test_case['testcases']:
        print(f"   Command: {testcase['test_command']}")

        try:
            result = subprocess.run(
                testcase['test_command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print(f"   ✅ Test Passed")
                if "PASSED" in result.stdout:
                    print(f"   Details: Test case executed successfully")
            else:
                print(f"   ❌ Test Failed (Exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:300]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Test execution timed out")
            return False
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            return False

    return True

def run_file_comparison_test(test_case):
    """Run file comparison test"""
    print(f"📄 Executing file comparison test...")

    for testcase in test_case['testcases']:
        print(f"   Command: {testcase['test_command']}")

        try:
            # Execute file generation command
            result = subprocess.run(
                testcase['test_command'],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"   ✅ File generation command executed successfully")

                # Check if expected output file exists
                if test_case['expected_output_files']:
                    for expected_file in test_case['expected_output_files']:
                        if os.path.exists(expected_file):
                            file_size = os.path.getsize(expected_file)
                            print(f"   ✅ Expected file exists: {expected_file} ({file_size} bytes)")
                        else:
                            print(f"   ❌ Expected file not found: {expected_file}")
                            return False

            else:
                print(f"   ❌ File generation failed (Exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"   ⏰ Command execution timed out")
            return False
        except Exception as e:
            print(f"   ❌ Execution error: {e}")
            return False

    return True

def run_single_test(test_case):
    """Run single test case"""
    print(f"\n{'='*60}")
    print(f"Test: {test_case['metric']}")
    print(f"Type: {test_case['type']}")
    print('='*60)

    if test_case['type'] == 'shell_interaction':
        return run_shell_interaction_test(test_case)
    elif test_case['type'] == 'unit_test':
        return run_unit_test(test_case)
    elif test_case['type'] == 'file_comparison':
        return run_file_comparison_test(test_case)
    else:
        print(f"❌ Unknown test type: {test_case['type']}")
        return False

def main():
    """Main function"""
    print_banner()

    # Load test plan
    test_plan = load_test_plan()
    if not test_plan:
        print("❌ Unable to load test plan")
        return

    print(f"📋 Loaded {len(test_plan)} test case(s)")

    # Statistics
    passed_tests = 0
    failed_tests = 0

    # Execute all tests
    for i, test_case in enumerate(test_plan, 1):
        print(f"\n🔍 Executing test {i}/{len(test_plan)}")

        try:
            if run_single_test(test_case):
                passed_tests += 1
                print(f"✅ Test Passed")
            else:
                failed_tests += 1
                print(f"❌ Test Failed")
        except Exception as e:
            failed_tests += 1
            print(f"❌ Test error: {e}")

    # Output test results summary
    print(f"\n{'='*60}")
    print(f"📊 Test Results Summary")
    print('='*60)
    print(f"Total tests: {len(test_plan)}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success rate: {passed_tests/len(test_plan)*100:.1f}%")

    if failed_tests == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed, please check related functionality")

if __name__ == "__main__":
    main()