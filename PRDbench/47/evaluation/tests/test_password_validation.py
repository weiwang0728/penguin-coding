# -*- coding: utf-8 -*-
"""MiCodeStrongRepublicVerifyTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.validators import validator

def test_password_strength_validation():
    """TestMiCodeStrongRepublicVerifyFunction"""
    
    # TestEmptyMiCode
    valid, error = validator.validate_password("")
    assert not valid, "EmptyMiCodeShouldThisVerifyFailure"
    assert "NotEnergyasEmpty" in error
    
    # TestshortMiCode（5CharacterSymbol）
    valid, error = validator.validate_password("12345")
    assert not valid, "shortMiCodeShouldThisVerifyFailure"
    assert "LengthRepublic" in error
    
    # TestUltraLengthMiCode（33CharacterSymbol）
    valid, error = validator.validate_password("a" * 33)
    assert not valid, "UltraLengthMiCodeShouldThisVerifyFailure"
    assert "LengthRepublic" in error
    
    print("Test Passed：MiCodeStrongRepublicVerifyFunctionNormal")
    return True
