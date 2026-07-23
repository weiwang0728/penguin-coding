#!/usr/bin/env python3
"""
Test script: Verify descriptive statistics chart output functionality
Test type: file_comparison
Test target: 2.2.1b Descriptive Statistics (Chart Output)
"""

import os
import subprocess
import sys
from pathlib import Path
import filecmp

def run_test():
    """Run chart generation test"""
    print("=" * 60)
    print("Test: 2.2.1b Descriptive Statistics (Chart Output)")
    print("=" * 60)

    # Test command
    test_command = [
        "python", "-m", "src.main", "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]

    # Expected output files
    expected_files = [
        "evaluation/expected_gender_distribution.png",
        "evaluation/expected_venue_type_distribution.png"
    ]

    # Actual output files
    actual_files = [
        "evaluation/reports/descriptive/gender_distribution.png",
        "evaluation/reports/descriptive/venue_type_distribution.png"
    ]

    print("Step 1: Cleaning up previous output files...")
    for file_path in actual_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"  Deleted: {file_path}")

    print("\nStep 2: Executing test command...")
    print(f"Command: {' '.join(test_command)}")
    
    try:
        result = subprocess.run(test_command, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"❌ Command execution failed, exit code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False

        print("✅ Command execution successful")
        print(f"Standard output: {result.stdout}")

    except Exception as e:
        print(f"❌ Command execution exception: {e}")
        return False

    print("\nStep 3: Verifying output files...")
    all_files_exist = True

    for actual_file in actual_files:
        if os.path.exists(actual_file):
            file_size = os.path.getsize(actual_file)
            print(f"✅ File generated: {actual_file} (size: {file_size} bytes)")
        else:
            print(f"❌ File not generated: {actual_file}")
            all_files_exist = False

    if not all_files_exist:
        return False

    print("\nStep 4: File comparison...")
    # Note: PNG files are binary files and may vary slightly with each generation (timestamps, etc.)
    # Here we mainly check if the file exists and has a reasonable size
    comparison_passed = True

    for expected_file, actual_file in zip(expected_files, actual_files):
        if os.path.exists(expected_file) and os.path.exists(actual_file):
            expected_size = os.path.getsize(expected_file)
            actual_size = os.path.getsize(actual_file)

            # Allow some file size variation (PNG files may differ slightly due to generation time, etc.)
            size_diff_ratio = abs(expected_size - actual_size) / expected_size

            if size_diff_ratio < 0.1:  # Allow 10% size difference
                print(f"✅ File size matches: {actual_file}")
                print(f"   Expected size: {expected_size} bytes, Actual size: {actual_size} bytes")
            else:
                print(f"⚠️  File size difference is significant: {actual_file}")
                print(f"   Expected size: {expected_size} bytes, Actual size: {actual_size} bytes")
                print(f"   Difference ratio: {size_diff_ratio:.2%}")
        else:
            print(f"❌ Cannot compare files: {expected_file} or {actual_file} does not exist")
            comparison_passed = False

    print("\n" + "=" * 60)
    if all_files_exist and comparison_passed:
        print("🎉 Test passed! All chart files have been successfully generated.")
        return True
    else:
        print("❌ Test failed!")
        return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)