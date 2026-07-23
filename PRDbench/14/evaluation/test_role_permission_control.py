#!/usr/bin/env python3
"""
Role permission control test script
Test [2.3.3a Permission Control (Roles)] functionality
"""

import subprocess
import os
import sys
from pathlib import Path

def test_role_permission_control():
    """Test role permission control functionality"""
    print("🧪 Starting role permission control functionality test...")

    # Test step 1: Check if --role option exists
    print("\n📋 Step 1: Check if --role option exists")
    cmd1 = ["python", "-m", "src.main", "--help"]

    try:
        result1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8')

        if result1.returncode != 0:
            print(f"❌ Help command execution failed, exit code: {result1.returncode}")
            return False

        # Check if --role option description is included
        if "--role" in result1.stdout and "User role" in result1.stdout:
            print("✅ --role option exists and description is correct")
            print(f"   Found option description: {[line.strip() for line in result1.stdout.split('\\n') if '--role' in line][0]}")
        else:
            print("❌ --role option does not exist or description is incorrect")
            return False

    except Exception as e:
        print(f"❌ Step 1 execution exception: {e}")
        return False

    # Test step 2: Regular user permission test (should fail)
    print("\n📋 Step 2: Test regular user permission (should be denied)")
    cmd2 = [
        "python", "-m", "src.main", "--role", "Regular User",
        "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]

    try:
        result2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8')

        if result2.returncode == 1:
            print("✅ Regular user permission correctly denied (exit code 1)")
        else:
            print(f"❌ Regular user permission check failed, exit code: {result2.returncode}")
            return False

        # Check error message
        expected_messages = [
            "Permission Error: 'Regular User' role is not authorized to perform this operation",
            "This operation requires 'Analyst' or higher permission"
        ]

        for msg in expected_messages:
            if msg in result2.stdout:
                print(f"✅ Contains expected error message: {msg}")
            else:
                print(f"❌ Missing expected error message: {msg}")
                print(f"Actual output: {result2.stdout}")
                return False

    except Exception as e:
        print(f"❌ Step 2 execution exception: {e}")
        return False

    # Test step 3: Analyst permission test (should succeed)
    print("\n📋 Step 3: Test analyst permission (should succeed)")
    cmd3 = [
        "python", "-m", "src.main", "--role", "Analyst",
        "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]

    try:
        result3 = subprocess.run(cmd3, capture_output=True, text=True, encoding='utf-8')

        if result3.returncode == 0:
            print("✅ Analyst permission correctly passed (exit code 0)")
        else:
            print(f"❌ Analyst permission check failed, exit code: {result3.returncode}")
            print(f"Error output: {result3.stderr}")
            return False

        # Check success message
        expected_success_messages = [
            "Successfully read data file: evaluation/sample_data.csv",
            "Descriptive statistics analysis complete, report saved to evaluation/reports/descriptive"
        ]

        for msg in expected_success_messages:
            if msg in result3.stdout:
                print(f"✅ Contains expected success message: {msg}")
            else:
                print(f"❌ Missing expected success message: {msg}")
                print(f"Actual output: {result3.stdout}")
                return False

    except Exception as e:
        print(f"❌ Step 3 execution exception: {e}")
        return False

    # Verify output files
    print("\n📋 Verifying output files")
    expected_files = [
        "evaluation/reports/descriptive/descriptive_stats.md",
        "evaluation/reports/descriptive/gender_distribution.png",
        "evaluation/reports/descriptive/venue_type_distribution.png"
    ]

    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ Output file exists: {file_path}")
        else:
            print(f"⚠️  Output file does not exist: {file_path}")

    print("\n🎉 All permission control tests passed!")
    return True

def test_additional_roles():
    """Test other roles"""
    print("\n🔍 Testing other roles...")

    # Test administrator role (should succeed)
    print("\n📋 Test administrator permission (should succeed)")
    cmd = [
        "python", "-m", "src.main", "--role", "Administrator",
        "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode == 0:
            print("✅ Administrator permission correctly passed")
        else:
            print(f"❌ Administrator permission check failed, exit code: {result.returncode}")
            return False

    except Exception as e:
        print(f"❌ Administrator permission test exception: {e}")
        return False

    # Test default role (should succeed)
    print("\n📋 Test default role (should succeed)")
    cmd_default = [
        "python", "-m", "src.main",
        "analyze", "stats",
        "--data-path", "evaluation/sample_data.csv",
        "--output-dir", "evaluation/reports/descriptive"
    ]

    try:
        result_default = subprocess.run(cmd_default, capture_output=True, text=True, encoding='utf-8')

        if result_default.returncode == 0:
            print("✅ Default role (Analyst) correctly passed")
        else:
            print(f"❌ Default role check failed, exit code: {result_default.returncode}")
            return False

    except Exception as e:
        print(f"❌ Default role test exception: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_role_permission_control()
    
    if success:
        additional_success = test_additional_roles()
        success = success and additional_success
    
    sys.exit(0 if success else 1)