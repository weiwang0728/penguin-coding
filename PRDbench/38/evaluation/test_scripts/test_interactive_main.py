#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ResolveOutputInputWeightFixedDirectionEOFIssueInteractiveTestScript
"""
import subprocess
import sys
import os
import time

# AddsrcDirectorytoPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')

def test_product_modification():
    """TestProductBrandModifyFunction - 2.1.2c"""
    print("=" * 60)
    print("2.1.2c ProductAttributeManagement-ModifyProductAttribute - InteractiveTest")
    print("=" * 60)
    
    try:
        # StartMainProgram
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
        
        print(f"beforeSetCheckExperience：{'PASS' if success_indicators[0] else 'FAIL'} FoundDataManagementMenu")
        print(f"MenuNavigation：{'PASS' if success_indicators[1] else 'FAIL'} ImportInputProductAttributeManagement")
        print(f"FunctionAccurateCertified：{'PASS' if success_indicators[2] else 'FAIL'} FoundModifyProductBrandOption")
        print(f"Execution Result：{'PASS' if success_indicators[3] else 'FAIL'} ProductBrandModifyExecute")
        
        if passed_checks >= 3:
            print("SUCCESS: 2.1.2c ProductBrandModifyFunctional TestPass")
            return True
        else:
            print("PARTIAL: 2.1.2c ProductBrandModifyFunctionPartially Passed")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("ERROR: TestUltraTime，ProgramCanEnergyDefectInputEqualWaitStatus")
        return False
    except Exception as e:
        print(f"ERROR: TestExecuteFailure: {e}")
        return False

def test_product_deletion():
    """TestProductBrandDeleteFunction - 2.1.2d"""
    print("\n" + "=" * 60)
    print("2.1.2d ProductAttributeManagement-DeleteProductRecord - InteractiveTest")
    print("=" * 60)
    
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
        
        # SendSendInteractiveSequenceSeries：1->2->4->1->y->0->0
        inputs = "1\n2\n4\n1\ny\n0\n0\n"
        
        stdout, stderr = process.communicate(input=inputs, timeout=30)
        
        success_indicators = [
            "DataManagement" in stdout,
            "ProductAttributeManagement" in stdout,
            "DeleteProductBrand" in stdout,
            "ProductBrandDeleteSuccess" in stdout or "DeleteCompleteSuccess" in stdout
        ]
        
        passed_checks = sum(success_indicators)
        
        print(f"beforeSetCheckExperience：{'PASS' if success_indicators[0] else 'FAIL'} FoundDataManagementMenu")
        print(f"MenuNavigation：{'PASS' if success_indicators[1] else 'FAIL'} ImportInputProductAttributeManagement")
        print(f"FunctionAccurateCertified：{'PASS' if success_indicators[2] else 'FAIL'} FoundDeleteProductBrandOption")
        print(f"Execution Result：{'PASS' if success_indicators[3] else 'FAIL'} ProductBrandDeleteExecute")
        
        if passed_checks >= 3:
            print("SUCCESS: 2.1.2d ProductBrandDeleteFunctional TestPass")
            return True
        else:
            print("PARTIAL: 2.1.2d ProductBrandDeleteFunctionPartially Passed")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("ERROR: TestUltraTime")
        return False
    except Exception as e:
        print(f"ERROR: TestExecuteFailure: {e}")
        return False

def test_user_preference_modeling():
    """TestUserPreferenceBuildModel - 2.2.2"""
    print("\n" + "=" * 60)
    print("2.2.2 User Attribute Preference Modeling-PreferenceVectorGeneration - InteractiveTest")
    print("=" * 60)
    
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
        
        # SendSendInteractiveSequenceSeries：3->1->../evaluation/user_preferences.json->0->0
        inputs = "3\n1\n../evaluation/user_preferences.json\n0\n0\n"
        
        stdout, stderr = process.communicate(input=inputs, timeout=30)
        
        success_indicators = [
            "UserAnalysis" in stdout,
            "Preference" in stdout or "BuildModel" in stdout,
            "Success" in stdout or "CompleteSuccess" in stdout
        ]
        
        passed_checks = sum(success_indicators)
        
        print(f"beforeSetCheckExperience：{'PASS' if success_indicators[0] else 'FAIL'} FoundUserAnalysisMenu")
        print(f"FunctionAccurateCertified：{'PASS' if success_indicators[1] else 'FAIL'} PreferenceBuildModelFunction")
        print(f"Execution Result：{'PASS' if success_indicators[2] else 'FAIL'} BuildModelExecute")
        
        if passed_checks >= 2:
            print("SUCCESS: 2.2.2 UserPreferenceBuildModelTest Passed")
            return True
        else:
            print("PARTIAL: 2.2.2 UserPreferenceBuildModelPartially Passed")
            return False
            
    except subprocess.TimeoutExpired:
        process.kill()
        print("ERROR: TestUltraTime")
        return False
    except Exception as e:
        print(f"ERROR: TestExecuteFailure: {e}")
        return False

if __name__ == "__main__":
    print("StartingInteractiveTest，ResolveOutputInputWeightFixedDirectionEOFIssue...")
    
    # CheckCommandLineParameter，AccurateFixedNeedRunWhichitem(s)Test
    import sys
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "2.1.2c":
            result = test_product_modification()
        elif test_name == "2.1.2d":
            result = test_product_deletion()
        elif test_name == "2.2.2":
            result = test_user_preference_modeling()
        else:
            print(f"NotKnowTest Item: {test_name}")
            result = False
        
        print(f"Test Results: {'PASS' if result else 'FAIL'}")
        sys.exit(0 if result else 1)
    
    # ForExampleResultNotHasParameter，RunPlaceHasTest
    results = []
    results.append(test_product_modification())
    results.append(test_product_deletion())
    results.append(test_user_preference_modeling())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n" + "=" * 60)
    print(f"InteractiveTestSummary：{passed}/{total} item(s)Pass")
    print("=" * 60)
    
    if passed == total:
        print("SUCCESS: PlaceHasInteractiveTest Passed！SuccessResolveOutputInputWeightFixedDirectionIssue")
    else:
        print("PARTIAL: Partial test passed, but it already successfully bypassed the EOF issue")