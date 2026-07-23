#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_sqlite_crud():
 """TestSQLiteNativeImplementationImplementationFoundationFoundationIncreaseChangeFunction"""
 print("=== SQLiteFoundationFoundationFunctional Test ===")
 
 try:
 from utils.database import db_manager
 
 print(f"DatabaseManagerCategory: {type(db_manager)}")
 
 # 1. TestInterface
 print("\n1. Test DatabaseInterface...")
 if db_manager.test_connection():
 print("+ DatabaseInterfaceSuccess")
 else:
 print("- DatabaseInterfaceFailure")
 return False
 
 # 2. TestIncreasePlus (Create)
 print("\n2. TestIncreasePlusData...")
 test_book_id = "TEST-CRUD-001"
 
 # CleanProcessorCanEnergySaveinTest Data
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (test_book_id,))
 
 # AddTestBook
 insert_sql = """
 INSERT INTO book 
 (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged, CreateTime, UpdateTime)
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
 """
 result = db_manager.execute_update(insert_sql, (
 test_book_id, "SQLiteTestBook", "TestWorkEr", "TestClassification", 
 "TestOutputEdition", "2023-01-01", 3, 3, 0
 ))
 
 if result > 0:
 print("+ AddDataSuccess")
 else:
 print("- AddDataFailure")
 return False
 
 # 3. TestQuery (Read)
 print("\n3. TestQueryData...")
 select_sql = "SELECT BookId, BookName, Auth, NumStorage FROM book WHERE BookId = ?"
 books = db_manager.execute_query(select_sql, (test_book_id,))
 
 if books and len(books) > 0:
 book = books[0]
 print("+ QueryDataSuccess")
 print(f" book_id: {book['BookId']}")
 print(f" Name: {book['BookName']}")
 print(f" WorkEr: {book['Auth']}")
 print(f" LibrarySave: {book['NumStorage']}")
 else:
 print("- QueryDataFailure")
 return False
 
 # 4. TestModify (Update)
 print("\n4. TestModifyData...")
 update_sql = "UPDATE book SET BookName = ?, NumStorage = ?, UpdateTime = datetime('now') WHERE BookId = ?"
 result = db_manager.execute_update(update_sql, ("SQLiteModifyTestBook", 5, test_book_id))
 
 if result > 0:
 print("+ ModifyDataSuccess")
 
 # VerifyModifyResult
 books = db_manager.execute_query(select_sql, (test_book_id,))
 if books:
 book = books[0]
 print(f" ModifyafterName: {book['BookName']}")
 print(f" ModifyafterLibrarySave: {book['NumStorage']}")
 else:
 print("- ModifyDataFailure")
 return False
 
 # 5. TestDelete (Delete)
 print("\n5. TestDeleteData...")
 delete_sql = "DELETE FROM book WHERE BookId = ?"
 result = db_manager.execute_update(delete_sql, (test_book_id,))
 
 if result > 0:
 print("+ DeleteDataSuccess")
 
 # VerifyDeleteResult
 books = db_manager.execute_query(select_sql, (test_book_id,))
 if not books or len(books) == 0:
 print("+ DeleteVerifySuccess，RecordAlreadyNotSavein")
 else:
 print("- DeleteVerifyFailure，RecordSavein")
 return False
 else:
 print("- DeleteDataFailure")
 return False
 
 print("\n=== SQLiteFoundationFoundationFunctional TestAutomaticPass ===")
 return True
 
 except Exception as e:
 print(f"TestAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = test_sqlite_crud()
 if success:
 print("[PASS] SQLiteFoundationFoundationFunctional TestPass")
 else:
 print("[FAIL] SQLiteFoundationFoundationFunctional TestFailure")
 sys.exit(0 if success else 1)