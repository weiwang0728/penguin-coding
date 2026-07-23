#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def test_3_3b_book_delete():
 """Test3.3bBookDeleteFunction - ContainsDataStandardPrepareandDeleteVerify"""
 print("=== 3.3b BookDeleteFunctional Test ===\n")
 
 try:
 # 1. DataStandardPrepare
 print("1. StandardPrepareTest Data...")
 from utils.database import db_manager
 
 # AddOneBookUseAtDeleteTestBook
 delete_test_book = {
 'book_id': 'DELETE-TEST-001',
 'book_name': 'WaitDeleteTestBook',
 'auth': 'TestWorkEr',
 'category': 'Test',
 'publisher': 'TestOutputEdition',
 'publish_time': '2023-01-01',
 'num_storage': 1
 }
 
 # CleanProcessorCanEnergySaveinRecord
 db_manager.execute_update('DELETE FROM user_book WHERE BookId = ?', (delete_test_book['book_id'],))
 db_manager.execute_update('DELETE FROM book WHERE BookId = ?', (delete_test_book['book_id'],))
 
 # AddTestBook
 db_manager.execute_update('''
 INSERT INTO book 
 (BookId, BookName, Auth, Category, Publisher, PublishTime, NumStorage, NumCanBorrow, NumBookinged, CreateTime, UpdateTime) 
 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
 ''', (
 delete_test_book['book_id'], delete_test_book['book_name'], delete_test_book['auth'],
 delete_test_book['category'], delete_test_book['publisher'], delete_test_book['publish_time'],
 delete_test_book['num_storage'], delete_test_book['num_storage'], 0
 ))
 
 print(f"+ AlreadyAddTestBook: {delete_test_book['book_name']} ({delete_test_book['book_id']})")
 
 # 2. CreateDeleteTestOutputInput File
 print("\n2. CreateDeleteTestOutputInput...")
 delete_input = '''1
admin
123456

2
5
DELETE-TEST-001
y

0
0
0
'''
 
 with open('evaluation/test_3_3b_temp_input.in', 'w', encoding='utf-8') as f:
 f.write(delete_input)
 
 print("+ CreateTimeOutputInput File")
 
 # 3. ExecuteDeleteTest
 print("\n3. ExecuteDeleteTest...")
 result = subprocess.run(
 'chcp 65001 && type evaluation\\test_3_3b_temp_input.in | python src\\run.py',
 shell=True, 
 capture_output=True, 
 text=True, 
 cwd='.'
 )
 
 output = result.stdout
 print("+ TestExecuteSuccessfully")
 
 # 4. VerifyDeleteResult
 print("\n4. VerifyDeleteResult...")
 remaining_books = db_manager.execute_query(
 'SELECT COUNT(*) as count FROM book WHERE BookId = ?', 
 (delete_test_book['book_id'],)
 )
 
 remaining_count = remaining_books[0]['count'] if remaining_books else 0
 
 # AnalysisOutput
 has_confirm_prompt = "AccurateCertifiedDeleteBook" in output
 has_success_msg = "DeleteSuccess" in output or remaining_count == 0
 
 print(f"Verification Results:")
 print(f" DisplayAccurateCertifiedImproved to: {'✓' if has_confirm_prompt else '✗'}")
 print(f" BookSuccessDelete: {'✓' if remaining_count == 0 else '✗'}")
 print(f" RecordNumber: {remaining_count}")
 
 # 5. CleanProcessorTimeFile
 if os.path.exists('evaluation/test_3_3b_temp_input.in'):
 os.remove('evaluation/test_3_3b_temp_input.in')
 
 success = has_confirm_prompt and remaining_count == 0
 
 if success:
 print("\n✓ 3.3bBookDeleteFunctional TestPass")
 print(" - ManagementEnergyBookDeleteFunction")
 print(" - DisplayAccurateCertifiedImproved to") 
 print(" - AccurateCertifiedafterSuccessDeleteBookRecord")
 else:
 print("\n✗ 3.3bBookDeleteFunctional TestFailure")
 
 return success
 
 except Exception as e:
 print(f"TestAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = test_3_3b_book_delete()
 sys.exit(0 if success else 1)