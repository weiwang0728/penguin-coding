#!/usr/bin/env python3
"""
Test script for logging functionality (2.3.3b Logging)
This script tests that the application properly logs command execution to activity.log
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

def test_logging_functionality():
    """
    Test that the application logs command execution to activity.log
    """
    print("🧪 Testing logging functionality...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Remove existing activity.log if it exists
    log_file = project_root / "activity.log"
    if log_file.exists():
        log_file.unlink()
        print("✅ Removed existing activity.log file")
    
    # Execute the test command
    test_command = ["python", "-m", "src.main", "q", "list"]
    print(f"🔧 Executing command: {' '.join(test_command)}")
    
    try:
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30
        )
        
        print(f"📊 Command exit code: {result.returncode}")
        if result.stdout:
            print(f"📤 Command output:\n{result.stdout}")
        if result.stderr:
            print(f"❌ Command errors:\n{result.stderr}")
        
        # Check if command executed successfully
        if result.returncode != 0:
            print(f"❌ Command failed with exit code {result.returncode}")
            return False
        
        # Check if activity.log was created
        if not log_file.exists():
            print("❌ activity.log file was not created")
            return False
        
        # Read and validate log content
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read().strip()
        
        print(f"📋 Log file content:\n{log_content}")
        
        # Validate log content format
        if "EXECUTED: q list" not in log_content:
            print("❌ Log file does not contain expected command execution record")
            return False
        
        # Check log format (should contain timestamp, level, and message)
        lines = log_content.split('\n')
        for line in lines:
            if line.strip():  # Skip empty lines
                if " - INFO - EXECUTED: " not in line:
                    print(f"❌ Log line does not match expected format: {line}")
                    return False
        
        print("✅ Logging functionality test passed!")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def compare_with_expected():
    """
    Compare actual log output with expected output (for file comparison test)
    """
    print("\n🔍 Comparing with expected output...")
    
    project_root = Path(__file__).parent.parent
    actual_log = project_root / "activity.log"
    expected_log = Path(__file__).parent / "expected_activity.log"
    
    if not actual_log.exists():
        print("❌ Actual activity.log file not found")
        return False
    
    if not expected_log.exists():
        print("❌ Expected activity.log file not found")
        return False
    
    # Read both files
    with open(actual_log, 'r', encoding='utf-8') as f:
        actual_content = f.read().strip()
    
    with open(expected_log, 'r', encoding='utf-8') as f:
        expected_content = f.read().strip()
    
    # For logging, we only care about the command part, not the exact timestamp
    actual_command = actual_content.split(" - INFO - ")[-1] if " - INFO - " in actual_content else ""
    expected_command = expected_content.split(" - INFO - ")[-1] if " - INFO - " in expected_content else ""
    
    if actual_command == expected_command:
        print("✅ Log content matches expected format")
        return True
    else:
        print(f"❌ Log content mismatch:")
        print(f"   Expected: {expected_command}")
        print(f"   Actual:   {actual_command}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Golf Analyzer Logging Test")
    print("=" * 60)
    
    success = test_logging_functionality()
    if success:
        success = compare_with_expected()
    
    if success:
        print("\n🎉 All logging tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Logging tests failed!")
        sys.exit(1)