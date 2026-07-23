#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def fix_test_imports_in_file(filepath):
 """FixedTest FileinImportIssue"""
 try:
 with open(filepath, 'r', encoding='utf-8') as f:
 content = f.read()
 
 original_content = content
 
 # ChangeEachTypesqliteImportasSystemdb_managerImport
 replacements = [
 # Change sqlite_database ModuleImport
 (r'from sqlite_database import sqlite_manager', 'from utils.database import db_manager'),
 (r'from utils\.sqlite_database import sqlite_db_manager', 'from utils.database import db_manager'),
 
 # ChangeObjectImportUse
 (r'sqlite_manager\.', 'db_manager.'),
 (r'sqlite_db_manager\.', 'db_manager.'),
 
 # MoveRemoveinit_databaseAdjustUse（Newdb_managerNot）
 (r'db_manager\.init_database\(\)\s*\n', ''),
 (r'sqlite_db_manager\.init_database\(\)\s*\n', ''),
 (r'sqlite_manager\.init_database\(\)\s*\n', ''),
 ]
 
 for pattern, replacement in replacements:
 content = re.sub(pattern, replacement, content)
 
 if content != original_content:
 with open(filepath, 'w', encoding='utf-8') as f:
 f.write(content)
 print(f'+ AlreadyFixed: {filepath}')
 return True
 else:
 print(f'- NoFixed: {filepath}')
 return False
 
 except Exception as e:
 print(f'x FixedFailure: {filepath} - {e}')
 return False

def main():
 """BatchFixedevaluation/testsDirectoryunderImportIssue"""
 tests_dir = 'evaluation/tests'
 fixed_count = 0
 
 print("StartingBatchFixedevaluation/testsinImportIssue...")
 
 # FixedFileList
 files_to_fix = [
 'test_database_exception.py',
 'test_duplicate_borrow_check.py', 
 'test_stock_check.py',
 'test_password_encryption.py',
 'test_book_uniqueness.py',
 'test_database_init.py',
 'test_1_1_DatabaseInterfaceandInitialInitialization.py'
 ]
 
 for filename in files_to_fix:
 filepath = os.path.join(tests_dir, filename)
 if os.path.exists(filepath):
 if fix_test_imports_in_file(filepath):
 fixed_count += 1
 else:
 print(f'- FileNotSavein: {filepath}')
 
 print(f"FixedSuccessfully！Fixed {fixed_count} itemsTest File")

if __name__ == "__main__":
 main()