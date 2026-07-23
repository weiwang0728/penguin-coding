#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DirectInterfaceTestRelatedKeyfile_comparisonUseExample
VerifyofbeforeModifyRecoveryYesNoHasEffect
"""

import sys
import os
import subprocess
import tempfile

def test_single_case(case_name, inputs, description):
    """TestSingleitem(s)UseExample"""
    print(f"\n{'='*60}")
    print(f"Test: {case_name}")
    print(f"Describedescription: {description}")
    print(f"OutputInputSequenceSeries: {inputs}")
    print('='*60)
    
    # WillOutputInputConversionasImplementationInternationalChangeLineSymbol
    input_text = inputs.replace('\\n', '\n')
    
    try:
        # UseUsesubprocessDirectInterfaceExecute
        result = subprocess.run(
            ['python', 'main.py'],
            input=input_text,
            text=True,
            capture_output=True,
            cwd='../src',
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        print(f"ExitCode: {result.returncode}")
        
        # CheckRelatedKeyIndicatorMark
        output = result.stdout + result.stderr
        
        has_invalid_choice = "NoEffectSelectChoose" in output
        has_normal_exit = "InfectionThanksUseUseRecommendation System" in output
        has_menu_display = "MainMenu" in output
        has_algorithm_menu = "CalculateMethodEvaluation" in output
        
        print(f"ContainsMenuDisplay: {'Yes' if has_menu_display else 'No'}")
        print(f"ContainsCalculateMethodEvaluationMenu: {'Yes' if has_algorithm_menu else 'No'}")
        print(f"YesNoHasNoEffectSelectChooseError: {'Yes' if has_invalid_choice else 'No'}")
        print(f"ProgramNormalExit: {'Yes' if has_normal_exit else 'No'}")
        
        # DisplayPartDivideOutput
        if len(output) > 0:
            preview = output[:500] + ("..." if len(output) > 500 else "")
            print(f"\nOutputPreview:\n{preview}")
        
        # JudgeBreakTest Results
        if has_invalid_choice:
            result_status = "Failure - StillHasNoEffectSelectChooseError"
            return False
        elif has_normal_exit:
            result_status = "Success - ProgramNormalCompleteSuccess"
            return True
        else:
            result_status = "Warning - ProgramNotNormalResultBundle"
            return False
        
    except subprocess.TimeoutExpired:
        result_status = "Failure - TestUltraTime"
        return False
    except Exception as e:
        result_status = f"Failure - ExecuteError: {e}"
        return False
    
    finally:
        print(f"\nResult: {result_status}")

def main():
    """MainTestFunctionNumber"""
    print("File Comparison RelatedKeyUseExampleDirectInterfaceTest")
    print("="*80)
    
    # NeedTestRelatedKeyUseExample
    test_cases = [
        {
            'name': '2.3.4 SparseMatrixProcessing',
            'inputs': '5\\n4\\n0\\n0',
            'description': 'CalculateMethodEvaluation -> RunCalculateMethodBiferCompare -> AttributeEffectUseRecommendation -> ReturnReturn -> Exit'
        },
        {
            'name': '2.5.2 ChartTableGenerate',
            'inputs': '5\\n5\\n1\\n0\\n0',
            'description': 'CalculateMethodEvaluation -> RunCalculateMethodBiferCompare -> AutomaticPartCalculateMethod -> ReturnReturn -> Exit'
        },
        {
            'name': '2.5.3 DecisionRecoveryComplexityRepublic',
            'inputs': '2\\n1\\n1\\n1\\n5\\ny\\n0\\n0',
            'description': 'RecommendationFunction -> asUserGenerateRecommendation -> UserID=1 -> CalculateMethod=1 -> RecommendationNumber=5 -> AccurateCertified -> ReturnReturn -> Exit'
        },
        {
            'name': '2.6.2 PermissionManagement',
            'inputs': '7\\n3\\n1\\n0\\n0',
            'description': 'SystemManagement -> ViewLog -> SelectChooseSystemLog -> ReturnReturn -> Exit'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        success = test_single_case(
            test_case['name'],
            test_case['inputs'], 
            test_case['description']
        )
        results.append((test_case['name'], success))
    
    # entriesSummaryResult
    print(f"\n{'='*80}")
    print("Test ResultsentriesTotal")
    print('='*80)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    for name, success in results:
        status = "[Pass]" if success else "[Failure]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {total} item(s)Test")
    print(f"Pass: {passed} item(s)")
    print(f"Failure: {failed} item(s)")
    print(f"SuccessRate: {passed/total*100:.1f}%")
    
    if failed == 0:
        print("\nPlaceHasRelatedKeyUseExampleTest Passed！ModifyRecoverySuccess！")
        return True
    else:
        print(f"\nStillHas {failed} item(s)UseExampleFailure，NeedImportOneStepAdjustTry。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)