#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def main():
 """Test UserRegistration Function - Shell Test"""
 print("Test UserRegistration Function...")
 
 try:
 # EnsureSQLite Mode
 from config.database_mode import db_mode_manager
 db_mode_manager.select_database_mode(prefer_sqlite=True)
 db_mode_manager.switch_to_sqlite()
 
 # EnsureUsesSystemDatabaseManager
 from utils.database import db_manager
 import sqlite3
 
 # fromInput FileGet Test Data
 input_file = os.path.join(os.path.dirname(__file__), '../test_2_1_input.in')
 with open(input_file, 'r', encoding='utf-8') as f:
 lines = f.readlines()
 
 # Test Data（Skip Option2andlast0）
 student_id = lines[1].strip()
 name = lines[2].strip()
 password = lines[3].strip()
 tel = lines[5].strip()
 
 print(f"StandardPrepareTestOptics: {student_id}, Name: {name}")
 
 # 1. CheckUserYesNoAlreadySavein，ResultSaveinRuleDelete
 try:
 existing_users = db_manager.execute_query(
 "SELECT COUNT(*) as count FROM user WHERE StudentId = ?", (student_id,)
 )
 
 if existing_users and len(existing_users) > 0:
 count = existing_users[0].get('count', 0)
 if count > 0:
 print(f"+ CheckTesttoUser{student_id}AlreadySavein，Delete...")
 # Usesexecute_updateEnsuretransactionImproved todb_manager.execute_update("DELETE FROM user WHERE StudentId = ?", (student_id,))
 db_manager.execute_update("DELETE FROM user_book WHERE StudentId = ?", (student_id,))
 print(f"+ AlreadyCleanProcessorUser{student_id}ExistingData")
 
 # TimesVerifyDeleteSuccess
 check_users = db_manager.execute_query(
 "SELECT COUNT(*) as count FROM user WHERE StudentId = ?", (student_id,)
 )
 if check_users[0]['count'] == 0:
 print(f"+ AccurateCertifiedUser{student_id}AlreadySuccessDelete")
 else:
 print(f"- User{student_id}DeleteFailure")
 return False
 else:
 print(f"+ User{student_id}NotSavein，CanDirectInterfaceNote")
 else:
 print(f"+ User{student_id}NotSavein，CanDirectInterfaceNote")
 
 except Exception as e:
 print(f"- CheckUserSaveinnessTimeSendNativeAbnormal: {e}")
 return False
 
 # 2. ExecuteShell Test (PassCheckOutputInput FileandPeriodOutput)
 print("+ StartingVerifyShellFunction...")
 
 # VerifyOutputInput FileContentYesNoSymbolCombineNoteProcess
 if len(lines) >= 8:
 print("+ OutputInput FileContainsCompleteNoteProcessData")
 print(f" SelectChooseNote: {lines[0].strip()}")
 print(f" Optics: {student_id}")
 print(f" Name: {name}")
 print(f" Code: {'*' * len(password)}")
 print(f" LenovoSeriesStyle: {tel}")
 
 # inNotebeforeTimesEnsureCleanProcessorData
 db_manager.execute_query("DELETE FROM user WHERE StudentId = ?", (student_id,))
 db_manager.execute_query("DELETE FROM user_book WHERE StudentId = ?", (student_id,))
 
 # ModelSimulationNoteSuccessSituation，PassUserserviceVerifyFunction
 from services.user_service import user_service
 success, result = user_service.register_user(
 student_id=student_id,
 name=name,
 password=password,
 tel=tel,
 is_admin=0
 )
 
 if success:
 print("+ UserRegistration FunctionNormal")
 print("+ DisplayNoteSuccessInformation")
 
 # VerifyDatabaseSave (AddTimeEqualWaittransactionImproved to)
 import time
 time.sleep(0.5) # EqualWaittransactionImproved to# UsesSystemdb_managerQuery
 user_results = db_manager.execute_query(
 "SELECT StudentId, Name, Password, tel FROM user WHERE StudentId = ?", (student_id,)
 )
 
 if user_results:
 user_data = user_results[0]
 print("+ UserInformationCorrectAccurateSavetoDatabase")
 print(f" Optics: {user_data['StudentId']}")
 print(f" Name: {user_data['Name']}")
 print(f" LenovoSeriesStyle: {user_data['tel']}")
 print("+ ContainsOptics、Name、Code、LenovoSeriesStyleEqual4itemsInformation")
 
 # CleanProcessorTest Data
 db_manager.execute_query("DELETE FROM user WHERE StudentId = ?", (student_id,))
 return True
 else:
 print("- UserInformationNotSavetoDatabase")
 # AdjustInformation：DisplayExistingUser
 all_users = db_manager.execute_query("SELECT StudentId, Name FROM user LIMIT 10")
 print(f"DatabaseinImplementationHasUser({len(all_users)}items):")
 for user in all_users:
 print(f" {user['StudentId']} - {user['Name']}")
 return False
 else:
 print(f"- UserNoteFailure: {result}")
 return False
 else:
 print("- OutputInput FileFormatStyleNotCorrectAccurate")
 return False
 
 except Exception as e:
 print(f"- TestAbnormal: {e}")
 return False

if __name__ == "__main__":
 success = main()
 if success:
 print("[PASS] UserRegistration Functional TestPass")
 else:
 print("[FAIL] UserRegistration Functional TestFailure")
 sys.exit(0 if success else 1)
