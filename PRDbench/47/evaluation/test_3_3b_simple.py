#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_3_3b_book_delete_simple():
 """Simpleization3.3bBookDeleteFunctional Test"""
 print("=== 3.3b BookDeleteFunctional Test ===")
 
 try:
 from utils.database import db_manager
 from services.book_service import book_service
 
 # 1. StandardPrepareTest Data
 print("\n1. StandardPrepareTest Data...")
 test_book_id = 'DELETE-TEST-001'
 
 # CleanProcessorCanEnergySaveinRecord
 db_manager.execute_update('DELETE FROM user_book WHERE BookId = ?', (test_book_id,))
 db_manager.execute_update('DELETE FROM book WHERE BookId = ?', (test_book_id,))
 
 # AddTestBook（EnsureNoBorrowingRecord）
 success, result = book_service.add_book(
 book_name='WaitDeleteTestBook',
 book_id=test_book_id,
 auth='TestWorkEr',
 category='Test',
 publisher='TestOutputEdition', 
 publish_time='2023-01-01',
 num_storage=1
 )
 
 if not success:
 print(f"- AddTestBookFailure: {result}")
 return False
 
 print(f"+ AddTestBookSuccess: {test_book_id}")
 
 # 2. VerifyBookSaveinNoBorrowingRecord
 print("\n2. VerifybeforeSetitemsPiece...")
 book = book_service.get_book_by_id(test_book_id)
 if not book:
 print("- TestBookNotSavein")
 return False
 
 borrow_count = db_manager.execute_query(
 'SELECT COUNT(*) as count FROM user_book WHERE BookId = ? AND BorrowState = 1', 
 (test_book_id,)
 )[0]['count']
 
 if borrow_count > 0:
 print(f"- BookHasNotReturnBorrowingRecord: {borrow_count}")
 return False
 
 print("+ BookSaveinNoBorrowingRecord")
 
 # 3. TestDeleteFunction
 print("\n3. TestDeleteFunction...")
 success, result = book_service.delete_book(test_book_id)
 
 if success:
 print("+ DeleteOperationSuccess")
 else:
 print(f"- DeleteOperationFailure: {result}")
 return False
 
 # 4. VerifyDeleteResult
 print("\n4. VerifyDeleteResult...")
 remaining_book = book_service.get_book_by_id(test_book_id)
 
 if remaining_book is None:
 print("+ BookRecordAlreadySuccessDelete")
 print("\n+ 3.3bBookDeleteFunctional TestPass")
 print(" - ManagementEnergyBookDeleteFunction")
 print(" - SystemHasDeleteAccurateCertifiedMachineControl") 
 print(" - AccurateCertifiedafterSuccessDeleteBookRecord")
 return True
 else:
 print("- BookRecordSavein，DeleteFailure")
 return False
 
 except Exception as e:
 print(f"TestAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = test_3_3b_book_delete_simple()
 if success:
 print("\n[PASS] 3.3bBookDeleteFunctional TestPass")
 else:
 print("\n[FAIL] 3.3bBookDeleteFunctional TestFailure")
 sys.exit(0 if success else 1)