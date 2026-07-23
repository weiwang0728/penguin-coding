#!/usr/bin/env python3
"""
Agent Test Interface

This module provides automated testing interface for LLM agents
to evaluate the IoT Environmental System implementation.
"""

import json
import subprocess
import os
import sys
import time
import csv
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgentTestInterface:
    """
    Automated testing interface for LLM agents.
    
    Provides methods to execute test cases and evaluate system functionality
    based on the detailed test plan.
    """
    
    def __init__(self, project_root: str = ".."):
        """
        Initialize test interface.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.test_results = []
        self.total_score = 0
        self.max_score = 0
        
        # Load test plan
        self.test_plan = self._load_test_plan()
        
        logger.info(f"Agent Test Interface initialized for project: {self.project_root}")
    
    def _load_test_plan(self) -> Dict[str, Any]:
        """Load detailed test plan from JSON file."""
        try:
            test_plan_file = self.project_root / "evaluation" / "detailed_test_plan.json"
            with open(test_plan_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load test plan: {e}")
            return {}
    
    def _load_metrics(self) -> List[Dict[str, Any]]:
        """Load evaluation metrics from JSON file."""
        try:
            metrics_file = self.project_root / "evaluation" / "metric.json"
            with open(metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return []
    
    def execute_command(self, command: str, timeout: int = 30, 
                       working_dir: str = None) -> Tuple[bool, str, str]:
        """
        Execute shell command and return results.
        
        Args:
            command: Command to execute
            timeout: Command timeout in seconds
            working_dir: Working directory for command execution
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            if working_dir:
                cwd = self.project_root / working_dir
            else:
                cwd = self.project_root
            
            logger.info(f"Executing command: {command}")
            logger.info(f"Working directory: {cwd}")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            logger.info(f"Command result: success={success}, stdout_length={len(stdout)}")
            if stderr:
                logger.warning(f"Command stderr: {stderr}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout after {timeout} seconds")
            return False, "", f"Command timeout after {timeout} seconds"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return False, "", str(e)
    
    def check_file_exists(self, file_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path: Relative path to file
            
        Returns:
            True if file exists, False otherwise
        """
        full_path = self.project_root / file_path
        exists = full_path.exists()
        logger.info(f"File check: {file_path} - {'EXISTS' if exists else 'NOT FOUND'}")
        return exists
    
    def read_file_content(self, file_path: str) -> str:
        """
        Read file content.
        
        Args:
            file_path: Relative path to file
            
        Returns:
            File content as string
        """
        try:
            full_path = self.project_root / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Read file: {file_path} - {len(content)} characters")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return ""
    
    def validate_csv_data(self, file_path: str, expected_columns: List[str],
                         data_ranges: Dict[str, Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Validate CSV data format and ranges.
        
        Args:
            file_path: Path to CSV file
            expected_columns: List of expected column names
            data_ranges: Dictionary of column ranges {column: {min: x, max: y}}
            
        Returns:
            Validation results dictionary
        """
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                return {"valid": False, "error": "File not found"}
            
            # Read CSV
            with open(full_path, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                return {"valid": False, "error": "Empty CSV file"}
            
            # Check columns
            actual_columns = set(rows[0].keys())
            missing_columns = set(expected_columns) - actual_columns
            
            if missing_columns:
                return {
                    "valid": False, 
                    "error": f"Missing columns: {missing_columns}"
                }
            
            # Validate data ranges if provided
            range_violations = []
            if data_ranges:
                for row in rows[:10]:  # Check first 10 rows
                    for column, ranges in data_ranges.items():
                        if column in row:
                            try:
                                value = float(row[column])
                                if value < ranges['min'] or value > ranges['max']:
                                    range_violations.append(
                                        f"{column}={value} outside range [{ranges['min']}, {ranges['max']}]"
                                    )
                            except ValueError:
                                range_violations.append(f"{column} has non-numeric value: {row[column]}")
            
            result = {
                "valid": len(range_violations) == 0,
                "row_count": len(rows),
                "columns": list(actual_columns),
                "range_violations": range_violations[:5]  # First 5 violations
            }
            
            logger.info(f"CSV validation: {file_path} - {'VALID' if result['valid'] else 'INVALID'}")
            return result
            
        except Exception as e:
            logger.error(f"CSV validation failed for {file_path}: {e}")
            return {"valid": False, "error": str(e)}
    
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_case: Test case dictionary from test plan
            
        Returns:
            Test result dictionary
        """
        test_id = test_case.get('test_id', 'UNKNOWN')
        test_name = test_case.get('test_name', 'Unknown Test')
        weight = test_case.get('weight', 1)
        
        logger.info(f"Running test case: {test_id} - {test_name}")
        
        result = {
            'test_id': test_id,
            'test_name': test_name,
            'weight': weight,
            'success': False,
            'score': 0,
            'max_score': 2 * weight,
            'details': [],
            'errors': []
        }
        
        try:
            test_steps = test_case.get('test_steps', [])
            success_criteria = test_case.get('success_criteria', [])
            
            step_results = []
            
            for step in test_steps:
                step_result = self._execute_test_step(step)
                step_results.append(step_result)
                result['details'].append(step_result)
            
            # Evaluate success based on criteria
            success_count = sum(1 for step in step_results if step.get('success', False))
            total_steps = len(step_results)
            
            if total_steps == 0:
                result['score'] = 0
            elif success_count == total_steps:
                result['score'] = 2 * weight  # Full score
                result['success'] = True
            elif success_count > 0:
                result['score'] = 1 * weight  # Partial score
            else:
                result['score'] = 0  # No score
            
            logger.info(f"Test {test_id} completed: score={result['score']}/{result['max_score']}")
            
        except Exception as e:
            logger.error(f"Test case {test_id} failed: {e}")
            result['errors'].append(str(e))
            result['score'] = 0
        
        return result
    
    def _execute_test_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test step.
        
        Args:
            step: Test step dictionary
            
        Returns:
            Step execution result
        """
        action = step.get('action', 'unknown')
        
        if action == 'execute_command':
            return self._execute_command_step(step)
        elif action == 'read_file':
            return self._execute_read_file_step(step)
        elif action == 'check_files':
            return self._execute_check_files_step(step)
        elif action == 'validate_data_ranges':
            return self._execute_validate_data_step(step)
        elif action == 'interactive_cli':
            return self._execute_interactive_cli_step(step)
        else:
            return {
                'action': action,
                'success': False,
                'error': f'Unknown action: {action}'
            }
    
    def _execute_command_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute command step."""
        command = step.get('command', '')
        expected_output = step.get('expected_output', '')
        timeout = step.get('timeout', 30)
        
        success, stdout, stderr = self.execute_command(command, timeout)
        
        return {
            'action': 'execute_command',
            'command': command,
            'success': success,
            'stdout': stdout[:500],  # Limit output length
            'stderr': stderr[:500],
            'expected_output': expected_output
        }
    
    def _execute_read_file_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute read file step."""
        file_path = step.get('file_path', '')
        expected_content = step.get('expected_content', '')
        
        content = self.read_file_content(file_path)
        success = len(content) > 0
        
        return {
            'action': 'read_file',
            'file_path': file_path,
            'success': success,
            'content_length': len(content),
            'expected_content': expected_content
        }
    
    def _execute_check_files_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file check step."""
        file_pattern = step.get('file_pattern', '')
        
        # Simple file pattern check (could be enhanced with glob)
        if '*' in file_pattern:
            # Handle wildcard patterns
            import glob
            pattern_path = str(self.project_root / file_pattern)
            matching_files = glob.glob(pattern_path)
            success = len(matching_files) > 0
            
            return {
                'action': 'check_files',
                'file_pattern': file_pattern,
                'success': success,
                'matching_files': matching_files[:10]  # Limit to first 10
            }
        else:
            # Single file check
            success = self.check_file_exists(file_pattern)
            return {
                'action': 'check_files',
                'file_pattern': file_pattern,
                'success': success
            }
    
    def _execute_validate_data_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data validation step."""
        validation_rules = step.get('validation_rules', {})
        
        # Validate sample data file
        validation_result = self.validate_csv_data(
            "src/samples/environmental_sample.csv",
            ["timestamp", "temperature", "humidity", "pressure"],
            validation_rules
        )
        
        return {
            'action': 'validate_data_ranges',
            'success': validation_result.get('valid', False),
            'validation_result': validation_result
        }
    
    def _execute_interactive_cli_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute interactive CLI step (simplified implementation)."""
        command = step.get('command', '')
        interactions = step.get('interactions', [])
        
        # For this implementation, we'll simulate the interactive test
        # In a real scenario, this would use pexpect or similar library
        
        logger.info(f"Simulating interactive CLI: {command}")
        logger.info(f"Expected interactions: {len(interactions)}")
        
        # Try to execute the command with timeout to see if it starts
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.project_root,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit to see if process starts
            time.sleep(2)
            
            if process.poll() is None:
                # Process is still running, likely waiting for input
                process.terminate()
                success = True
                message = "Interactive command started successfully"
            else:
                # Process ended, check if it was successful
                stdout, stderr = process.communicate()
                success = process.returncode == 0
                message = f"Command completed: {stdout[:200]}"
            
        except Exception as e:
            success = False
            message = f"Interactive command failed: {e}"
        
        return {
            'action': 'interactive_cli',
            'command': command,
            'success': success,
            'message': message,
            'interactions_count': len(interactions)
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test cases from the test plan.
        
        Returns:
            Complete test results dictionary
        """
        logger.info("Starting automated test execution")
        
        test_cases = self.test_plan.get('test_cases', [])
        
        if not test_cases:
            logger.error("No test cases found in test plan")
            return {'error': 'No test cases found'}
        
        # Run pre-test setup
        self._run_pre_test_setup()
        
        # Execute all test cases
        for test_case in test_cases:
            result = self.run_test_case(test_case)
            self.test_results.append(result)
            
            self.total_score += result['score']
            self.max_score += result['max_score']
        
        # Generate final report
        final_report = self._generate_final_report()
        
        logger.info(f"All tests completed. Final score: {self.total_score}/{self.max_score}")
        
        return final_report
    
    def _run_pre_test_setup(self) -> None:
        """Run pre-test setup steps."""
        logger.info("Running pre-test setup")
        
        setup_steps = self.test_plan.get('pre_test_setup', [])
        
        for step in setup_steps:
            command = step.get('command', '')
            description = step.get('description', '')
            
            logger.info(f"Setup step: {description}")
            
            success, stdout, stderr = self.execute_command(command, timeout=60)
            
            if not success:
                logger.warning(f"Setup step failed: {description}")
                logger.warning(f"Error: {stderr}")
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final test report."""
        
        # Calculate scores by category
        category_scores = {}
        scoring_rules = self.test_plan.get('scoring_rules', {})
        
        for result in self.test_results:
            test_case = next((tc for tc in self.test_plan.get('test_cases', []) 
                            if tc.get('test_id') == result['test_id']), {})
            category = test_case.get('category', 'Unknown')
            
            if category not in category_scores:
                category_scores[category] = {'score': 0, 'max_score': 0, 'tests': 0}
            
            category_scores[category]['score'] += result['score']
            category_scores[category]['max_score'] += result['max_score']
            category_scores[category]['tests'] += 1
        
        # Calculate percentage score
        percentage_score = (self.total_score / self.max_score * 100) if self.max_score > 0 else 0
        
        # Determine grade
        grade_mapping = scoring_rules.get('grade_mapping', {})
        grade = 'F'
        for score_range, grade_value in grade_mapping.items():
            min_score, max_score = map(int, score_range.split('-'))
            if min_score <= percentage_score <= max_score:
                grade = grade_value.split('(')[1].rstrip(')')
                break
        
        report = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for r in self.test_results if r['success']),
                'failed_tests': sum(1 for r in self.test_results if not r['success']),
                'total_score': self.total_score,
                'max_possible_score': self.max_score,
                'percentage_score': round(percentage_score, 2),
                'grade': grade
            },
            'category_breakdown': category_scores,
            'detailed_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if not r['success']]
        
        if not failed_tests:
            recommendations.append("All tests passed! System implementation is complete and functions are normal.")
        else:
            recommendations.append(f"There are {len(failed_tests)} test(s) that did not pass. Improvements needed in the following areas:")

            for test in failed_tests:
                recommendations.append(f"- {test['test_name']}: Check related function implementation")

        # Check specific patterns
        mqtt_tests = [r for r in self.test_results if 'MQTT' in r['test_name'] and not r['success']]
        if mqtt_tests:
            recommendations.append("MQTT functions require configuration of Alibaba Cloud IoT platform credentials for full automated testing")

        ml_tests = [r for r in self.test_results if 'Machine Learning' in r['test_name'] or 'ML' in r['test_name'] and not r['success']]
        if ml_tests:
            recommendations.append("Machine learning functions may require more training data or parameter adjustment")
        
        return recommendations
    
    def save_report(self, output_file: str = "evaluation/test_report.json") -> bool:
        """
        Save test report to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            report = self._generate_final_report()
            
            output_path = self.project_root / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Test report saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return False


def main():
    """Main function for running automated tests."""
    print("=" * 60)
    print(" IoT Environmental System - Automated Testing")
    print(" Agent Test Interface")
    print("=" * 60)
    
    # Initialize test interface
    test_interface = AgentTestInterface()
    
    # Run all tests
    results = test_interface.run_all_tests()
    
    # Save report
    test_interface.save_report()
    
    # Print summary
    summary = results.get('test_summary', {})
    print(f"\n📊 Test Results Summary:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Passed: {summary.get('passed_tests', 0)}")
    print(f"   Failed: {summary.get('failed_tests', 0)}")
    print(f"   Score: {summary.get('total_score', 0)}/{summary.get('max_possible_score', 0)}")
    print(f"   Percentage: {summary.get('percentage_score', 0):.1f}%")
    print(f"   Grade: {summary.get('grade', 'N/A')}")
    
    # Print recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    return results


if __name__ == "__main__":
    main()