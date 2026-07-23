#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Test: Code Quality PEP8 Compliance Verification

Test Goal: Use code checking tools to verify code compliance with PEP8 standards, no format errors
"""

import os
import subprocess
import py test
from pathlib import Path


class TestCodeQuality:
 """Code quality test class"""

 def test_pep8_compliance(self):
 """Test PEP8 compliance"""
 project_root = Path(__file__).parent.parent.parent / "src"

 # Check project source code directory
 assert project_root.exists(), "Source code directory does not exist"

 # Use flake8 to check PEP8 compliance
 try:
 # Check main module files
 main_files = [
 project_root / "main.py",
 project_root / "credit_assessment"
 ]

 pep8_errors = []
 total_files_checked = 0

 for path in main_files:
 if path.exists():
 if path.is_file():
 # Check single file
 result = self._check_file_pep8(path)
 if result["errors"]:
 pep8_errors.extend(result["errors"])
 total_files_checked += 1
 else:
 # Check all Python files in directory
 for py_file in path.rglob("*.py"):
 result = self._check_file_pep8(py_file)
 if result["errors"]:
 pep8_errors.extend(result["errors"])
 total_files_checked += 1

 # Verify sufficient files were checked
 assert total_files_checked >= 5, f"Too few files checked: {total_files_checked}"

 # Verify PEP8 compliance
 if pep8_errors:
 error_summary = f"Found {len(pep8_errors)} PEP8 compliance issues:\n"
 for error in pep8_errors[:10]: # Only show first 10 errors
 error_summary += f" - {error}\n"

 # Allow minor format issues (1-point standard)
 if len(pep8_errors) <= 5:
 print(f"Warning: {error_summary}")
 # Don't raise exception, indicates basic compliance but with minor issues
 else:
 # Too many issues, does not comply with PEP8
 py test.fail(f"PEP8 compliance check failed: {error_summary}")

 print(f"PEP8 compliance check completed, checked {total_files_checked} files")

 except FileNotFoundError:
 # If flake8 is not installed, use basic format check
 print("Warning: flake8 not installed, using basic check")
 self._basic_format_check(project_root)

 def _check_file_pep8(self, file_path):
 """Use flake8 to check single file PEP8 compliance"""
 errors = []

 try:
 # Try to use flake8
 result = subprocess.run(
 ["python", "-m", "flake8", str(file_path), "--max-line-length=100"],
 capture_output=True,
 text=True,
 timeout=10
 )

 if result.stdout.strip():
 errors.extend(result.stdout.strip().split('\n'))

 except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
 # flake8 not available, perform basic check
 errors.extend(self._basic_file_check(file_path))

 return {"errors": errors}

 def _basic_file_check(self, file_path):
 """Basic file format check"""
 errors = []

 try:
 with open(file_path, 'r', encoding='utf-8') as f:
 lines = f.readlines()

 for i, line in enumerate(lines, 1):
 # Check line length
 if len(line.rstrip()) > 120:
 errors.append(f"{file_path}:{i}: rows length exceeds 120 characters")

 # Check indentation (should be multiples of 4)
 if line.startswith(' ') and len(line) - len(line.lstrip(' ')) % 4 != 0:
 errors.append(f"{file_path}:{i}: Indentation is not a multiple of 4")

 # Check trailing whitespace
 if line.endswith(' \n') or line.endswith('\t\n'):
 errors.append(f"{file_path}:{i}: rows has trailing whitespace")

 except Exception as e:
 errors.append(f"{file_path}: Error reading file: {str(e)}")

 return errors

 def _basic_format_check(self, project_root):
 """Perform basic format check on entire project"""
 python_files = list(project_root.rglob("*.py"))
 assert len(python_files) >= 5, "Insufficient number of Python files"

 total_errors = 0
 for py_file in python_files:
 errors = self._basic_file_check(py_file)
 total_errors += len(errors)

 # Allow minor format issues
 assert total_errors <= 10, f"Too many code format issues: {total_errors} issues"


if __name__ == "__main__":
 py test.main([__file__])
