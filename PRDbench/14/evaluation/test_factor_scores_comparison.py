#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factor score output file comparison test script
Used to verify "[2.2.2b Factor Analysis (Factor Score Output)]" test case
"""

import os
import sys
import subprocess
import pandas as pd
from pathlib import Path

def run_factor_analysis():
    """Run factor analysis command"""
    print("🔄 Executing factor analysis command...")

    cmd = [
        "python", "-m", "src.main", "analyze", "factor",
        "--data-path", "evaluation/sample_data.csv",
        "--questions", "price_influence,satisfaction,amenities_importance",
        "--output-dir", "evaluation/reports/factor"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ Factor analysis command execution successful")
            print(f"Output: {result.stdout}")
            return True
        else:
            print(f"❌ Factor analysis command execution failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error occurred while executing command: {e}")
        return False

def compare_factor_scores():
    """Compare actual output with expected output"""
    print("🔍 Comparing factor score files...")

    actual_file = Path("evaluation/reports/factor/factor_scores.csv")
    expected_file = Path("evaluation/expected_factor_scores.csv")

    if not actual_file.exists():
        print(f"❌ Actual output file does not exist: {actual_file}")
        return False

    if not expected_file.exists():
        print(f"❌ Expected output file does not exist: {expected_file}")
        return False

    try:
        # Read files
        actual_df = pd.read_csv(actual_file)
        expected_df = pd.read_csv(expected_file)

        # Check shape
        if actual_df.shape != expected_df.shape:
            print(f"❌ File shapes do not match: actual {actual_df.shape} vs expected {expected_df.shape}")
            return False

        # Check column names
        if list(actual_df.columns) != list(expected_df.columns):
            print(f"❌ Column names do not match: actual {list(actual_df.columns)} vs expected {list(expected_df.columns)}")
            return False

        # Check values (allow small floating point errors)
        if not actual_df.equals(expected_df):
            # Try numerical comparison (tolerate floating point errors)
            try:
                pd.testing.assert_frame_equal(actual_df, expected_df, rtol=1e-10, atol=1e-10)
                print("✅ File contents match (within numerical error tolerance)")
                return True
            except AssertionError as e:
                print(f"❌ File contents do not match: {e}")
                return False
        else:
            print("✅ File contents completely match")
            return True

    except Exception as e:
        print(f"❌ Error occurred while comparing files: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Factor Analysis (Factor Score Output) File Comparison Test")
    print("=" * 60)

    # Ensure in correct working directory
    if not Path("src/main.py").exists():
        print("❌ Please run this script from project root directory")
        sys.exit(1)

    # Create output directory
    output_dir = Path("evaluation/reports/factor")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run factor analysis
    if not run_factor_analysis():
        print("❌ Test failed: Factor analysis command execution failed")
        sys.exit(1)

    # Compare files
    if not compare_factor_scores():
        print("❌ Test failed: File comparison did not pass")
        sys.exit(1)

    print("=" * 60)
    print("🎉 Test passed! Factor score output file completely matches expected output")
    print("=" * 60)

if __name__ == "__main__":
    main()