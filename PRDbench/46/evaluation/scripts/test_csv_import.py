#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Specialized Test Script: CSV Data Import Functional Test

Direct interface with DataManager import_data method, avoid redundant menu navigation
"""

import sys
import os
from pathlib import Path

# Add project path
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

try:
 from credit_assessment.data import DataManager
 from credit_assessment.utils import ConfigManager

 def test_csv_import():
 """Test CSV format import function"""
 print("=== CSV Data Import Test ===")

 # Initialize data manager
 config = ConfigManager()
 data_manager = DataManager(config)

 # Test file path
 csv_file = Path(__file__).parent.parent / "test_data_csv.csv"

 if not csv_file.exists():
 print(f"Error: Test data file does not exist - {csv_file}")
 return False

 try:
 # Execute CSVImport
 print(f"ImportFile: {csv_file}")
 data = data_manager.import_data(csv_file, validate=True, encoding='utf-8')

 # VerifyImport result
 if data is not None:
 row_count = len(data)
 col_count = len(data.columns)
 print(f"Data import success! {row_count} rows, {col_count} columns")

 # Display column names
 print(f" column names: {list(data.columns)}")

 # VerifyData row count
 if row_count >= 10:
 print("✓ CSV format supportnormal")
 print("✓ Data row countmeets requirements")
 return True
 else:
 print("✗ insufficient data rows")
 return False
 else:
 print("✗ Data importFailure")
 return False

 except Exception as e:
 print(f"✗ CSV Import test failed: {str(e)}")
 return False

 # Execute test
 if __name__ == "__main__":
 success = test_csv_import()
 sys.exit(0 if success else 1)

except ImportError as e:
 print(f"Module import failure: {str(e)}")
 print("Please ensure project structure is correct")
 sys.exit(1)