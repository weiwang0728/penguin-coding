#!/usr/bin/env python3
"""
Simple test runner for data anonymization functionality.
This script can be used to quickly test the anonymization feature.
"""

import os
import sys
import subprocess

def main():
    """Run the anonymization test"""
    print("=" * 50)
    print("Data Anonymization Feature Test")
    print("=" * 50)

    # Change to the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    try:
        # Step 1: Setup test data
        print("1. Setting up test data...")
        result = subprocess.run([sys.executable, "evaluation/setup_test_data.py"],
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"Test data setup failed: {result.stderr}")
            return False
        print("   ✓ Test data setup successful")

        # Step 2: Run anonymization export
        print("2. Executing data anonymization export...")
        result = subprocess.run([sys.executable, "-m", "src.main", "data", "export",
                               "--anonymize", "--output-path", "evaluation/anonymized_data.csv"],
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode != 0:
            print(f"Data export failed: {result.stderr}")
            return False
        print("   ✓ Data export successful")
        print(f"   Output: {result.stdout.strip()}")

        # Step 3: Verify the output
        print("3. Verifying anonymization results...")
        output_file = "evaluation/anonymized_data.csv"
        if not os.path.exists(output_file):
            print("   ✗ Output file does not exist")
            return False

        # Read and display the anonymized data
        with open(output_file, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        print("   ✓ Anonymization results:")
        for i, line in enumerate(lines[:6]):  # Show first 6 lines
            print(f"     {line.strip()}")
        if len(lines) > 6:
            print(f"     ... (total {len(lines)} lines)")

        # Check if anonymization worked (checking for anonymized patterns like "Z*" or masked phone)
        if '*' in content and '138****5678' in content:
            print("   ✓ Data anonymization verification successful!")
            return True
        else:
            print("   ✗ Data anonymization verification failed!")
            return False

    except Exception as e:
        print(f"Error occurred during test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("=" * 50)
    if success:
        print("Test Result: Passed ✓")
    else:
        print("Test Result: Failed ✗")
    print("=" * 50)
    sys.exit(0 if success else 1)