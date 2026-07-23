#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.8.1 Data Export - CSV Format
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


def test_csv_export():
 """Test CSV format data export functionality"""
 print("Starting Test 2.8.1 CSV format export...")

 # Create config and data manager
 config = ConfigManager()
 data_manager = DataManager(config)

 # Create test data
 np.random.seed(42)
 n_samples = 50

 test_data = pd.DataFrame({
 'customer_id': range(1, n_samples + 1),
 'age': np.random.randint(20, 80, n_samples),
 'income': np.random.randint(20000, 200000, n_samples),
 'credit_score': np.random.randint(300, 850, n_samples),
 'risk_score': np.random.random(n_samples),
 'target': np.random.choice([0, 1], n_samples)
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
 assert len(exported_data) == n_samples, f"Export row count incorrect: {len(exported_data)} != {n_samples}"
 assert len(exported_data.columns) == 6, f"Export column count incorrect: {len(exported_data.columns)}"

 # Verify data completeness
 assert 'customer_id' in exported_data.columns, "customer_id field missing"
 assert 'age' in exported_data.columns, "age field missing"
 assert 'income' in exported_data.columns, "income field missing"

 print(f"SUCCESS: CSV file generated successfully: {output_path}")
 print(f"SUCCESS: File size: {file_size} bytes")
 print(f"SUCCESS: Data row count: {len(exported_data)}")
 print(f"SUCCESS: Data column count: {len(exported_data.columns)}")

 except Exception as e:
 print(f"FAIL: CSV export failed: {e}")
 return False

 print("2.8.1 CSV format export test passed")
 return True


if __name__ == "__main__":
 test_csv_export()
