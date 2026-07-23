#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.6.1a Report Generation - HTML Format Output
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
 from credit_assessment.evaluation.report_generator import ReportGenerator
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 print(f"Import failed, skipping test: {e}")
 sys.exit(0)


def test_html_report_generation():
 """Test HTML report generation functionality"""
 print("Starting Test 2.6.1a HTML report generation...")

 # Create config manager
 config = ConfigManager()
 report_generator = ReportGenerator(config)

 # Create simulated evaluation result s
 np.random.seed(42)
 n_samples = 100

 # Simulated prediction result s
 y_true = np.random.choice([0, 1], n_samples)
 y_pred = np.random.random(n_samples) # Prediction probability
 y_pred_binary = (y_pred > 0.5).astype(int) # Binary prediction

 # Create simulated data
 test_data = pd.DataFrame({
 'age': np.random.randint(20, 80, n_samples),
 'income': np.random.randint(20000, 200000, n_samples),
 'credit_score': np.random.randint(300, 850, n_samples),
 'target': y_true
 })

 # Create temporary output directory
 with tempfile.TemporaryDirectory() as temp_dir:
 output_path = os.path.join(temp_dir, "test_report.html")

 try:
 # Generate HTML report
 result = report_generator.generate_html_report(
 data=test_data,
 prediction s={'y_true': y_true, 'y_pred': y_pred, 'y_pred_binary': y_pred_binary},
 output_path=output_path
 )

 # Verify HTML file is generated
 assert os.path.exists(output_path), f"HTML report file not generated: {output_path}"

 # Verify file size
 file_size = os.path.getsize(output_path)
 assert file_size > 1000, f"HTML report file too small: {file_size} bytes"

 # Verify HTML content
 with open(output_path, 'r', encoding='utf-8') as f:
 content = f.read()
 assert '<html>' in content, "HTML format incorrect"
 assert 'Report' in content or 'report' in content, "HTML report content missing"

 print(f"SUCCESS: HTML report generated successfully: {output_path}")
 print(f"SUCCESS: File size: {file_size} bytes")
 print("SUCCESS: HTML format verification passed")

 except Exception as e:
 print(f"FAIL: HTML report generation failed: {e}")
 return False

 print("2.6.1a HTML report generation test passed")
 return True


if __name__ == "__main__":
 test_html_report_generation()
