#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def main():
 """TestBookAddFunction"""
 print("TestBookAddFunction...")
 
 try:
 # EnsureSQLite Mode
 from config.database_mode import db_mode_manager
 db_mode_manager.select_database_mode(prefer_sqlite=True)
 db_mode_manager.switch_to_sqlite()
 
 from services.book_service import book_service
 from utils.database import db_manager
 
 # StandardPrepareTest Data
 book_data = {
 "book_name": "TestBookAdd",
 "book_id": "9787111234567",
 "auth": "TestWorkEr",
 "category": "TestClassification",
 "publisher": "TestOutputEdition",
 "publish_time": "2023-01-01",
 "num_storage": 5
 }
 
 # 1. CheckBookYesNoAlreadySavein，ResultSaveinRuleDelete
 try:
 existing_books = db_manager.execute_query(
 "SELECT COUNT(*) as count FROM book WHERE BookId = ?", (book_data["book_id"],)
 )
 
 if existing_books and len(existing_books) > 0:
 count = existing_books[0].get('count', 0)
 if count > 0:
 print(f"+ CheckTesttoBook{book_data['book_id']}AlreadySavein，Delete...")
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_data["book_id"],))
 db_manager.execute_update("DELETE FROM user_book WHERE BookId = ?", (book_data["book_id"],))
 print(f"+ AlreadyCleanProcessorBook{book_data['book_id']}ExistingData")
 
 # TimesVerifyDeleteSuccess
 check_books = db_manager.execute_query(
 "SELECT COUNT(*) as count FROM book WHERE BookId = ?", (book_data["book_id"],)
 )
 if check_books[0]['count'] == 0:
 print(f"+ AccurateCertifiedBook{book_data['book_id']}AlreadySuccessDelete")
 else:
 print(f"- Book{book_data['book_id']}DeleteFailure")
 return False
 else:
 print(f"+ Book{book_data['book_id']}NotSavein，CanDirectInterfaceAdd")
 else:
 print(f"+ Book{book_data['book_id']}NotSavein，CanDirectInterfaceAdd")
 
 except Exception as e:
 print(f"- CheckBookSaveinnessTimeSendNativeAbnormal: {e}")
 return False
 
 # inAddbeforeTimesEnsureCleanProcessorData
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_data["book_id"],))
 db_manager.execute_update("DELETE FROM user_book WHERE BookId = ?", (book_data["book_id"],))
 
 # 2. TestAddBook
 success, result = book_service.add_book(**book_data)
 
 if success:
 print("+ BookAddSuccess")
 print("+ DisplayAddSuccessInformation")
 
 # 3. VerifyDatabaseinData
 import time
 time.sleep(0.5) # EqualWaittransactionImproved tobook_results = db_manager.execute_query(
 "SELECT BookName, BookId, Auth, Category, Publisher, PublishTime, NumStorage FROM book WHERE BookId = ?", (book_data["book_id"],)
 )
 
 if book_results:
 book_db_data = book_results[0]
 print("+ BookInformationCorrectAccurateSavetoDatabase")
 print(f" Name: {book_db_data['BookName']}")
 print(f" book_id: {book_db_data['BookId']}")
 print(f" WorkEr: {book_db_data['Auth']}")
 print(f" Classification: {book_db_data['Category']}")
 print(f" OutputEdition: {book_db_data['Publisher']}")
 print(f" OutputEditionTimeBetween: {book_db_data['PublishTime']}")
 print(f" LibrarySaveQuantity: {book_db_data['NumStorage']}")
 print("+ ContainsName、book_id、WorkEr、Classification、OutputEdition、OutputEditionTimeBetween、LibrarySaveQuantityEqual7itemsInformation")
 
 # CleanProcessorTest Data
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_data["book_id"],))
 return True
 else:
 print("- BookInformationNotSavetoDatabase")
 # AdjustInformation：DisplayExistingBook
 all_books = db_manager.execute_query("SELECT BookId, BookName FROM book LIMIT 10")
 print(f"DatabaseinImplementationHasBook({len(all_books)}items):")
 for book in all_books:
 print(f" {book['BookId']} - {book['BookName']}")
 return False
 else:
 print(f"- BookAddFailure: {result}")
 return False
 
 except Exception as e:
 print(f"- TestAbnormal: {e}")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
