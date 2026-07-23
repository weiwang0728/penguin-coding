# -*- coding: utf-8 -*-
"""LibrarySaveCheckTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.borrow_service import borrow_service
from services.auth_service import auth_service
from services.user_service import user_service

def setup_database():
 """EnsureTest Database"""
 try:
 from config.database_mode import db_mode_manager
 # StrongControlSwitchChangetoSQLite Mode
 db_mode_manager.switch_to_sqlite()
 
 # UsesSystemDatabaseManager
 from utils.database import db_manager
 
 return db_manager
 except Exception as e:
 pytest.skip(f"DatabaseEnsureFailure: {str(e)}")

def test_stock_check():
 """TestLibrarySaveCheckFunction"""
 db_manager = setup_database()
 book_id = "TESTZEROSTOCK"
 user_id = "TESTUSERSTOCK"
 
 try:
 # CleanProcessorTest Data
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
 db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (user_id,))
 
 # CreateTest User
 db_manager.execute_update("""
 INSERT INTO user (StudentId, Name, Password, IsAdmin, tel)
 VALUES (?, ?, ?, ?, ?)
 """, (user_id, "Test User", "hashedpwd", 0, "test@test.com"))
 
 # CreateLibrarySaveas0TestBook
 db_manager.execute_update("""
 INSERT INTO book (BookName, BookId, Auth, NumStorage, NumCanBorrow)
 VALUES (?, ?, ?, ?, ?)
 """, ("TestBook", book_id, "TestWorkEr", 1, 0))
 
 # ModelSimulationUserlogin
 user = user_service.get_user_by_id(user_id)
 if user:
 auth_service.current_user = user
 
 success, result = borrow_service.borrow_book(user_id, book_id)
 assert not success, "ShouldThisBorrowingLibrarySaveas0Book"
 assert "LibrarySave" in result or "Not" in result, f"ShouldImproved toLibrarySaveNot: {result}"
 
 print("Test Passed：CorrectAccurateBorrowingLibrarySaveas0Book")
 finally:
 try:
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
 db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (user_id,))
 except:
 pass
