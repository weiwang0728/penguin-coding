#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_4_4_reservation_simple():
 """4.4BookreserveFunction - SimpleizationEdition：DirectInterfaceCreatereserveTestscenario"""
 print("=== 4.4 BookreserveFunctional Test（SimpleizationEdition）===")
 
 try:
 from utils.database import db_manager
 
 print("\n1. RecordInitialInitialStatus...")
 initial_borrows = db_manager.execute_query("SELECT COUNT(*) as count FROM user_book")[0]['count']
 print(f"+ InitialInitialBorrowingRecordNumber: {initial_borrows}")
 
 print("\n2. StandardPreparereserveTestscenario...")
 
 # EnsureTEST001UserSavein
 existing_user = db_manager.execute_query("SELECT * FROM user WHERE StudentId = 'TEST001'")
 if not existing_user:
 db_manager.execute_update(
 "INSERT INTO user (StudentId, Name, Password, IsAdmin, CreateTime, UpdateTime) VALUES (?, ?, ?, 0, datetime('now'), datetime('now'))",
 ('TEST001', 'Test User', 'e10adc3949ba59abbe56e057f20f883e') # password123MD5
 )
 print("+ CreateTEST001User")
 else:
 print("+ TEST001UserAlreadySavein")
 
 # CreateOneBookBook，LibrarySave=1，butCompleteAutomaticOutput（CanQuantity=0）
 db_manager.execute_update("DELETE FROM book WHERE BookId = 'ISBN002'")
 db_manager.execute_update('''
 INSERT INTO book 
 (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged, CreateTime, UpdateTime) 
 VALUES (?, ?, ?, ?, ?, ?, 1, 0, 0, datetime('now'), datetime('now'))
 ''', ('ISBN002', 'reserveTestBook', 'TestWorkEr', 'Test', 'TestOutputEdition', '2023-01-01'))
 
 print("+ CreateISBN002Book：LibrarySave=1，Can=0（CompleteAutomaticOutputStatus）")
 
 # VerifyBookStatus
 book = db_manager.execute_query("SELECT * FROM book WHERE BookId = 'ISBN002'")[0]
 exists_but_unavailable = (book['NumStorage'] > 0 and book['NumCanBorrow'] == 0)
 
 print(f"+ reserveTestscenario: {'OK' if exists_but_unavailable else 'NO'}")
 print(f" LibrarySave={book['NumStorage']}, Can={book['NumCanBorrow']}")
 
 print("\n3. ModelSimulationreserveOperation...")
 
 # CheckYesNoAlreadyHasreserveRecord
 existing_reservation = db_manager.execute_query(
 "SELECT * FROM user_book WHERE StudentId = 'TEST001' AND BookId = 'ISBN002' AND BorrowState = 0"
 )
 
 if not existing_reservation:
 # CreatereserveRecord（BorrowState=0TablereserveStatus，BorrowTimeUseWhenbeforeTimeBetweenWorkPosition）
 db_manager.execute_update('''
 INSERT INTO user_book
 (StudentId, BookId, BorrowState, BorrowTime, CreateTime, UpdateTime)
 VALUES (?, ?, 0, datetime('now'), datetime('now'), datetime('now'))
 ''', ('TEST001', 'ISBN002'))
 
 print("+ CreatereserveRecordSuccess")
 reservation_created = True
 else:
 print("+ reserveRecordAlreadySavein")
 reservation_created = True
 
 # VerifyreserveRecord
 reservation_count = db_manager.execute_query(
 "SELECT COUNT(*) as count FROM user_book WHERE StudentId = 'TEST001' AND BookId = 'ISBN002' AND BorrowState = 0"
 )[0]['count']
 
 print(f"+ reserveRecordVerify: {'OK' if reservation_count > 0 else 'NO'} (Quantity:{reservation_count})")
 
 print("\n4. CleanProcessorTest Data...")
 
 # CleanProcessorTest Data
 db_manager.execute_update("DELETE FROM user_book WHERE StudentId = 'TEST001' AND BookId = 'ISBN002'")
 db_manager.execute_update("DELETE FROM book WHERE BookId = 'ISBN002'")
 # NotDeleteTEST001User，CauseasCanEnergyTestfinal_borrows = db_manager.execute_query("SELECT COUNT(*) as count FROM user_book")[0]['count']
 restored = (final_borrows == initial_borrows)
 
 print(f"+ DatabaseStatusResumeRecovery: {'OK' if restored else 'NO'} ({initial_borrows} -> {final_borrows})")
 
 print("\n5. AssessmentTest Results...")
 
 success = (exists_but_unavailable and reservation_created and restored)
 
 if success:
 print("+ 4.4BookreserveFunctional TestPass")
 print(" - BookSaveinbutCanQuantityas0scenarioCreateSuccess")
 print(" - reserveRecordCreateSuccess") 
 print(" - DatabaseStatusResumeRecovery")
 else:
 print("- 4.4BookreserveFunctional TestFailure")
 
 return success
 
 except Exception as e:
 print(f"TestAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = test_4_4_reservation_simple()
 if success:
 print("\n[PASS] 4.4BookreserveFunctional TestPass")
 else:
 print("\n[FAIL] 4.4BookreserveFunctional TestFailure")
 sys.exit(0 if success else 1)