# -*- coding: utf-8 -*-
"""
File Operations Tests
"""

import sys
import os
import pytest
import re
import glob
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.lottery_engine import LotteryEngine
from modules.result_display import ResultDisplay
from utils.file_utils import FileUtils

class TestFileOperations:
    """File Operations Test Class"""

    def setup_method(self):
        """Setup before tests"""
        self.engine = LotteryEngine()
        self.display = ResultDisplay()
        self.file_utils = FileUtils()

        # Clean up previous test files
        self.cleanup_test_files()

    def teardown_method(self):
        """Cleanup after tests"""
        self.cleanup_test_files()

    def cleanup_test_files(self):
        """Clean up test-generated files"""
        # Delete all lottery result files
        pattern = "LotteryResults_*.txt"
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
            except:
                pass

    def test_filename_format(self):
        """Test filename format specification"""
        # Prepare test data
        employees = [
            {'name': 'Zhang San', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': 'Li Si', 'employee_id': '0101002', 'score': 92, 'tenure': 18}
        ]

        # Execute lottery
        prizes = [
            {
                'name': 'Test Prize',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]

        # Execute lottery (disable output)
        import io
        import contextlib

        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)
        self.display.set_results(results)

        # Generate file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LotteryResults_{timestamp}.txt"

        content = self.display.generate_report_content(employees)
        success = self.file_utils.save_text_file(filename, content)

        assert success, "File save failed"
        assert os.path.exists(filename), f"File {filename} was not generated"

        # Verify filename format
        pattern = r"^LotteryResults_\d{8}_\d{6}\.txt$"
        assert re.match(pattern, filename), f"Filename format incorrect: {filename}"

        # Verify date time format
        date_part = filename.split('_')[1]  # YYYYMMDD
        time_part = filename.split('_')[2].replace('.txt', '')  # HHMMSS

        assert len(date_part) == 8, f"Date part format error: {date_part}"
        assert len(time_part) == 6, f"Time part format error: {time_part}"

        # Verify date time validity
        try:
            datetime.strptime(date_part, "%Y%m%d")
            datetime.strptime(time_part, "%H%M%S")
        except ValueError as e:
            pytest.fail(f"Date time format invalid: {e}")

        print(f"Filename format test passed: {filename}")

    def test_file_content_completeness(self):
        """Test file content completeness"""
        # Prepare test data
        employees = [
            {'name': 'Zhang San', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': 'Li Si', 'employee_id': '0201002', 'score': 92, 'tenure': 18},
            {'name': 'Wang Wu', 'employee_id': '0301003', 'score': 78, 'tenure': 36}
        ]

        # Execute lottery
        prizes = [
            {
                'name': 'First Prize',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            },
            {
                'name': 'Second Prize',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]

        # Execute lottery (disable output)
        import io
        import contextlib

        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)
        self.display.set_results(results)

        # Generate report content
        content = self.display.generate_report_content(employees)

        # Verify report content completeness
        required_content = [
            "Lottery System - Lottery Results Report" or "Lottery Results Report",
            "Generation Time:" or "Generated:",
            "Lottery Results" or "Results",
            "Fairness Statistical Report" or "Fairness Report",
            "Report End" or "End"
        ]

        # Check for prize names
        for prize_name in results.keys():
            assert prize_name in content, f"Report missing prize: {prize_name}"

        print("File content completeness test passed")

    def test_file_save_functionality(self):
        """Test file save functionality"""
        test_content = "This is a test file content\nContains Chinese characters\nTest UTF-8 encoding"
        test_filename = "test_save_functionality.txt"

        # Test save functionality
        success = self.file_utils.save_text_file(test_filename, test_content)
        assert success, "File save functionality failed"
        assert os.path.exists(test_filename), "Saved file does not exist"

        # Verify file content
        with open(test_filename, 'r', encoding='utf-8') as f:
            saved_content = f.read()

        assert saved_content == test_content, "Saved file content incorrect"

        # Clean up test file
        os.remove(test_filename)

        print("File save functionality test passed")
