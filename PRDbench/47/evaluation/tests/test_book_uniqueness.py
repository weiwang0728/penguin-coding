# -*- coding: utf-8 -*-
"""book_idOnenessVerifyTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.book_service import book_service

def setup_database():
 """EnsureTest Database"""
 try:
 from config.database_mode import db_mode_manager
 # StrongControlSwitchChangetoSQLite Mode
 db_mode_manager.switch_to_sqlite()
 
 # EnsureExistingModuleUsesSQLiteManager
 from utils.database import db_manager
 
 return db_manager
 except Exception as e:
 pytest.skip(f"DatabaseEnsureFailure: {str(e)}")

def test_book_id_uniqueness():
 """Testbook_idOnenessCheckFunction"""
 db_manager = setup_database()
 book_id = "TESTBOOK001"
 
 try:
 # CleanProcessorTest Data
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
 
 # FirstTimesAdd
 success1, result1 = book_service.add_book(
 book_name="TestBook", book_id=book_id, auth="TestWorkEr",
 category="Test", publisher="TestOutputEdition",
 publish_time="2023-01-01", num_storage=5
 )
 assert success1, f"FirstTimesAddFailure: {result1}"
 
 # SecondTimesAddCameraSamebook_id
 success2, result2 = book_service.add_book(
 book_name="TestBook2", book_id=book_id, auth="TestWorkEr2"
 )
 assert not success2, "ShouldThisCheckTesttoWeightRecoverybook_id"
 assert "AlreadySavein" in result2 or "WeightRecovery" in result2, f"ErrorInformationShouldImproved toWeightRecovery: {result2}"
 
 print("Test Passed：book_idOnenessCheckNormal")
 finally:
 try:
 db_manager.execute_update("DELETE FROM book WHERE BookId = ?", (book_id,))
 except:
 pass
