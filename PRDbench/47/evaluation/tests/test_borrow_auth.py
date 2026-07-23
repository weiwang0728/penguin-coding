# -*- coding: utf-8 -*-
"""BorrowingVerifyCheckTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from services.borrow_service import borrow_service
from services.auth_service import auth_service

def test_borrow_authentication_check():
 """TestBorrowingVerifyCheckFunction"""
 auth_service.logout()
 
 try:
 success, result = borrow_service.borrow_book("TESTUSER", "TESTBOOK001")
 assert not success, "NotloginUserShouldThisBorrowing"
 assert "login" in result or "" in result, f"ShouldImproved toVerifyError: {result}"
 
 print("Test Passed：CorrectAccurateNotloginUserBorrowing")
 except Exception as e:
 pytest.fail(f"Test Failed: {str(e)}")
