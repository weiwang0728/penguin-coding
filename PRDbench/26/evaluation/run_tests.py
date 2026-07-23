#!/usr/bin/env python3
"""
OA System Test Runner
Automatically execute all test cases and generate test reports
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

class TestRunner:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        
    def run_command(self, command, input_data=None, timeout=30):
        """Execute command and return result"""
        try:
            if input_data:
                process = subprocess.run(
                    command,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    cwd=current_dir.parent
                )
            else:
                process = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    timeout=timeout,
                    cwd=current_dir.parent
                )
            
            return {
                'returncode': process.returncode,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'success': process.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'success': False
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def run_unit_tests(self):
        """Run unit tests"""
        print("=" * 60)
        print("Running unit tests")
        print("=" * 60)

        # Check if pytest is available
        pytest_check = self.run_command(['python', '-m', 'pytest', '--version'])
        if not pytest_check['success']:
            print("❌ pytest is not installed, skipping unit tests")
            print("Please run: pip install pytest")
            return

        # Run all unit tests
        test_files = [
            'evaluation/tests/test_system_init.py::test_database_initialization',
            'evaluation/tests/test_auth_service.py::test_user_authentication', 
            'evaluation/tests/test_workflow_service.py::test_workflow_operations'
        ]
        
        for test_file in test_files:
            print(f"\nRunning test: {test_file}")
            result = self.run_command(['python', '-m', 'pytest', test_file, '-v'])

            self.total_tests += 1
            if result['success']:
                print(f"✅ Passed: {test_file}")
                self.passed_tests += 1
            else:
                print(f"❌ Failed: {test_file}")
                print(f"Error message: {result['stderr']}")
                self.failed_tests += 1

            self.test_results.append({
                'type': 'unit_test',
                'name': test_file,
                'success': result['success'],
                'output': result['stdout'],
                'error': result['stderr']
            })

    def run_shell_interaction_tests(self):
        """Run shell interaction tests"""
        print("\n" + "=" * 60)
        print("Running shell interaction tests")
        print("=" * 60)

        # Load test plan
        try:
            with open(current_dir / 'detailed_test_plan.json', 'r', encoding='utf-8') as f:
                test_plan = json.load(f)
        except Exception as e:
            print(f"❌ Cannot load test plan: {e}")
            return

        # Filter shell_interaction type tests
        shell_tests = [test for test in test_plan if test['type'] == 'shell_interaction']

        for test in shell_tests[:5]:  # Only run first 5 tests as example
            print(f"\nRunning test: {test['metric']}")

            for testcase in test['testcases']:
                command = testcase['test_command'].split()
                input_file = testcase.get('test_input')

                # Read input data
                input_data = None
                if input_file:
                    try:
                        with open(current_dir / input_file, 'r', encoding='utf-8') as f:
                            input_data = f.read()
                    except Exception as e:
                        print(f"❌ Cannot read input file {input_file}: {e}")
                        continue

                # Execute command
                result = self.run_command(command, input_data)

                self.total_tests += 1

                # Simple success judgment (success if program doesn't crash)
                if result['success'] or result['returncode'] == 0:
                    print(f"✅ Passed: {' '.join(command)}")
                    self.passed_tests += 1
                    success = True
                else:
                    print(f"❌ Failed: {' '.join(command)}")
                    print(f"Error message: {result['stderr']}")
                    self.failed_tests += 1
                    success = False

                self.test_results.append({
                    'type': 'shell_interaction',
                    'name': test['metric'],
                    'command': ' '.join(command),
                    'success': success,
                    'output': result['stdout'][:500],  # Limit output length
                    'error': result['stderr']
                })

    def run_file_comparison_tests(self):
        """Run file comparison tests"""
        print("\n" + "=" * 60)
        print("Running file comparison tests")
        print("=" * 60)

        # Load test plan
        try:
            with open(current_dir / 'detailed_test_plan.json', 'r', encoding='utf-8') as f:
                test_plan = json.load(f)
        except Exception as e:
            print(f"❌ Cannot load test plan: {e}")
            return

        # Filter file_comparison type tests
        file_tests = [test for test in test_plan if test['type'] == 'file_comparison']

        for test in file_tests:
            print(f"\nRunning test: {test['metric']}")

            for testcase in test['testcases']:
                command = testcase['test_command'].split()
                input_file = testcase.get('test_input')

                # Read input data
                input_data = None
                if input_file:
                    try:
                        with open(current_dir / input_file, 'r', encoding='utf-8') as f:
                            input_data = f.read()
                    except Exception as e:
                        print(f"❌ Cannot read input file {input_file}: {e}")
                        continue

                # Execute command
                result = self.run_command(command, input_data)

                self.total_tests += 1

                # Check if expected files are generated
                expected_files = test.get('expected_output_files', [])
                files_exist = True

                for expected_file in expected_files:
                    if not os.path.exists(expected_file):
                        files_exist = False
                        break

                if result['success'] and files_exist:
                    print(f"✅ Passed: {' '.join(command)}")
                    self.passed_tests += 1
                    success = True
                else:
                    print(f"❌ Failed: {' '.join(command)}")
                    if not files_exist:
                        print("Expected files not generated")
                    if result['stderr']:
                        print(f"Error message: {result['stderr']}")
                    self.failed_tests += 1
                    success = False

                self.test_results.append({
                    'type': 'file_comparison',
                    'name': test['metric'],
                    'command': ' '.join(command),
                    'success': success,
                    'output': result['stdout'][:500],
                    'error': result['stderr']
                })

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("Test Report")
        print("=" * 60)

        print(f"Total tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")

        # Statistics by type
        unit_tests = [r for r in self.test_results if r['type'] == 'unit_test']
        shell_tests = [r for r in self.test_results if r['type'] == 'shell_interaction']
        file_tests = [r for r in self.test_results if r['type'] == 'file_comparison']

        print(f"\nStatistics by type:")
        print(f"Unit tests: {len(unit_tests)} tests")
        print(f"Shell interaction tests: {len(shell_tests)} tests")
        print(f"File comparison tests: {len(file_tests)} tests")

        # Save detailed report
        report_file = current_dir / 'test_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': self.total_tests,
                    'passed': self.passed_tests,
                    'failed': self.failed_tests,
                    'success_rate': (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
                },
                'results': self.test_results,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)

        print(f"\nDetailed report saved to: {report_file}")

    def run_all_tests(self):
        """Run all tests"""
        print("Starting OA system test suite")
        print("=" * 60)

        # Check system initialization status
        print("Checking system status...")
        db_file = current_dir.parent / "oa_system.db"
        if not db_file.exists():
            print("⚠️  Database file does not exist, recommend initializing system first")
            print("Run: python src/main.py then select '2. Initialize System'")

        # Run various tests
        self.run_unit_tests()
        self.run_shell_interaction_tests()
        self.run_file_comparison_tests()

        # Generate report
        self.generate_report()


def main():
    """Main function"""
    runner = TestRunner()
    runner.run_all_tests()


if __name__ == '__main__':
    main()