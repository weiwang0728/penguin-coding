#!/usr/bin/env python3
"""
Test Execution Script

Comprehensive test runner for the IoT Environmental System evaluation.
Executes all test types: shell_interaction, unit_test, and file_comparison.
"""

import json
import subprocess
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestRunner:
    """Comprehensive test runner for all evaluation metrics."""
    
    def __init__(self):
        """Initialize test runner."""
        self.project_root = Path(__file__).parent.parent
        self.evaluation_dir = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        
        # Load test plan
        self.test_plan = self._load_test_plan()
        self.results = []
        
        logger.info(f"Test runner initialized - Project root: {self.project_root}")
    
    def _load_test_plan(self) -> List[Dict[str, Any]]:
        """Load detailed test plan."""
        try:
            with open(self.evaluation_dir / "detailed_test_plan.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load test plan: {e}")
            return []
    
    def run_shell_interaction_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run shell interaction test."""
        metric = test_case['metric']
        testcases = test_case['testcases']
        
        logger.info(f"Running shell interaction test: {metric}")
        
        results = []
        overall_success = True
        
        for i, testcase in enumerate(testcases):
            command = testcase['test_command']
            test_input = testcase.get('test_input')
            
            logger.info(f"Executing command {i+1}/{len(testcases)}: {command}")
            
            try:
                # Handle input file if specified
                stdin_input = None
                if test_input and test_input != "null":
                    input_file_path = self.evaluation_dir / test_input
                    if input_file_path.exists():
                        with open(input_file_path, 'r') as f:
                            stdin_input = f.read()
                
                # Execute command
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    input=stdin_input,
                    timeout=60
                )
                
                success = result.returncode == 0
                if not success:
                    overall_success = False
                
                results.append({
                    'command': command,
                    'success': success,
                    'returncode': result.returncode,
                    'stdout_length': len(result.stdout),
                    'stderr_length': len(result.stderr),
                    'stdout_preview': result.stdout[:200],
                    'stderr_preview': result.stderr[:200]
                })
                
                logger.info(f"Command result: success={success}, returncode={result.returncode}")
                
            except subprocess.TimeoutExpired:
                logger.error(f"Command timeout: {command}")
                overall_success = False
                results.append({
                    'command': command,
                    'success': False,
                    'error': 'Timeout'
                })
            except Exception as e:
                logger.error(f"Command failed: {command} - {e}")
                overall_success = False
                results.append({
                    'command': command,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'metric': metric,
            'type': 'shell_interaction',
            'overall_success': overall_success,
            'command_results': results
        }
    
    def run_unit_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run unit test."""
        metric = test_case['metric']
        testcases = test_case['testcases']
        
        logger.info(f"Running unit test: {metric}")
        
        results = []
        overall_success = True
        
        for testcase in testcases:
            command = testcase['test_command']
            
            logger.info(f"Executing pytest command: {command}")
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.evaluation_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                success = result.returncode == 0
                if not success:
                    overall_success = False
                
                results.append({
                    'command': command,
                    'success': success,
                    'returncode': result.returncode,
                    'stdout_preview': result.stdout[:500],
                    'stderr_preview': result.stderr[:500]
                })
                
                logger.info(f"Pytest result: success={success}")
                
            except subprocess.TimeoutExpired:
                logger.error(f"Pytest timeout: {command}")
                overall_success = False
                results.append({
                    'command': command,
                    'success': False,
                    'error': 'Timeout'
                })
            except Exception as e:
                logger.error(f"Pytest failed: {command} - {e}")
                overall_success = False
                results.append({
                    'command': command,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'metric': metric,
            'type': 'unit_test',
            'overall_success': overall_success,
            'test_results': results
        }
    
    def run_file_comparison_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run file comparison test."""
        metric = test_case['metric']
        testcases = test_case['testcases']
        expected_files = test_case.get('expected_output_files', [])
        
        logger.info(f"Running file comparison test: {metric}")
        
        results = []
        overall_success = True
        
        for testcase in testcases:
            command = testcase['test_command']
            
            logger.info(f"Executing file generation command: {command}")
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                command_success = result.returncode == 0
                
                # For file comparison, also check if expected files exist
                file_comparison_success = True
                if expected_files:
                    for expected_file in expected_files:
                        expected_path = self.evaluation_dir / expected_file
                        if not expected_path.exists():
                            file_comparison_success = False
                            logger.warning(f"Expected file not found: {expected_file}")
                
                success = command_success and file_comparison_success
                if not success:
                    overall_success = False
                
                results.append({
                    'command': command,
                    'command_success': command_success,
                    'file_comparison_success': file_comparison_success,
                    'success': success,
                    'stdout_preview': result.stdout[:300],
                    'expected_files': expected_files
                })
                
                logger.info(f"File comparison result: success={success}")
                
            except Exception as e:
                logger.error(f"File comparison failed: {command} - {e}")
                overall_success = False
                results.append({
                    'command': command,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'metric': metric,
            'type': 'file_comparison',
            'overall_success': overall_success,
            'comparison_results': results
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests from the test plan."""
        logger.info("Starting comprehensive test execution")
        
        if not self.test_plan:
            logger.error("No test plan loaded")
            return {'error': 'No test plan available'}
        
        total_tests = len(self.test_plan)
        passed_tests = 0
        
        for i, test_case in enumerate(self.test_plan):
            test_type = test_case.get('type', 'unknown')
            metric = test_case.get('metric', f'Test {i+1}')
            
            logger.info(f"Running test {i+1}/{total_tests}: {metric}")
            
            try:
                if test_type == 'shell_interaction':
                    result = self.run_shell_interaction_test(test_case)
                elif test_type == 'unit_test':
                    result = self.run_unit_test(test_case)
                elif test_type == 'file_comparison':
                    result = self.run_file_comparison_test(test_case)
                else:
                    logger.warning(f"Unknown test type: {test_type}")
                    result = {
                        'metric': metric,
                        'type': test_type,
                        'overall_success': False,
                        'error': f'Unknown test type: {test_type}'
                    }
                
                if result.get('overall_success', False):
                    passed_tests += 1
                
                self.results.append(result)
                
            except Exception as e:
                logger.error(f"Test execution failed: {metric} - {e}")
                self.results.append({
                    'metric': metric,
                    'type': test_type,
                    'overall_success': False,
                    'error': str(e)
                })
        
        # Generate summary
        summary = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'detailed_results': self.results
        }
        
        logger.info(f"Test execution completed: {passed_tests}/{total_tests} passed")
        
        return summary
    
    def save_results(self, results: Dict[str, Any], output_file: str = "test_execution_results.json"):
        """Save test results to file."""
        try:
            output_path = self.evaluation_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Test results saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return False


def main():
    """Main function."""
    print("=" * 60)
    print(" IoT Environmental System - Comprehensive Test Runner")
    print("=" * 60)
    
    runner = TestRunner()
    
    # Run all tests
    results = runner.run_all_tests()
    
    # Save results
    runner.save_results(results)
    
    # Print summary
    summary = results
    print(f"\n📊 Test Execution Summary:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Passed: {summary.get('passed_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
    
    # Print failed tests
    failed_tests = [r for r in summary.get('detailed_results', []) if not r.get('overall_success', False)]
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"   • {test.get('metric', 'Unknown')}")
    
    return 0 if summary.get('success_rate', 0) >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())