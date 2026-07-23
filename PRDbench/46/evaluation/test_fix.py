#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Fix Effect Script
"""

import sys
import os
sys.path.insert(0, '../src')

from credit_assessment.data.data_manager import DataManager
from credit_assessment.utils import ConfigManager

def test_data_import():
 """Test data import function"""
 print("=" * 50)
 print("Test data Import Function")
 print("=" * 50)

 try:
 # Create data manager
 config = ConfigManager()
 dm = DataManager(config)

 # Test import ing anomaly data
 print("Importing test data: test_data_anomaly.csv")
 df = dm.import_data('test_data_anomaly.csv', validate=True, encoding='utf-8')

 print(f"[SUCCESS] Successfully import ed data: {df.shape[0]} rows {df.shape[1]} columns")
 print(f"Column names: {list(df.columns)}")
 print("\nFirst 5 rows:")
 print(df.head())

 # Get validation report
 validation_report = dm.validate_current_data()
 print(f"\nValidation result: {validation_report['validation_summary']}")

 if validation_report.get('warnings'):
 print("\n[WARNING] Warning information:")
 for warning in validation_report['warnings']:
 print(f" - {warning}")

 if validation_report.get('suggestions'):
 print("\n[INFO] Suggestion information:")
 for suggestion in validation_report['suggestions']:
 print(f" - {suggestion}")

 return True

 except Exception as e:
 print(f"[ERROR] Import failed: {e}")
 import traceback
 traceback.print_exc()
 return False

def test_logger():
 """Test logging function"""
 print("\n" + "=" * 50)
 print("Test Logging Function")
 print("=" * 50)

 try:
 from credit_assessment.utils.logger import setup_logger
 logger = setup_logger("test_logger")
 logger.info("Test log information")
 logger.warning("Test warning information")
 print("[SUCCESS] Logging function normal")
 return True
 except Exception as e:
 print(f"[ERROR] Logging function abnormal: {e}")
 return False

if __name__ == "__main__":
 print("Starting to test fix effects...")

 # Test logging function
 logger_ok = test_logger()

 # Test data import function
 import_ok = test_data_import()

 print("\n" + "=" * 50)
 print("Test Results Summary")
 print("=" * 50)
 print(f"Logging function: {'[PASS]' if logger_ok else '[FAIL]'}")
 print(f"Data import: {'[PASS]' if import_ok else '[FAIL]'}")

 if logger_ok and import_ok:
 print("\n[SUCCESS] All functionality tests passed! Issues have been fixed.")
 else:
 print("\n[WARNING] There are still issues to resolve.")
