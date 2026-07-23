#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean py test runner - completely reset Python environment before running py test
"""
import sys
import os
import subprocess

def run_pytest_clean(test_file, test_method=None):
 """Run py test in a completely clean subprocess"""
 print(f"=== Running py test test in clean environment ===")
 print(f"Test file: {test_file}")

 # Build py test command
 if test_method:
 cmd = [sys.executable, "-m", "py test", f"{test_file}::{test_method}", "-v"]
 else:
 cmd = [sys.executable, "-m", "py test", test_file, "-v"]

 print(f"Executing command: {' '.join(cmd)}")

 try:
 # Run py test in subprocess, completely isolated environment
 result = subprocess.run(
 cmd,
 cwd=os.getcwd(),
 capture_output=True,
 text=True,
 encoding='utf-8',
 timeout=60
 )

 print("=== STDOUT ===")
 print(result.stdout)
 print("=== STDERR ===")
 print(result.stderr)
 print(f"=== Exit code: {result.returncode} ===")

 return result.returncode == 0

 except subprocess.TimeoutExpired:
 print("Test timeout")
 return False
 except Exception as e:
 print(f"Error during test execution: {e}")
 return False

if __name__ == "__main__":
 # Test missing value detection
 success = run_pytest_clean(
 "tests/test_missing_value s_detection.py"
 )

 if success:
 print("\n✅ py test test successful!")
 else:
 print("\n❌ py test test failed")