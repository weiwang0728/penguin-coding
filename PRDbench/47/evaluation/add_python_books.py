#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def add_python_books():
 """Add3BookContainsPythonBook，printProcess"""
 print("=== AddPythonBookProcess ===\n")
 
 try:
 # 1. ImportModule
 print("1. ImportModule...")
 from utils.database import db_manager
 from services.book_service import book_service
 print(f"+ db_managerCategory: {type(db_manager)}")
 print(f"+ book_serviceCategory: {type(book_service)}")
 
 # 2. Test DatabaseInterface
 print("\n2. Test DatabaseInterface...")
 if db_manager.test_connection():
 print("+ DatabaseInterfaceSuccess")
 else:
 print("- DatabaseInterfaceFailure")
 return False
 
 # 3. CheckWhenbeforeDatabaseStatus
 print("\n3. CheckWhenbeforeDatabaseStatus...")
 all_books = db_manager.execute_query("SELECT BookId, BookName FROM book")
 print(f"+ DatabaseinWhenbeforeBookTotal: {len(all_books)}")
 
 python_books_current = db_manager.execute_query(
 "SELECT BookName FROM book WHERE BookName LIKE ?", ('%Python%',)
 )
 print(f"+ WhenbeforeContainsPythonBook: {len(python_books_current)}Book")
 
 # 4. StandardPrepareAddBookData
 print("\n4. StandardPrepareBookData...")
 python_books = [
 {
 'book_name': 'PythonCodeProcess：fromInputtoImplementation',
 'book_id': '978-7-111-54742-6',
 'auth': '·',
 'category': 'DesignCalculateMachine',
 'publisher': 'MachineMechanicalEngineeringOutputEdition',
 'publish_time': '2016-07-01',
 'num_storage': 5
 },
 {
 'book_name': 'TrendPython',
 'book_id': '978-7-115-42884-6', 
 'auth': 'Luciano Ramalho',
 'category': 'DesignCalculateMachine',
 'publisher': 'PersonOutputEdition',
 'publish_time': '2017-05-01',
 'num_storage': 3
 },
 {
 'book_name': 'PythonCoreCodeProcess',
 'book_id': '978-7-115-28533-4',
 'auth': 'Wesley J. Chun',
 'category': 'DesignCalculateMachine',
 'publisher': 'PersonOutputEdition',
 'publish_time': '2012-06-01',
 'num_storage': 4
 }
 ]
 
 # AddSamBookSmallzhangsan_books = [
 {
 'book_name': 'Day',
 'book_id': '978-7-5086-5001-0',
 'auth': 'Sam',
 'category': 'TextOptics',
 'publisher': 'WorkPlayerOutputEdition',
 'publish_time': '2020-03-01',
 'num_storage': 6
 },
 {
 'book_name': 'dayReturn',
 'book_id': '978-7-5086-5002-7',
 'auth': 'Sam',
 'category': 'TextOptics',
 'publisher': 'PersonTextOpticsOutputEdition',
 'publish_time': '2021-07-01',
 'num_storage': 4
 }
 ]
 
 # AddOneBook（UseAtbook_idEliteAccurateQueryTest）
 fairy_tale_books = [
 {
 'book_name': 'NativeSet',
 'book_id': 'ISBN001',
 'auth': '··Native',
 'category': 'TextOptics',
 'publisher': 'PersonOutputEdition',
 'publish_time': '2019-09-01',
 'num_storage': 8
 }
 ]
 
 all_books = python_books + zhangsan_books + fairy_tale_books
 
 print(f"+ StandardPrepareAdd {len(python_books)} BookPythonBook")
 print(f"+ StandardPrepareAdd {len(zhangsan_books)} BookSamSmall")
 print(f"+ TotalAdd {len(all_books)} BookBook")
 
 # 5. itemsAddBook
 print("\n5. StartingAddBook...")
 success_count = 0
 
 for i, book_data in enumerate(all_books, 1):
 print(f"\n--- AddNo.{i}BookBook ---")
 print(f"Name: {book_data['book_name']}")
 print(f"book_id: {book_data['book_id']}")
 print(f"WorkEr: {book_data['auth']}")
 
 # CheckYesNoAlreadySavein
 existing = db_manager.execute_query(
 "SELECT COUNT(*) as count FROM book WHERE BookId = ?", (book_data['book_id'],)
 )
 if existing and existing[0]['count'] > 0:
 print(f"Book{book_data['book_id']}AlreadySavein，SkipAdd")
 continue
 
 # Add
 try:
 success, result = book_service.add_book(**book_data)
 if success:
 print(f"+ AddSuccess")
 success_count += 1
 
 # VerifyAddResult
 verify_books = db_manager.execute_query(
 "SELECT BookName, Auth FROM book WHERE BookId = ?", (book_data['book_id'],)
 )
 if verify_books:
 book = verify_books[0]
 print(f"+ VerifySuccess: {book['BookName']} - {book['Auth']}")
 else:
 print("- VerifyFailure: BookNotinDatabaseinto")
 
 else:
 print(f"- AddFailure: {result}")
 
 except Exception as e:
 print(f"- AddAbnormal: {e}")
 import traceback
 traceback.print_exc()
 
 # 6. FinalVerify
 print(f"\n6. FinalVerify...")
 print(f"SuccessAdd {success_count}/{len(all_books)} BookBook")
 
 # QueryExistingContainsPythonBook
 final_python_books = db_manager.execute_query(
 "SELECT BookName, Auth FROM book WHERE BookName LIKE ?", ('%Python%',)
 )
 print(f"\nDatabaseinContainsPythonBookTotal: {len(final_python_books)}Book")
 for book in final_python_books:
 print(f" {book['BookName']} - {book['Auth']}")
 
 # QuerySamBook
 zhangsan_books_final = db_manager.execute_query(
 "SELECT BookName, Auth FROM book WHERE Auth = ?", ('Sam',)
 )
 print(f"\nDatabaseinSamBookTotal: {len(zhangsan_books_final)}Book")
 for book in zhangsan_books_final:
 print(f" {book['BookName']} - {book['Auth']}")
 
 return len(final_python_books) >= 3 and len(zhangsan_books_final) >= 2
 
 except Exception as e:
 print(f"ScriptAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = add_python_books()
 if success:
 print("\n[PASS] PythonBookAddSuccessfully")
 else:
 print("\n[FAIL] PythonBookAddFailure")
 sys.exit(0 if success else 1)