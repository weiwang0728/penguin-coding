# -*- coding: utf-8 -*-
"""DatabaseInterfaceAbnormalProcessingTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
 from utils.database import db_manager
 
 def test_database_connection_exception():
 """Test DatabaseInterfaceAbnormalProcessingFunction"""
 
 # UsesErrorDatabasePathTestAbnormalProcessing
 original_path = db_manager.db_path
 db_manager.db_path = '/nonexistent/path/test.db'
 
 try:
 # InterfaceErrorDatabasePath
 result = db_manager.test_connection()
 if not result:
 print("Test Passed：CorrectAccurateProcessingDatabaseInterfaceAbnormal")
 db_manager.db_path = original_path
 return True
 else:
 print("Test Failed：NotCorrectAccurateProcessingDatabaseInterfaceAbnormal")
 db_manager.db_path = original_path
 return False
 except Exception as e:
 print(f"Test Passed：GettoAbnormal - {e}")
 db_manager.db_path = original_path
 return True
 
 if __name__ == "__main__":
 try:
 if test_database_connection_exception():
 print("[PASS] Test Passed：DatabaseInterfaceAbnormalProcessingFunctionNormal")
 else:
 print("[FAIL] Test Failed：DatabaseInterfaceAbnormalProcessingAbnormal")
 sys.exit(1)
 except Exception as e:
 print(f"[FAIL] Test Failed：{e}")
 sys.exit(1)

except ImportError as e:
 print(f"[FAIL] ImportModuleFailure：{e}")
 sys.exit(1)