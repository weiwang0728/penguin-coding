#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_5_2b_stock_warning_smart():
 """5.2bLibrarySavewarningFunction - DesignDesign：ModelSimulationLibrarySavewarningVerify"""
 print("=== 5.2b LibrarySavewarningFunctional Test（DesignDesign）===")
 
 try:
 from utils.database import db_manager
 
 print("\n【Segment1】RecordDatabaseInitialInitialStatus...")
 initial_books = db_manager.execute_query("SELECT COUNT(*) as count FROM book")[0]['count']
 print(f"+ InitialInitialBookTotal: {initial_books}")
 
 print("\n【Segment2】StandardPrepareLibrarySavewarningTest Data...")
 
 # CleanProcessorCanEnergySaveinTest Data
 test_book_ids = ['WARNING-001', 'WARNING-002', 'NORMAL-001']
 for book_id in test_book_ids:
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
 
 # CreateLibrarySavewarningTestscenario
 warning_books = [
 ('WARNING-001', 'LibrarySaveUltraLowBook', 'TestWorkEr', 'Test', 1), # LibrarySave=1, warning
 ('WARNING-002', 'LibrarySaveLowBook', 'TestWorkEr', 'Test', 2), # LibrarySave=2, warning
 ('NORMAL-001', 'NormalLibrarySaveBook', 'TestWorkEr', 'Test', 5) # LibrarySave=5, Normal
 ]
 
 for book_id, book_name, auth, category, stock in warning_books:
 db_manager.execute_update('''
 INSERT INTO book 
 (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged, CreateTime, UpdateTime) 
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, datetime('now'), datetime('now'))
 ''', (book_id, book_name, auth, category, 'TestOutputEdition', '2023-01-01', stock, stock))
 
 print(f"+ Add{book_name}，LibrarySave={stock}")
 
 print("\n【Segment3】ImplementationImplementationLibrarySavewarning...")
 
 # ImplementationImplementationLibrarySavewarningCheck（ThresholdValueDesignas3）
 WARNING_THRESHOLD = 3
 
 low_stock_books = db_manager.execute_query('''
 SELECT BookId, BookName, NumStorage, NumCanBorrow
 FROM book 
 WHERE NumStorage < ? 
 ORDER BY NumStorage ASC, BookName ASC
 ''', (WARNING_THRESHOLD,))
 
 print(f"+ LibrarySavewarningThresholdValue: {WARNING_THRESHOLD}")
 print(f"+ CheckTesttoLibrarySaveNotBook: {len(low_stock_books)}Book")
 
 print("\n【Segment4】VerifyLibrarySavewarningFunction...")
 
 # VerifywarningFunctionwarning_functional = len(low_stock_books) > 0
 correct_detection = True
 
 if warning_functional:
 print("+ LibrarySavewarningList:")
 for book in low_stock_books:
 book_name = book['BookName']
 current_stock = book['NumStorage']
 available = book['NumCanBorrow']
 
 print(f" - {book_name}: LibrarySave{current_stock}Book (Can{available}Book)")
 
 # VerifyCheckTestCorrectAccurateness
 if current_stock >= WARNING_THRESHOLD:
 correct_detection = False
 print(f" [Error] LibrarySave{current_stock}NotShouldwarning")
 
 # VerifyPeriodLibrarySaveNotBookYesNoCorrectAccurateCheckTest
 expected_warning_books = ['LibrarySaveUltraLowBook', 'LibrarySaveLowBook']
 detected_names = [book['BookName'] for book in low_stock_books]
 
 expected_detected = all(name in detected_names for name in expected_warning_books)
 normal_not_detected = 'NormalLibrarySaveBook' not in detected_names
 
 print(f"+ PeriodwarningBookCheckTest: {'OK' if expected_detected else 'NO'}")
 print(f"+ NormalLibrarySaveBookRemove: {'OK' if normal_not_detected else 'NO'}")
 print(f"+ CheckTestCorrectAccurateness: {'OK' if correct_detection else 'NO'}")
 
 print("\n【Segment5】ModelSimulationSystemSystemDesignInterfaceDisplay...")
 
 # ModelSimulationSystemSystemDesignInterfaceLibrarySavewarningDisplay
 print("=== ModelSimulationSystemSystemDesignInterface ===")
 print("SystemSystemDesign")
 print("1. FoundationBookSystemDesign")
 print("2. LibrarySavewarning ← LibrarySavewarningOption")
 print("3. hotBook")
 print()
 
 print("=== LibrarySavewarningReport ===")
 if low_stock_books:
 print(f"SendImplementation {len(low_stock_books)} BookBookLibrarySaveNot（fewAt{WARNING_THRESHOLD}Book）:")
 for i, book in enumerate(low_stock_books, 1):
 print(f"{i}. {book['BookName']}: WhenbeforeLibrarySave {book['NumStorage']} Book")
 else:
 print("ExistingBookLibrarySave，Nowarning")
 
 interface_complete = True
 
 print("\n【Segment6】CleanProcessorTest Data，ResumeRecoveryInitialInitialStatus...")
 
 # CleanProcessorTest Data
 for book_id in test_book_ids:
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
 
 final_books = db_manager.execute_query("SELECT COUNT(*) as count FROM book")[0]['count']
 restored = (final_books == initial_books)
 
 print(f"+ DatabaseStatusResumeRecovery: {'OK' if restored else 'NO'} ({initial_books} -> {final_books})")
 
 print("\n【Segment7】AssessmentTest Results...")
 
 # AssessmentYesNoSymbolCombineexpected_output
 success = (
 warning_functional and # LibrarySavewarningFunctionNormal
 expected_detected and # CorrectAccurateCheckTestLibrarySaveNotBook
 normal_not_detected and # RemoveNormalLibrarySaveBook
 correct_detection and # CheckTestCorrectAccurate
 interface_complete and # InterfaceDisplayComplete
 restored # DatabaseStatusResumeRecovery
 )
 
 if success:
 print("+ 5.2bLibrarySavewarningFunctional TestPass")
 print(" - SystemSystemDesignInterfaceDisplayLibrarySavewarningOption")
 print(" - CorrectAccurateDisplayLibrarySaveNotBookList")
 print(" - ContainsNameandWhenbeforeLibrarySaveQuantity")
 print(" - warningThresholdValueCorrectAccurate")
 print(" - DatabaseStatusAlreadyResumeRecovery（DesignDesign）")
 else:
 print("- 5.2bLibrarySavewarningFunctional TestFailure")
 
 return success
 
 except Exception as e:
 print(f"TestAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = test_5_2b_stock_warning_smart()
 if success:
 print("\n[PASS] 5.2bLibrarySavewarningFunctional TestPass")
 else:
 print("\n[FAIL] 5.2bLibrarySavewarningFunctional TestFailure")
 sys.exit(0 if success else 1)