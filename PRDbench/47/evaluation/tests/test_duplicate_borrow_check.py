# -*- coding: utf-8 -*-
"""WeightRecoveryBorrowingCheckTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
 from utils.database import db_manager
 from services.borrow_service import borrow_service
 from config.database_mode import db_mode_manager
 
 # EnsureSQLite Mode
 db_mode_manager.select_database_mode(prefer_sqlite=True)
 db_mode_manager.switch_to_sqlite()
 
 def test_duplicate_borrow_check():
 """TestWeightRecoveryBorrowingCheckFunction"""
 
 # CreateTest User
 db_manager.execute_query(
 "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
 ('TEST001', 'Test User', 'e10adc3949ba59abbe56e057f20f883e', 0)
 )
 
 # CreateTestBook
 db_manager.execute_query(
 "INSERT OR REPLACE INTO book (BookId, BookName, Auth, Category, NumStorage, NumCanBorrow) VALUES (?, ?, ?, ?, ?, ?)",
 ('ISBN001', 'PythonCodeProcess', 'Sam', 'DesignCalculateMachine', 5, 4)
 )
 
 # ModelSimulationUserAlreadyBorrowingThisBook
 from datetime import datetime
 current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 db_manager.execute_query(
 "INSERT INTO user_book (StudentId, BookId, BorrowState, BorrowTime) VALUES (?, ?, ?, ?)",
 ('TEST001', 'ISBN001', 1, current_time)
 )
 
 # WeightRecoveryBorrowingSameOneBooktry:
 result = borrow_service.borrow_book('TEST001', 'ISBN001')
 if not result['success'] and 'AlreadyBorrowing' in result['message']:
 print("Test Passed：CorrectAccurateWeightRecoveryBorrowing")
 return True
 else:
 print("Test Failed：NotWeightRecoveryBorrowing")
 return False
 except Exception as e:
 print(f"TestAbnormal：{e}")
 return False
 
 if __name__ == "__main__":
 try:
 if test_duplicate_borrow_check():
 print("[PASS] Test Passed：WeightRecoveryBorrowingCheckFunctionNormal")
 else:
 print("[FAIL] Test Failed：WeightRecoveryBorrowingCheckAbnormal")
 sys.exit(1)
 except Exception as e:
 print(f"[FAIL] Test Failed：{e}")
 sys.exit(1)

except ImportError as e:
 print(f"[FAIL] ImportModuleFailure：{e}")
 sys.exit(1)