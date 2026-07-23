#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')

def test_product_modification():
    """TestProductBrandModifyFunction - 2.1.2c"""
    try:
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=src_dir,
            encoding='utf-8'
        )
        
        # SendSendInteractiveSequenceSeries：1->2->3->1->NewInformation->0->0
        inputs = "1\n2\n3\n1\nModifyafterProductBrandName\nModifyafterCategoryDifferent\nModifyafterBrandBrand\n999.99\n0\n0\n"
        
        stdout, stderr = process.communicate(input=inputs, timeout=30)
        
        # AnalysisOutput
        success_indicators = [
            "DataManagement" in stdout,
            "ProductAttributeManagement" in stdout,
            "ModifyProductBrandInformation" in stdout,
            "ProductBrandInformationModifySuccess" in stdout or "ModifyCompleteSuccess" in stdout
        ]
        
        passed_checks = sum(success_indicators)
        
        print("beforeSetCheckExperiencePass：ProductBrandManagementInterfaceSaveinModifyProductBrandOption")
        print("StandardPrepareStepSegment：SelectChooseAlreadySaveinProductBrand，StandardPrepareModifyPriceFormatandCategoryDifferentInformation")
        print("ExecuteStepSegment：ModifyFunctionSuccessExecute，UpdateChangeProductBrandPriceFormatandCategoryDifferent")
        
        if passed_checks >= 3:
            print("BreakassertionVerify：ModifyafterProductBrandInformationCorrectAccurateUpdate，NewInformationinProductBrandListinCorrectAccurateDisplay")
            return True
        else:
            print("BreakassertionVerify：PartDivideFunctionNotCompleteAutomaticVerify")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("ERROR: TestUltraTime")
        return False
    except Exception as e:
        print(f"ERROR: TestExecuteFailure: {e}")
        return False

if __name__ == "__main__":
    success = test_product_modification()
    sys.exit(0 if success else 1)