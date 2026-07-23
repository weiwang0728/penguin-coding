#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Import Issues Helper Script

Since src/credit_assessment/utils/__init__.py does not export LoggerMixin,
we create a fix script in the evaluation directory to resolve the import issue
"""

import sys
import os
from pathlib import Path

# Add src path to system path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import LoggerMixin directly from logger module and add to utils namespace
try:
 from credit_assessment.utils.logger import LoggerMixin, OperationLogger
 import credit_assessment.utils as utils_module

 # Dynamically add LoggerMixin to utils module
 setattr(utils_module, 'LoggerMixin', LoggerMixin)
 setattr(utils_module, 'OperationLogger', OperationLogger)

 print("Successfully fixed LoggerMixin import issue")

except ImportError as e:
 print(f"Import fix failed: {e}")

if __name__ == "__main__":
 print("LoggerMixin fix script executed successfully")