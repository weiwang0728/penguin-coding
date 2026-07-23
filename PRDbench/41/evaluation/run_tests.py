#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated test execution script
Execute all tests based on detailed_test_plan.json and generate report
"""

import json
import subprocess
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

class TestExecutor:
    def __init__(self):
        self.test_plan_file = "evaluation/detailed_test_plan.json"
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    def load_test_plan(self) -> List[Dict]:
        """Load test plan"""
        try:
            with open(self.test_plan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error: Cannot load test plan file - {e}")
            return []

    def execute_shell_interaction_test(self, test_case: Dict) -> Dict:
        """Execute shell interaction test"""
        result = {
            "status": "UNKNOWN",
            "output": "",
            "error": "",
            "execution_time": 0
        }

        try:
            start_time = time.time()

            # Build command
            cmd = test_case["test_command"]
            test_input_file = test_case.get("test_input")

            if test_input_file and os.path.exists(test_input_file):
                # Use input file
                with open(test_input_file, 'r') as f:
                    input_data = f.read()

                process = subprocess.run(
                    cmd.split(),
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=10
                )
            else:
                # No input file
                process = subprocess.run(
                    cmd.split(),
                    text=True,
                    capture_output=True,
                    timeout=10
                )

            end_time = time.time()
            result["execution_time"] = end_time - start_time
            result["output"] = process.stdout
            result["error"] = process.stderr

            if process.returncode == 0:
                result["status"] = "PASSED"
            else:
                result["status"] = "FAILED"

        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["error"] = "Test timeout"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def execute_unit_test(self, test_case: Dict) -> Dict:
        """Execute unit test"""
        result = {
            "status": "UNKNOWN",
            "output": "",
            "error": "",
            "execution_time": 0
        }

        try:
            start_time = time.time()

            cmd = test_case["test_command"]
            process = subprocess.run(
                cmd.split(),
                text=True,
                capture_output=True,
                timeout=30
            )

            end_time = time.time()
            result["execution_time"] = end_time - start_time
            result["output"] = process.stdout
            result["error"] = process.stderr

            if process.returncode == 0 and "PASSED" in process.stdout:
                result["status"] = "PASSED"
            else:
                result["status"] = "FAILED"

        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["error"] = "Test timeout"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def execute_file_comparison_test(self, test_case: Dict, expected_files: List[str]) -> Dict:
        """Execute file comparison test"""
        result = {
            "status": "UNKNOWN",
            "output": "",
            "error": "",
            "execution_time": 0
        }

        try:
            start_time = time.time()

            # First execute command to generate files
            cmd = test_case["test_command"]
            test_input_file = test_case.get("test_input")

            if test_input_file and os.path.exists(test_input_file):
                with open(test_input_file, 'r') as f:
                    input_data = f.read()

                process = subprocess.run(
                    cmd.split(),
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=10
                )
            else:
                process = subprocess.run(
                    cmd.split(),
                    text=True,
                    capture_output=True,
                    timeout=10
                )

            end_time = time.time()
            result["execution_time"] = end_time - start_time
            result["output"] = process.stdout
            result["error"] = process.stderr

            # Check if expected files exist
            if expected_files:
                files_exist = all(os.path.exists(f) for f in expected_files)
                if files_exist:
                    result["status"] = "PASSED"
                else:
                    result["status"] = "FAILED"
                    result["error"] = "Expected output files do not exist"
            else:
                result["status"] = "PASSED" if process.returncode == 0 else "FAILED"

        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["error"] = "Test timeout"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)

        return result

    def execute_test(self, test_item: Dict) -> Dict:
        """Execute single test"""
        print(f"Executing test: {test_item['metric']}")

        test_result = {
            "metric": test_item["metric"],
            "type": test_item["type"],
            "status": "UNKNOWN",
            "details": [],
            "execution_time": 0,
            "error_message": ""
        }

        total_time = 0
        all_passed = True

        for test_case in test_item["testcases"]:
            if test_item["type"] == "shell_interaction":
                result = self.execute_shell_interaction_test(test_case)
            elif test_item["type"] == "unit_test":
                result = self.execute_unit_test(test_case)
            elif test_item["type"] == "file_comparison":
                expected_files = test_item.get("expected_output_files", [])
                result = self.execute_file_comparison_test(test_case, expected_files)
            else:
                result = {"status": "ERROR", "error": "Unknown test type"}

            test_result["details"].append(result)
            total_time += result.get("execution_time", 0)

            if result["status"] != "PASSED":
                all_passed = False
                test_result["error_message"] += f"{result.get('error', '')} "

        test_result["execution_time"] = total_time
        test_result["status"] = "PASSED" if all_passed else "FAILED"

        return test_result

    def run_all_tests(self):
        """Run all tests"""
        print("Starting automated tests...")
        print("="*60)

        test_plan = self.load_test_plan()
        if not test_plan:
            print("Cannot load test plan, exiting")
            return

        self.total_tests = len(test_plan)
        start_time = time.time()

        for test_item in test_plan:
            result = self.execute_test(test_item)
            self.results.append(result)

            if result["status"] == "PASSED":
                self.passed_tests += 1
                print(f"✓ {result['metric']} - PASSED")
            else:
                self.failed_tests += 1
                print(f"✗ {result['metric']} - FAILED")
                if result["error_message"]:
                    print(f"  Error: {result['error_message']}")

        end_time = time.time()
        total_execution_time = end_time - start_time

        print("="*60)
        print(f"Tests completed! Total time: {total_execution_time:.2f} seconds")
        print(f"Total tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Pass rate: {(self.passed_tests/self.total_tests*100):.1f}%")

        # Generate detailed report
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        report = {
            "test_execution_report": {
                "execution_date": datetime.now().isoformat(),
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "pass_rate": f"{(self.passed_tests/self.total_tests*100):.1f}%",
                "test_results": self.results
            }
        }

        report_file = "evaluation/test_execution_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"Detailed test report saved to: {report_file}")
        except Exception as e:
            print(f"Failed to save test report: {e}")

def main():
    """Main function"""
    if not os.path.exists("evaluation/detailed_test_plan.json"):
        print("Error: Cannot find test plan file evaluation/detailed_test_plan.json")
        sys.exit(1)

    executor = TestExecutor()
    executor.run_all_tests()

if __name__ == "__main__":
    main()
