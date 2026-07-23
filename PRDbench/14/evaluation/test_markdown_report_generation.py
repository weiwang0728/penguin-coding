#!/usr/bin/env python3
"""
Markdown report generation test script
Test [2.3.2c Full Report Export (Markdown)] functionality
"""

import subprocess
import os
import sys
from pathlib import Path

def test_markdown_report_generation():
    """Test Markdown report generation functionality"""
    print("🧪 Starting Markdown report generation functionality test...")

    # 1. Execute Markdown report generation command
    cmd = [
        "python", "-m", "src.main", "report", "generate-full",
        "--data-path", "evaluation/sample_data.csv",
        "--format", "markdown",
        "--output-path", "evaluation/full_report.md"
    ]

    print(f"📋 Executing command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            print(f"❌ Command execution failed, exit code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False

        print("✅ Command execution successful")
        print(f"Output: {result.stdout}")

        # 2. Check if expected output files exist
        output_file = "evaluation/full_report.md"
        expected_file = "evaluation/expected_full_report.md"

        if not os.path.exists(output_file):
            print(f"❌ Output file does not exist: {output_file}")
            return False
        print(f"✅ Output file exists: {output_file}")

        if not os.path.exists(expected_file):
            print(f"❌ Expected file does not exist: {expected_file}")
            return False
        print(f"✅ Expected file exists: {expected_file}")

        # 3. Verify file size is not zero
        output_size = os.path.getsize(output_file)
        expected_size = os.path.getsize(expected_file)

        if output_size == 0:
            print(f"❌ Output file size is zero: {output_file}")
            return False
        print(f"✅ Output file size: {output_size} bytes")

        if expected_size == 0:
            print(f"❌ Expected file size is zero: {expected_file}")
            return False
        print(f"✅ Expected file size: {expected_size} bytes")

        # 4. Verify file format (check Markdown file extension)
        if not output_file.endswith('.md'):
            print(f"❌ Output file is not in Markdown format: {output_file}")
            return False
        print(f"✅ Output file is in Markdown format")

        # 5. Validate file content
        if not validate_markdown_content(output_file, expected_file):
            return False

        print("🎉 All tests passed! Markdown report generation functionality works correctly.")
        return True

    except Exception as e:
        print(f"❌ Exception occurred during test: {e}")
        return False

def validate_markdown_content(output_file, expected_file):
    """Validate Markdown file content"""
    print(f"🔍 Validating Markdown file content...")

    try:
        # Read output file
        with open(output_file, 'r', encoding='utf-8') as f:
            output_content = f.read()

        # Read expected file
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_content = f.read()

        # Check if content matches exactly
        if output_content == expected_content:
            print("✅ File content matches expected output exactly")
            return True

        # If not exactly matching, perform detailed comparison
        print("⚠️  File content differs, performing detailed analysis...")

        output_lines = output_content.split('\n')
        expected_lines = expected_content.split('\n')

        print(f"✅ Output file line count: {len(output_lines)}")
        print(f"✅ Expected file line count: {len(expected_lines)}")

        # Check if key sections exist
        required_sections = [
            "# Golf Tourist Consumer Behavior Analysis Report",
            "## Executive Summary",
            "## Data Overview",
            "## Descriptive Statistical Analysis",
            "### Numerical Field Statistics",
            "### Categorical Field Distribution",
            "## Analysis Conclusion",
            "## Marketing Recommendations"
        ]

        for section in required_sections:
            if section in output_content:
                print(f"✅ Contains required section: {section}")
            else:
                print(f"❌ Missing required section: {section}")
                return False

        # Check table format
        table_headers = [
            "| Field | Mean | Std Dev | Min | Max | Median |",
            "| Category | Count | Percentage |"
        ]

        for header in table_headers:
            if header in output_content:
                print(f"✅ Contains table format: {header}")
            else:
                print(f"❌ Missing table format: {header}")
                return False

        # Check data content (key statistical data)
        key_data_points = [
            "This analysis includes **10** valid records",
            "Covering **11** dimensions of information",
            "| price_influence | 3.00 | 1.49 | 1 | 5 | 3.00 |",
            "| Male | 5 | 50.0% |",
            "| Female | 5 | 50.0% |"
        ]

        for data_point in key_data_points:
            if data_point in output_content:
                print(f"✅ Contains key data: {data_point}")
            else:
                print(f"❌ Missing key data: {data_point}")
                return False

        print("✅ File content validation passed (structure and key data are correct)")
        return True

    except Exception as e:
        print(f"❌ File content validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_markdown_report_generation()
    sys.exit(0 if success else 1)