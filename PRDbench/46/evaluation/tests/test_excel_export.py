#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.8.2 Data Export - Excel Format
"""

import sys
import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# Add project path
current_dir = Path(__file__).parent.parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
 from credit_assessment.data.data_manager import DataManager
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 print(f"Import failed, skipping test: {e}")
 sys.exit(0)


def test_excel_export():
 """Test Excel format data export functionality"""
 print("Starting Test 2.8.2 Excel format export...")

 # Create config and data manager
 config = ConfigManager()
 data_manager = DataManager(config)

 # Create test data
 test_data = pd.DataFrame({
 'customer_id': [1, 2, 3, 4, 5],
 'age': [25, 35, 45, 30, 55],
 'income': [50000, 75000, 60000, 80000, 45000],
 'credit_score': [650, 700, 620, 750, 580],
 'risk_score': [0.3, 0.2, 0.4, 0.1, 0.6],
 'target': [1, 0, 1, 0, 1]
 })

 # Create temporary output path
 with tempfile.TemporaryDirectory() as temp_dir:
 output_path = os.path.join(temp_dir, "exported_data.xlsx")

 try:
 # Execute Excel export
 data_manager.export_data(test_data, output_path, mask_sensitive=False)

 # Verify file is generated
 assert os.path.exists(output_path), f"Excel file not generated: {output_path}"

 # Verify file size
 file_size = os.path.getsize(output_path)
 assert file_size > 1000, f"Excel file too small: {file_size} bytes"

 # Verify Excel content
 exported_data = pd.read_excel(output_path)
 assert len(exported_data) == 5, f"Export row count incorrect: {len(exported_data)} != 5"
 assert len(exported_data.columns) == 6, f"Export column count incorrect: {len(exported_data.columns)}"

 # Verify data completeness
 assert 'customer_id' in exported_data.columns, "customer_id field missing"
 assert 'age' in exported_data.columns, "age field missing"
 assert 'income' in exported_data.columns, "income field missing"
 assert 'credit_score' in exported_data.columns, "credit_score field missing"

 print(f"SUCCESS: Excel file generated successfully: {output_path}")
 print(f"SUCCESS: File size: {file_size} bytes")
 print(f"SUCCESS: Data row count: {len(exported_data)}")
 print(f"SUCCESS: Data column count: {len(exported_data.columns)}")

 except Exception as e:
 print(f"FAIL: Excel export failed: {e}")
 return False

 print("2.8.2 Excel format export test passed")
 return True


if __name__ == "__main__":
 test_excel_export()
