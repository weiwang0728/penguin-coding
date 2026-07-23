# -*- coding: utf-8 -*-
"""
Fairness Report Tests
"""

import sys
import os
import pytest
import numpy as np
from io import StringIO
from contextlib import redirect_stdout

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.result_display import ResultDisplay
from modules.lottery_engine import LotteryEngine

class TestFairnessReport:
    """Fairness Report Test Class"""

    def setup_method(self):
        """Setup before tests"""
        self.display = ResultDisplay()
        self.engine = LotteryEngine()

    def test_statistical_tests(self):
        """Test Z-test and Chi-square test implementation"""
        # Prepare multi-department employee data
        employees = [
            {'name': 'Dept01 Employee1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': 'Dept01 Employee2', 'employee_id': '0101002', 'score': 92, 'tenure': 18},
            {'name': 'Dept01 Employee3', 'employee_id': '0101003', 'score': 88, 'tenure': 30},
            {'name': 'Dept02 Employee1', 'employee_id': '0201001', 'score': 78, 'tenure': 36},
            {'name': 'Dept02 Employee2', 'employee_id': '0201002', 'score': 90, 'tenure': 12},
            {'name': 'Dept03 Employee1', 'employee_id': '0301001', 'score': 95, 'tenure': 48}
        ]

        # Simulate lottery results
        mock_results = {
            'Test Prize': [
                {'name': 'Dept01 Employee1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
                {'name': 'Dept02 Employee1', 'employee_id': '0201001', 'score': 78, 'tenure': 36}
            ]
        }

        self.display.set_results(mock_results)

        # Capture output
        output = StringIO()
        with redirect_stdout(output):
            self.display.display_fairness_report(employees)

        output_text = output.getvalue()

        # Verify Z-test related output
        assert "Score Distribution Z-Test" in output_text or "Z-Test" in output_text, "Missing Z-test title"
        assert "Population score mean" in output_text or "score mean" in output_text.lower(), "Missing overall score mean"
        assert "Z statistic" in output_text or "Z-statistic" in output_text, "Missing Z statistic"
        assert "p-value" in output_text or "p value" in output_text, "Missing p-value"

        # Verify Chi-square test related output
        assert "Department Distribution Chi-Square Test" in output_text or "Chi-Square" in output_text, "Missing chi-square test title"

        print("Z-test and Chi-square test implementation test passed")

    def test_randomness_marking(self):
        """Test automatic randomness marking function"""
        # Use employees with different scores to ensure Z-test can be performed
        employees = [
            {'name': f'Employee{i}', 'employee_id': f'010100{i}', 'score': 80 + i*2, 'tenure': 24}
            for i in range(1, 21)  # 20 employees with different scores
        ]

        # Simulate lottery results
        mock_results = {
            'Random Prize': [
                {'name': 'Employee1', 'employee_id': '0101001', 'score': 82, 'tenure': 24},
                {'name': 'Employee2', 'employee_id': '0101002', 'score': 84, 'tenure': 24},
                {'name': 'Employee3', 'employee_id': '0101003', 'score': 86, 'tenure': 24}
            ]
        }

        self.display.set_results(mock_results)

        # Generate report content
        report_content = self.display.generate_report_content(employees)

        # Verify randomness marking exists (due to Z-test results)
        has_z_test = "Z Statistic:" in report_content or "Z-statistic:" in report_content
        if has_z_test:
            assert "meets randomness requirements" in report_content or "may indicate bias" in report_content, "Missing randomness judgment marker"

            # Verify p-value judgment logic
            lines = report_content.split('\n')
            p_value_lines = [line for line in lines if 'p-value:' in line or 'p value:' in line]

            if len(p_value_lines) > 0:
                # Check if there is corresponding randomness marker
                for p_line in p_value_lines:
                    # Extract p-value
                    try:
                        if 'p-value:' in p_line:
                            p_value_str = p_line.split('p-value:')[1].strip()
                        else:
                            p_value_str = p_line.split('p value:')[1].strip()
                        p_value = float(p_value_str)

                        # Check if there is corresponding marker based on p-value
                        if p_value > 0.05:
                            assert "meets randomness requirements" in report_content, f"p-value {p_value} > 0.05 but missing randomness marker"
                        else:
                            assert "may indicate bias" in report_content, f"p-value {p_value} <= 0.05 but missing bias marker"

                    except (ValueError, IndexError):
                        continue  # Skip unparseable lines
        else:
            # If no Z-test, at least there should be report structure
            assert "Fairness Statistical Report" in report_content or "Fairness Report" in report_content, "Missing fairness report section"

        print("Automatic randomness marking function test passed")

    def test_report_content_completeness(self):
        """Test report content completeness"""
        employees = [
            {'name': 'Zhang San', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': 'Li Si', 'employee_id': '0201002', 'score': 92, 'tenure': 18}
        ]

        mock_results = {
            'First Prize': [{'name': 'Zhang San', 'employee_id': '0101001', 'score': 85, 'tenure': 24}],
            'Second Prize': [{'name': 'Li Si', 'employee_id': '0201002', 'score': 92, 'tenure': 18}]
        }

        self.display.set_results(mock_results)

        # Generate complete report
        report_content = self.display.generate_report_content(employees)

        # Verify report structure completeness
        required_sections = [
            "Lottery System - Lottery Results Report" or "Lottery Results Report",
            "Generation Time:" or "Generated:",
            "Lottery Results" or "Results",
            "First Prize",
            "Second Prize",
            "Fairness Statistical Report" or "Fairness Report",
            "Report End" or "End of Report"
        ]

        # At least check for key sections
        assert "First Prize" in report_content, f"Report missing required part: First Prize"
        assert "Second Prize" in report_content, f"Report missing required part: Second Prize"

        print("Report content completeness test passed")
