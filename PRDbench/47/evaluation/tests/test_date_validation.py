# -*- coding: utf-8 -*-
"""dayPeriodFormatStyleVerifyTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from utils.validators import validator

def test_date_format_validation():
 """TestdayPeriodFormatStyleVerifyFunction"""
 
 # TestNoEffectFormatStyle1
 valid, error = validator.validate_date("2023/13/01")
 assert not valid, "NoEffectdayPeriodFormatStyleShouldThisVerifyFailure"
 assert "FormatStyle" in error
 
 # TestNoEffectFormatStyle2
 valid, error = validator.validate_date("2023-02-30")
 assert not valid, "NotSaveindayPeriodShouldThisVerifyFailure"
 assert "FormatStyle" in error
 
 # TestNoEffectFormatStyle3
 valid, error = validator.validate_date("abcd-ef-gh")
 assert not valid, "CharacterdayPeriodShouldThisVerifyFailure"
 assert "FormatStyle" in error
 
 print("Test Passed：dayPeriodFormatStyleVerifyFunctionNormal")
 return True
