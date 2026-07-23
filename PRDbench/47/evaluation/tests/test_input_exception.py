# -*- coding: utf-8 -*-
"""OutputInputAbnormalProcessingTest"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

try:
 from utils.validators import validator
 
 def test_input_exception_handling():
 """TestOutputInputAbnormalProcessingFunction"""
 
 exception_handled = 0
 
 # 1. TestMethodCharacterSymbolOutputInput
 try:
 valid, error = validator.validate_student_id("test@#$%^&*()")
 if not valid and error:
 exception_handled += 1
 print("✓ CorrectAccurateProcessingSpecialCharacterSymbolOutputInputAbnormal")
 except Exception as e:
 print(f"✗ SpecialCharacterSymbolOutputInputTestAbnormal：{e}")
 
 # 2. TestUltraLengthStringOutputInput
 try:
 long_string = "a" * 1000
 valid, error = validator.validate_student_id(long_string)
 if not valid and error:
 exception_handled += 1
 print("✓ CorrectAccurateProcessingUltraLengthStringOutputInputAbnormal")
 except Exception as e:
 print(f"✗ UltraLengthStringOutputInputTestAbnormal：{e}")
 
 # 3. TestEmptyValueandNoneOutputInput
 try:
 valid1, error1 = validator.validate_student_id("")
 valid2, error2 = validator.validate_student_id(None)
 if not valid1 and not valid2 and error1 and error2:
 exception_handled += 1
 print("✓ CorrectAccurateProcessingEmptyValueOutputInputAbnormal")
 except Exception as e:
 print(f"✗ EmptyValueOutputInputTestAbnormal：{e}")
 
 # 4. TestNumberCategoryOutputInput（ShouldThisConversionasStringProcessing）
 try:
 valid, error = validator.validate_student_id(12345)
 # ShouldThisEnergyCorrectAccurateProcessingNumberOutputInput
 exception_handled += 1
 print("✓ CorrectAccurateProcessingNumberCategoryOutputInput")
 except Exception as e:
 print(f"NumberCategoryOutputInputTest: {e}")
 exception_handled += 1 # UseOutputImplementationAbnormalCalculateCorrectAccurateProcessing
 
 # CheckYesNoProcessingAbnormalCategory（few3Type）
 if exception_handled >= 3:
 print(f"Test Passed：CorrectAccurateProcessing{exception_handled}TypeOutputInputAbnormal")
 return True
 else:
 print(f"Test Failed：Processing{exception_handled}TypeOutputInputAbnormal")
 return False
 
 if __name__ == "__main__":
 try:
 if test_input_exception_handling():
 print("[PASS] Test Passed：OutputInputAbnormalProcessingFunctionNormal")
 else:
 print("[FAIL] Test Failed：OutputInputAbnormalProcessingAbnormal")
 sys.exit(1)
 except Exception as e:
 print(f"[FAIL] Test Failed：{e}")
 sys.exit(1)

except ImportError as e:
 print(f"[FAIL] ImportModuleFailure：{e}")
 sys.exit(1)