# -*- coding: utf-8 -*-
"""Code and SaveVerifyTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.user_service import user_service
from utils.encrypt import encryptor

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

def test_password_encryption():
 """TestCode and SaveFunction"""
 db_manager = setup_database()
 student_id = "TESTPWD001" # ContainsCharacterandNumber
 password = "password123"
 
 try:
 # CleanProcessorTest Data
 db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (student_id,))
 
 success, result = user_service.register_user(student_id, "Test User", password)
 assert success, f"UserNoteFailure: {result}"
 
 # QueryCode
 results = db_manager.execute_query("SELECT Password FROM user WHERE StudentId = ?", (student_id,))
 assert results, "UserNotSavetoDatabase"
 stored_password = results[0]['Password']
 
 assert len(stored_password) == 32, f"CodeLengthRepublicNotCorrectAccurate，Shouldas32Position"
 assert stored_password != password, "CodeNot and "
 assert stored_password == encryptor.md5_hash(password), "MD5 and ResultNotCorrectAccurate"
 
 print("Test Passed：CodeCorrectAccurate and as32PositionMD5HasselbladValue")
 finally:
 try:
 db_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (student_id,))
 except:
 pass
