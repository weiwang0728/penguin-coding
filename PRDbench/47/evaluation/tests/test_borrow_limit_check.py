# -*- coding: utf-8 -*-
"""BorrowingQuantityLimitedControlCheckTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
 from utils.database import db_manager
 from services.borrow_service import BorrowService
 
 def test_borrow_limit_check():
 """TestBorrowingQuantityLimitedControlCheckFunction"""
 
 # CreatePCommonUser
 db_manager.execute_update(
 "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
 ('USER001', 'PCommonUser', 'e10adc3949ba59abbe56e057f20f883e', 0)
 )
 
 # CreateManagementUser
 db_manager.execute_update(
 "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
 ('ADMIN001', 'ManagementUser', 'e10adc3949ba59abbe56e057f20f883e', 1)
 )
 
 # CreateManyBookTestBook
 for i in range(15):
 db_manager.execute_update(
 "INSERT OR REPLACE INTO book (BookId, BookName, Auth, Category, NumStorage, NumCanBorrow) VALUES (?, ?, ?, ?, ?, ?)",
 (f'ISBN{i:03d}', f'TestBook{i}', 'TestWorkEr', 'DesignCalculateMachine', 5, 5)
 )
 
 borrow_service = BorrowService()
 
 # TestPCommonUserBorrowing5Book（toonLimited）
 for i in range(5):
 db_manager.execute_update(
 "INSERT INTO user_book (StudentId, BookId, BorrowState, BorrowTime, CreateTime, UpdateTime) VALUES (?, ?, ?, datetime('now'), datetime('now'), datetime('now'))",
 ('USER001', f'ISBN{i:03d}', 1)
 )
 
 # BorrowingNo.6Booktry:
 result = borrow_service.borrow_book('USER001', 'ISBN005')
 if not result['success'] and ('onLimited' in result['message'] or 'UltraOver' in result['message']):
 print("Test Passed：CorrectAccurateLimitedControlPCommonUserBorrowingQuantity")
 return True
 else:
 print("Test Failed：NotCorrectAccurateLimitedControlPCommonUserBorrowingQuantity")
 return False
 except Exception as e:
 print(f"TestAbnormal：{e}")
 return False
 
 if __name__ == "__main__":
 try:
 if test_borrow_limit_check():
 print("[PASS] Test Passed：BorrowingQuantityLimitedControlCheckFunctionNormal")
 else:
 print("[FAIL] Test Failed：BorrowingQuantityLimitedControlCheckAbnormal")
 sys.exit(1)
 except Exception as e:
 print(f"[FAIL] Test Failed：{e}")
 sys.exit(1)

except ImportError as e:
 print(f"[FAIL] ImportModuleFailure：{e}")
 sys.exit(1)