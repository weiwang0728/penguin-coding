# -*- coding: utf-8 -*-
"""SystemLogRecordTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.logger import log_operation, log_error, log_system_event
from config.settings import FILE_PATHS

def test_system_logging():
 """TestSystemLogRecordFunction"""
 
 try:
 # Test UserloginLog
 log_operation("Userlogin", "TEST001", "UserloginTest")
 
 # TestSystemPieceLog
 log_system_event("BookBorrowing", "BorrowingOperationTest")
 
 # TestErrorLog
 log_error("DataModify", "ModifyOperationTestError")
 
 # CheckLogFile
 log_file = os.path.join(FILE_PATHS.get('log_dir', 'logs'), 'system.log')
 if os.path.exists(log_file):
 with open(log_file, 'r', encoding='utf-8') as f:
 log_content = f.read()
 
 # Verify3TypeCategoryLogHasRecord
 assert "Userlogin" in log_content, "UserOperationLogNotRecord"
 assert "BookBorrowing" in log_content, "SystemPieceLogNotRecord"
 assert "DataModify" in log_content, "ErrorLogNotRecord"
 
 print("Test Passed：EnergyRecordAutomatic3TypeCategoryOperationLog")
 return True
 
 except Exception as e:
 pytest.fail(f"Test Failed: {str(e)}")
