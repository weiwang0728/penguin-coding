#!/usr/bin/env python3
"""
Test script for data anonymization functionality.
This script sets up test data, runs the anonymization export, and verifies the results.
"""

import sys
import os
import subprocess
import csv
import tempfile
import shutil

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            cwd=cwd or os.path.dirname(__file__)
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except Exception as e:
        return 1, "", str(e)

def compare_csv_files(actual_file, expected_file):
    """Compare two CSV files and return True if they match"""
    try:
        with open(actual_file, 'r', encoding='utf-8-sig') as f1, \
             open(expected_file, 'r', encoding='utf-8') as f2:
            
            reader1 = csv.reader(f1)
            reader2 = csv.reader(f2)
            
            for row1, row2 in zip(reader1, reader2):
                if row1 != row2:
                    print(f"Mismatch found:")
                    print(f"Actual:   {row1}")
                    print(f"Expected: {row2}")
                    return False
            
            # Check if one file has more rows than the other
            try:
                next(reader1)
                print("Actual file has more rows than expected")
                return False
            except StopIteration:
                pass
            
            try:
                next(reader2)
                print("Expected file has more rows than actual")
                return False
            except StopIteration:
                pass
                
        return True
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False

def test_anonymization():
    """Main test function for data anonymization"""
    print("Starting data anonymization functionality test...")

    # Step 1: Setup test data
    print("Step 1: Setting up test data...")
    setup_script = os.path.join(os.path.dirname(__file__), 'setup_test_data.py')
    returncode, stdout, stderr = run_command(f"python {setup_script}")

    if returncode != 0:
        print(f"Test data setup failed:")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return False

    print("Test data setup successful")

    # Step 2: Run anonymization export
    print("Step 2: Executing data anonymization export...")
    output_file = os.path.join(os.path.dirname(__file__), 'anonymized_data.csv')

    # Remove output file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    export_command = f"python -m src.main data export --anonymize --output-path {output_file}"
    returncode, stdout, stderr = run_command(export_command, cwd=os.path.join(os.path.dirname(__file__), '..'))

    if returncode != 0:
        print(f"Data export failed:")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return False

    print("Data export successful")
    print(f"Output info: {stdout.strip()}")

    # Step 3: Verify output file exists
    if not os.path.exists(output_file):
        print(f"Output file does not exist: {output_file}")
        return False

    print("Output file created")

    # Step 4: Compare with expected output
    print("Step 3: Verifying anonymization results...")
    expected_file = os.path.join(os.path.dirname(__file__), 'expected_anonymized_data.csv')

    if not os.path.exists(expected_file):
        print(f"Expected output file does not exist: {expected_file}")
        return False

    if compare_csv_files(output_file, expected_file):
        print("Anonymization verification successful! Data has been correctly anonymized.")
        return True
    else:
        print("Anonymization verification failed!")

        # Show actual content for debugging
        print("\nActual output content:")
        with open(output_file, 'r', encoding='utf-8-sig') as f:
            print(f.read())

        print("\nExpected output content:")
        with open(expected_file, 'r', encoding='utf-8') as f:
            print(f.read())

        return False

if __name__ == "__main__":
    success = test_anonymization()
    sys.exit(0 if success else 1)