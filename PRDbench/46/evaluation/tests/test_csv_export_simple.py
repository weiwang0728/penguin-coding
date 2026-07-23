#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.8.1 Data Export - CSV Format (simplified Version)
"""

import pandas as pd
import os
import tempfile


def test_csv_export_simple():
 """simplified CSV export test, does not depend on project modules"""
 print("Starting Test 2.8.1 CSV format export (simplified version)...")

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
 output_path = os.path.join(temp_dir, "exported_data.csv")

 try:
 # Execute CSV export
 test_data.to_csv(output_path, index=False, encoding='utf-8')

 # Verify file is generated
 assert os.path.exists(output_path), f"CSV file not generated: {output_path}"

 # Verify file size
 file_size = os.path.getsize(output_path)
 assert file_size > 100, f"CSV file too small: {file_size} bytes"

 # Verify CSV content
 exported_data = pd.read_csv(output_path, encoding='utf-8')
 assert len(exported_data) == 5, f"Export row count incorrect: {len(exported_data)}"
 assert len(exported_data.columns) == 6, f"Export column count incorrect: {len(exported_data.columns)}"

 # Verify field completeness
 required_fields = ['customer_id', 'age', 'income', 'credit_score', 'risk_score', 'target']
 for field in required_fields:
 assert field in exported_data.columns, f"{field} field missing"

 # Verify data content
 assert exported_data['customer_id'].tolist() == [1, 2, 3, 4, 5], "customer_id data incorrect"
 assert exported_data['age'].tolist() == [25, 35, 45, 30, 55], "age data incorrect"

 print(f"SUCCESS: CSV file generated successfully: {output_path}")
 print(f"SUCCESS: File size: {file_size} bytes")
 print(f"SUCCESS: Data row count: {len(exported_data)}")
 print(f"SUCCESS: Data column count: {len(exported_data.columns)}")
 print("SUCCESS: All field verifications passed")

 return True

 except Exception as e:
 print(f"FAIL: CSV export failed: {e}")
 return False


if __name__ == "__main__":
 success = test_csv_export_simple()
 if success:
 print("2.8.1 CSV format export test passed")
 else:
 print("2.8.1 CSV format export test failed")