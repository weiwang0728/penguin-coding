#!/usr/bin/env python3
"""
Test script: Verify descriptive statistics analysis functionality
"""

import subprocess
import os
import sys
from pathlib import Path

def test_descriptive_stats():
    """Test descriptive statistics analysis functionality"""

    # Test command
    test_command = [
        "python", "-m", "src.main", "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]

    print("🧪 Starting descriptive statistics analysis test...")
    print(f"📋 Executing command: {' '.join(test_command)}")

    try:
        # Execute command
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=os.getcwd()
        )

        # Check exit code
        if result.returncode != 0:
            print(f"❌ Command execution failed, exit code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False

        print("✅ Command execution successful")
        print(f"📤 Standard output: {result.stdout}")

        # Check if output file exists
        expected_file = Path("evaluation/reports/descriptive/descriptive_stats.md")
        if not expected_file.exists():
            print(f"❌ Expected output file does not exist: {expected_file}")
            return False

        print(f"✅ Output file generated: {expected_file}")

        # Check file content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify key content
        required_elements = [
            "# Descriptive Statistics Analysis Report",
            "Data Overview",
            "Numerical Field Statistics",
            "Mean",
            "Standard Deviation",
            "Categorical Field Distribution",
            "Percentage"
        ]

        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)

        if missing_elements:
            print(f"❌ Output file missing required elements: {missing_elements}")
            return False

        print("✅ Output file contains all required statistical information")
        print("🎉 Descriptive statistics analysis test passed!")
        return True

    except Exception as e:
        print(f"❌ Exception occurred during test: {e}")
        return False

if __name__ == "__main__":
    success = test_descriptive_stats()
    sys.exit(0 if success else 1)