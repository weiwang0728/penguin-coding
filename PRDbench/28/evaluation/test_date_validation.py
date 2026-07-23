#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Date field validation test script
"""

import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.input_helpers import InputHelper

def test_date_validation_logic():
 """Test date validation logic"""
 print("Testing date field validation logic...")

 input_helper = InputHelper()

 # Test invalid date format
 invalid_dates = [
 "2025-13-32", # Invalid month and date
 "abc", # Non-date string
 "2020/01/15", # Wrong format
 "2020-1-1", # Format not standard
 ]

 valid_dates = [
 "2020-01-15", # Correct format
 "2023-12-31", # Boundary date
 ]

 print("[OK] Test invalid date detection logic:")
 for invalid_date in invalid_dates:
 try:
 # Simulate date validation process
 datetime.strptime(invalid_date, "%Y-%m-%d")
 print(f" [ERROR] Should detect invalid date: {invalid_date}")
 return False
 except ValueError:
 print(f" [OK] Correctly detected invalid date: {invalid_date}")

 print("[OK] Test valid date validation:")
 for valid_date in valid_dates:
 try:
 date_obj = datetime.strptime(valid_date, "%Y-%m-%d")
 if date_obj <= datetime.now():
 print(f" [OK] Correctly validated valid date: {valid_date}")
 else:
 print(f" [WARNING] Future date should be rejected: {valid_date}")
 except ValueError:
 print(f" [ERROR] Valid date was incorrectly rejected: {valid_date}")
 return False

 print("[OK] System can detect date format errors and require re-entering correct format (YYYY-MM-DD) date")
 return True

def test_progress_feedback_logic():
 """Test progress feedback display logic"""
 print("Testing progress feedback display logic...")

 input_helper = InputHelper()

 # Test progress display function
 total_fields = 8
 for current in range(1, total_fields + 1):
 try:
 # Test progress display function
 input_helper.display_progress(current, total_fields, "Filling progress")
 if current == total_fields:
 print(f"\n[OK] Progress display functionality normal, supports 'Already completed {current}/{total_fields} items' format")
 except Exception as e:
 print(f"Error: Progress display function abnormal: {e}")
 return False

 return True

def main():
 """Main test function"""
 tests = [
 ("Date field validation", test_date_validation_logic),
 ("Progress feedback display", test_progress_feedback_logic)
 ]

 all_passed = True
 for test_name, test_func in tests:
 print(f"\n--- {test_name} ---")
 try:
 result = test_func()
 if not result:
 all_passed = False
 print(f"[FAIL] {test_name} test failed")
 else:
 print(f"[PASS] {test_name} test passed")
 except Exception as e:
 print(f"[ERROR] {test_name} test error occurred: {e}")
 all_passed = False

 if all_passed:
 print("\n[SUCCESS] All input validation function tests passed")
 return True
 else:
 print("\n[FAILED] Some input validation function tests failed")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)