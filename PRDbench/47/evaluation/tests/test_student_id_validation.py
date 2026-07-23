# -*- coding: utf-8 -*-
"""OpticsFormatStyleVerifyTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.validators import validator

def test_student_id_validation():
 """TestOpticsFormatStyleVerifyFunction"""
 
 # TestEmptyString
 valid, error = validator.validate_student_id("")
 assert not valid, "EmptyStringShouldThisVerifyFailure"
 assert "NotEnergyasEmpty" in error
 
 # TestUltraLengthString（21CharacterSymbol）
 valid, error = validator.validate_student_id("a" * 21)
 assert not valid, "UltraLengthOpticsShouldThisVerifyFailure"
 assert "LengthRepublic" in error
 
 # TestSpecialCharacterSymbol
 valid, error = validator.validate_student_id("test@#$")
 assert not valid, "ContainsSpecialCharacterSymbolShouldThisVerifyFailure"
 assert "CharacterandNumber" in error
 
 print("Test Passed：OpticsFormatStyleVerifyFunctionNormal")
 return True

if __name__ == "__main__":
 try:
 test_student_id_validation()
 print("[PASS] Test Passed：OpticsFormatStyleVerifyFunctionNormal")
 except Exception as e:
 print(f"[FAIL] Test Failed：{e}")
 sys.exit(1)
