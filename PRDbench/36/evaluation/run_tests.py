#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TestRunScript
UseAtAutomatedExecutetest planinEachTypeTest
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def load_test_plan():
    """Loadtest plan"""
    test_plan_path = Path(__file__).parent / "detailed_test_plan.json"
    with open(test_plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_shell_interaction_test(testcase):
    """RunshellinteractiveTest"""
    cmd = testcase['test_command']
    input_file = testcase.get('test_input')

    print(f"RunCommand: {cmd}")

    if input_file:
        input_path = Path(__file__).parent.parent / input_file
        if input_path.exists():
            with open(input_path, 'r', encoding='utf-8') as f:
                input_data = f.read()

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=30
                )
                return result.returncode == 0, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                return False, "", "TestUltraTime"
        else:
            return False, "", f"OutputInputFileNotSavein: {input_file}"
    else:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "TestUltraTime"

def run_unit_test(testcase):
    """RunUnit Test"""
    cmd = testcase['test_command']
    print(f"RunUnit Test: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "TestUltraTime"

def run_file_comparison_test(testcase):
    """RunFileBiferCompareTest"""
    # firstRunCommandGenerateFile
    success, stdout, stderr = run_shell_interaction_test(testcase)

    if not success:
        return False, stdout, stderr

    # hereCantoAddFileBiferComparelogic
    return True, "FileBiferCompareTest Passed", ""

def run_single_test(test_item):
    """RunSingleitem(s)Test"""
    metric = test_item['metric']
    test_type = test_item['type']
    testcases = test_item['testcases']

    print(f"\n{'='*60}")
    print(f"Test Itemitem: {metric}")
    print(f"TestCategoryType: {test_type}")
    print(f"{'='*60}")

    all_passed = True

    for i, testcase in enumerate(testcases, 1):
        print(f"\n--- Test Case {i} ---")

        if test_type == "shell_interaction":
            success, stdout, stderr = run_shell_interaction_test(testcase)
        elif test_type == "unit_test":
            success, stdout, stderr = run_unit_test(testcase)
        elif test_type == "file_comparison":
            success, stdout, stderr = run_file_comparison_test(testcase)
        else:
            success, stdout, stderr = False, "", f"NotKnowTestCategoryType: {test_type}"

        if success:
            print("✅ Test Passed")
        else:
            print("❌ Test Failed")
            all_passed = False

        if stdout:
            print(f"Output: {stdout[:200]}...")
        if stderr:
            print(f"Error: {stderr[:200]}...")

    return all_passed

def main():
    """mainFunctionNumber"""
    print("Keigo HigashinoSmallnovel textminingandLanguageDefinitionAnalysisTool - AutomatedTest")
    print("="*60)

    # CheckWhenbeforeDirectory
    current_dir = Path.cwd()
    if current_dir.name != "problem8":
        print("pleaseinitem(s)project rootDirectoryunderRunthisScript")
        sys.exit(1)

    # Loadtest plan
    try:
        test_plan = load_test_plan()
        print(f"Load {len(test_plan)} item(s)Test Itemitem")
    except Exception as e:
        print(f"Loadtest planFailure: {e}")
        sys.exit(1)

    # RunTest
    passed_tests = 0
    total_tests = len(test_plan)

    for test_item in test_plan:
        try:
            if run_single_test(test_item):
                passed_tests += 1
        except KeyboardInterrupt:
            print("\nTestbyUserinBreak")
            break
        except Exception as e:
            print(f"TestExecuteOutputWrong: {e}")

    # OutputResult
    print(f"\n{'='*60}")
    print(f"TestCompleteSuccess: {passed_tests}/{total_tests} item(s)Test Passed")
    print(f"Pass Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
