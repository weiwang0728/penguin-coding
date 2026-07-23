#!/usr/bin/env python3
"""
Factor analysis test script
Test for factor analysis functionality file comparison test
"""

import subprocess
import sys
import os
import pandas as pd
from pathlib import Path

def run_command(command):
    """Execute command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def compare_csv_files(expected_file, actual_file):
    """Compare contents of two CSV files"""
    try:
        expected_df = pd.read_csv(expected_file)
        actual_df = pd.read_csv(actual_file)

        # Check if shapes match
        if expected_df.shape != actual_df.shape:
            return False, f"File shapes do not match: expected {expected_df.shape}, actual {actual_df.shape}"

        # Check if column names match
        if list(expected_df.columns) != list(actual_df.columns):
            return False, f"Column names do not match: expected {list(expected_df.columns)}, actual {list(actual_df.columns)}"

        # Check if indices match
        if list(expected_df.index) != list(actual_df.index):
            return False, f"Indices do not match: expected {list(expected_df.index)}, actual {list(actual_df.index)}"

        return True, "File contents match"

    except Exception as e:
        return False, f"Error occurred while comparing files: {str(e)}"

def test_factor_analysis():
    """Test factor analysis functionality"""
    print("=" * 60)
    print("Factor Analysis Test")
    print("=" * 60)

    # Test command
    test_command = 'python -m src.main analyze factor --data-path evaluation/sample_data.csv --questions "price_influence,satisfaction,amenities_importance" --output-dir evaluation/reports/factor'

    print(f"Executing command: {test_command}")

    # Execute command
    returncode, stdout, stderr = run_command(test_command)

    print(f"Return code: {returncode}")
    print(f"Standard output: {stdout}")
    if stderr:
        print(f"Standard error: {stderr}")

    # Check if command executed successfully
    if returncode != 0:
        print("❌ Command execution failed")
        return False

    # Check if output file exists
    expected_file = "evaluation/reports/factor/factor_loadings.csv"
    if not os.path.exists(expected_file):
        print(f"❌ Expected output file does not exist: {expected_file}")
        return False

    print(f"✅ Output file generated: {expected_file}")

    # Check file content
    try:
        df = pd.read_csv(expected_file, index_col=0)
        print(f"✅ File format correct, shape: {df.shape}")
        print("File content preview:")
        print(df.head())

        # Check if expected variables are included
        expected_variables = ['price_influence', 'satisfaction', 'amenities_importance']
        if df.index.tolist() == expected_variables:
            print("✅ Contains all expected analysis variables")
        else:
            print(f"❌ Variables do not match, expected: {expected_variables}, actual: {df.index.tolist()}")
            return False

        # Check if factor columns exist
        factor_columns = [col for col in df.columns if col.startswith('Factor_')]
        if len(factor_columns) >= 1:
            print(f"✅ Contains {len(factor_columns)} factors: {factor_columns}")
        else:
            print("❌ Factor columns not found")
            return False

    except Exception as e:
        print(f"❌ Error occurred while reading file: {e}")
        return False

    print("✅ Factor analysis test passed")
    return True

if __name__ == "__main__":
    success = test_factor_analysis()
    sys.exit(0 if success else 1)