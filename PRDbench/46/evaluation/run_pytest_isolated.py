#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Isolated py test runner to solve buffer detached issue
"""
import os
import sys
import subprocess
import tempfile


def run_isolated_py test(test_file, test_method=None):
 """Run py test in completely isolated process"""
 print(f"=== Running py test in completely isolated environment ===")
 print(f"Test file: {test_file}")

 # Create startup script
 script_content = f'''
import sys
import os
sys.path.insert(0, '{os.path.abspath("../src")}')

# Completely reset stdout/stderr
import io
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

# Set environment variables
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUNBUFFERED"] = "1"

# Run py test
import py test
'''

 if test_method:
 script_content += f'''
py test.main(["{test_file}::{test_method}", "-v", "-s", "--tb=short"])
'''
 else:
 script_content += f'''
py test.main(["{test_file}", "-v", "-s", "--tb=short"])
'''

 # Write to temporary script
 with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
 f.write(script_content)
 script_path = f.name

 try:
 # Run in new Python process
 result = subprocess.run([
 sys.executable, script_path
 ],
 cwd=os.getcwd(),
 capture_output=True,
 text=True,
 encoding='utf-8',
 timeout=120
 )

 print("=== Output ===")
 print(result.stdout)
 if result.stderr:
 print("=== Error output ===")
 print(result.stderr)
 print(f"=== Exit code: {result.returncode} ===")

 return result.returncode == 0

 finally:
 # Clean up temporary file
 if os.path.exists(script_path):
 os.unlink(script_path)


if __name__ == "__main__":
 # Test missing value detection
 success = run_isolated_py test(
 "tests/test_missing_value s_detection.py",
 "TestMissingValuesDetection::test_missing_value s_detection"
 )

 if success:
 print("\n✅ Isolated py test test successful!")
 else:
 print("\n❌ Isolated py test test still failed")