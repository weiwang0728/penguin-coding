#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def main():
 """Test DatabaseInterfaceandInitialInitialization"""
 print("Test DatabaseInterface...")
 
 try:
 # ImportSwitchChangetoSQLite Mode
 from config.database_mode import db_mode_manager
 
 # CheckTestSelectChooseDatabaseMode
 db_mode = db_mode_manager.select_database_mode(prefer_sqlite=True)
 
 if db_mode == 'sqlite':
 print("+ DatabaseInterfaceSuccess（SQLite Mode）")
 
 # CheckSQLiteDatabaseTableResultStructure
 from utils.database import db_manager
 
 tables = ['user', 'book', 'user_book']
 table_count = 0
 for table in tables:
 try:
 result = db_manager.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
 if result:
 print(f"+ {table}TableSaveinCan")
 table_count += 1
 else:
 print(f"- {table}TableNotSavein")
 except Exception as e:
 print(f"- {table}TableCheckFailure: {e}")
 
 if table_count == 3:
 print("DatabaseInitialInitializationVerifySuccessfully")
 return True
 else:
 print(f"DatabaseTableResultStructureNotComplete：{table_count}/3")
 return False
 else:
 print("- DatabaseInterfaceFailure")
 return False
 except Exception as e:
 print(f"- TestAbnormal: {e}")
 return False

if __name__ == "__main__":
 success = main()
 if success:
 print("[PASS] Test Passed")
 else:
 print("[FAIL] Test Failed")
 sys.exit(0 if success else 1)