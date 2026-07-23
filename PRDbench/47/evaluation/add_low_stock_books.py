#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def add_low_stock_books():
 """AddLibrarySaveNotTestBook"""
 print("=== AddLibrarySaveNotTestBook ===")
 
 try:
 from services.book_service import book_service
 
 # LibrarySaveNotTestBook
 low_stock_books = [
 {
 'book_id': 'WARNING-001',
 'book_name': 'LibrarySavewarningBook1',
 'auth': 'TestWorkEr',
 'category': 'Test',
 'publisher': 'TestOutputEdition',
 'publish_time': '2023-01-01',
 'num_storage': 1
 },
 {
 'book_id': 'WARNING-002', 
 'book_name': 'LibrarySavewarningBook2',
 'auth': 'TestWorkEr',
 'category': 'Test',
 'publisher': 'TestOutputEdition',
 'publish_time': '2023-01-01',
 'num_storage': 2
 }
 ]
 
 print("StartingAddLibrarySaveNotBook...")
 
 for book_info in low_stock_books:
 # DeleteCanEnergySaveinSameNameBook
 try:
 book_service.delete_book(book_info['book_id'])
 print(f"- DeleteAlreadySavein {book_info['book_id']}")
 except:
 pass
 
 # AddNewBook
 success, result = book_service.add_book(
 book_name=book_info['book_name'],
 book_id=book_info['book_id'],
 auth=book_info['auth'],
 category=book_info['category'],
 publisher=book_info['publisher'],
 publish_time=book_info['publish_time'],
 num_storage=book_info['num_storage']
 )
 
 if success:
 print(f"+ SuccessAdd: {book_info['book_name']} (LibrarySave: {book_info['num_storage']})")
 else:
 print(f"- AddFailure: {book_info['book_name']} - {result}")
 
 # VerifyAddResult
 print("\nVerifyLibrarySavewarningBook:")
 low_stock_list = book_service.get_low_stock_books(threshold=3)
 
 if low_stock_list:
 print(f"SendImplementation {len(low_stock_list)} BookLibrarySaveNotBook:")
 for book in low_stock_list:
 print(f" - {book['BookName']}: LibrarySave {book['NumStorage']} Book")
 else:
 print("NotSendImplementationLibrarySaveNotBook")
 
 print("\nLibrarySaveNotTestBookAddSuccessfully!")
 return True
 
 except Exception as e:
 print(f"AddBookAbnormal: {e}")
 import traceback
 traceback.print_exc()
 return False

if __name__ == "__main__":
 success = add_low_stock_books()
 sys.exit(0 if success else 1)