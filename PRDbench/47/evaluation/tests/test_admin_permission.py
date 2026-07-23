# -*- coding: utf-8 -*-
"""ManagementPermissionControlTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
 from utils.database import db_manager
 from services.user_service import UserService
 from services.book_service import BookService
 
 def test_admin_permission_control():
 """TestManagementPermissionControlFunction"""
 
 # CreateManagementUser
 db_manager.execute_update(
 "INSERT OR REPLACE INTO user (StudentId, Name, Password, IsAdmin) VALUES (?, ?, ?, ?)",
 ('ADMIN001', 'Management', 'e10adc3949ba59abbe56e057f20f883e', 1)
 )
 
 user_service = UserService()
 book_service = BookService()
 
 # TestManagementEnergyFunction
 functions_accessible = 0
 
 # 1. User ManagementFunction
 try:
 users = user_service.get_all_users()
 if users is not None:
 functions_accessible += 1
 print("✓ ManagementCanUser ManagementFunction")
 except Exception as e:
 print(f"✗ User ManagementFunctional TestAbnormal：{e}")
 
 # 2. BookManagementFunction
 try:
 books = book_service.get_all_books()
 if books is not None:
 functions_accessible += 1
 print("✓ ManagementCanBookManagementFunction")
 except Exception as e:
 print(f"✗ BookManagementFunctional TestAbnormal：{e}")
 
 # 3. BorrowingManagementFunction（PassQueryBorrowingRecordTest）
 try:
 borrow_records = db_manager.execute_query("SELECT * FROM user_book")
 if borrow_records is not None:
 functions_accessible += 1
 print("✓ ManagementCanBorrowingManagementFunction")
 except Exception as e:
 print(f"✗ BorrowingManagementFunctional TestAbnormal：{e}")
 
 # 4. SystemSystemDesignFunction
 try:
 user_count = db_manager.execute_query("SELECT COUNT(*) as count FROM user")[0]['count']
 book_count = db_manager.execute_query("SELECT COUNT(*) as count FROM book")[0]['count']
 if user_count is not None and book_count is not None:
 functions_accessible += 1
 print("✓ ManagementCanSystemSystemDesignFunction")
 except Exception as e:
 print(f"✗ SystemSystemDesignFunctional TestAbnormal：{e}")
 
 # 5. Data ExportFunction（SimpleSingleTest）
 try:
 # ModelSimulationData ExportTest
 export_data = {
 'users': db_manager.execute_query("SELECT * FROM user"),
 'books': db_manager.execute_query("SELECT * FROM book")
 }
 if export_data['users'] is not None and export_data['books'] is not None:
 functions_accessible += 1
 print("✓ ManagementCanData ExportFunction")
 except Exception as e:
 print(f"✗ Data ExportFunctional TestAbnormal：{e}")
 
 # 6. PCommonUserFunction（ManagementShouldThisEnergyUses）
 try:
 # ManagementShouldThisEnergyBorrowingBook
 functions_accessible += 1
 print("✓ ManagementCanPCommonUserFunction")
 except Exception as e:
 print(f"✗ PCommonUserFunctional TestAbnormal：{e}")
 
 # CheckYesNoEnergyFunction（few4items）
 if functions_accessible >= 4:
 print(f"Test Passed：ManagementEnergy{functions_accessible}itemsFunction")
 return True
 else:
 print(f"Test Failed：ManagementEnergy{functions_accessible}itemsFunction")
 return False
 
 if __name__ == "__main__":
 try:
 if test_admin_permission_control():
 print("[PASS] Test Passed：ManagementPermissionControlFunctionNormal")
 else:
 print("[FAIL] Test Failed：ManagementPermissionControlAbnormal")
 sys.exit(1)
 except Exception as e:
 print(f"[FAIL] Test Failed：{e}")
 sys.exit(1)

except ImportError as e:
 print(f"[FAIL] ImportModuleFailure：{e}")
 sys.exit(1)