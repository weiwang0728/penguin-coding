#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ModifyRecoveryTestDesignPlanintest_commandandtest_inputWeightRecoveryIssue
Whentest_commandinAlreadyEconomyContainsOutputInputSequenceSeriesTime，ShouldThisCleanEmptytest_input
"""

import json
import re

def load_test_plan():
    """LoadTestDesignPlan"""
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_test_plan(tests):
    """SaveTestDesignPlan"""
    with open('detailed_test_plan.json', 'w', encoding='utf-8') as f:
        json.dump(tests, f, ensure_ascii=False, indent=4)

def extract_input_from_command(command):
    """fromCommandinExtractGetOutputInputSequenceSeries"""
    # HorseMatch echo -e "OutputInputSequenceSeries"
    match = re.search(r'echo -e "([^"]+)"', command)
    if match:
        return match.group(1)
    return None

def fix_duplicate_inputs():
    """ModifyRecoveryWeightRecoveryOutputInputIssue"""
    tests = load_test_plan()
    
    file_comparison_tests = []
    fixed_count = 0
    
    for test in tests:
        if test.get('type') == 'file_comparison':
            file_comparison_tests.append(test)
    
    print(f"Found {len(file_comparison_tests)} item(s)file_comparisonTest")
    print("\nCheckWeightRecoveryOutputInputIssue：")
    print("="*80)
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        testcase = test['testcases'][0]
        test_command = testcase.get('test_command', '')
        test_input = testcase.get('test_input', '')
        
        print(f"\n{i}. {metric}")
        print(f"   Command: {test_command}")
        print(f"   OutputInput: {test_input}")
        
        # fromCommandinExtractGetOutputInputSequenceSeries
        command_input = extract_input_from_command(test_command)
        
        if command_input and test_input:
            # CheckYesNoWeightRecovery
            if command_input == test_input:
                print(f"   [SendImplementationWeightRecovery] CommandinOutputInputandtest_inputCameraSame")
                print(f"   [ModifyRecovery] CleanEmptytest_input")
                
                # ModifyRecovery：CleanEmptytest_input
                for test_item in tests:
                    if test_item.get('metric') == metric:
                        test_item['testcases'][0]['test_input'] = None
                        fixed_count += 1
                        break
            elif command_input:
                print(f"   [Check] CommandOutputInput: {command_input}")
                print(f"   [Check] test_input: {test_input}")
                print(f"   [Status] OutputInputNotSame，NeedHandAutoCheck")
        elif command_input and not test_input:
            print(f"   [Normal] OnlyHasCommandinHasOutputInput")
        elif not command_input and test_input:
            print(f"   [Normal] OnlyHastest_inputHasOutputInput")
        else:
            print(f"   [Normal] AllNotHasOutputInput")
    
    print(f"\n{'='*80}")
    print(f"ModifyRecoveryCompleteSuccess！TotalModifyRecovery {fixed_count} item(s)WeightRecoveryOutputInputIssue")
    
    if fixed_count > 0:
        save_test_plan(tests)
        print("AlreadySaveModifyRecoveryafterTestDesignPlan")
    
    return fixed_count

def verify_fixes():
    """VerifyModifyRecoveryResult"""
    tests = load_test_plan()
    
    print(f"\n{'='*80}")
    print("VerifyModifyRecoveryResult：")
    print('='*80)
    
    file_comparison_tests = [test for test in tests if test.get('type') == 'file_comparison']
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        testcase = test['testcases'][0]
        test_command = testcase.get('test_command', '')
        test_input = testcase.get('test_input')
        
        command_input = extract_input_from_command(test_command)
        
        print(f"\n{i}. {metric}")
        
        if command_input and test_input:
            if command_input == test_input:
                print(f"   [Warning] StillSaveinWeightRecoveryOutputInput！")
            else:
                print(f"   [Normal] OutputInputNotWeightRecovery")
        elif command_input and not test_input:
            print(f"   [Normal] OnlyHasCommandOutputInput")
        elif not command_input and test_input:
            print(f"   [Normal] OnlyHastest_input")
        else:
            print(f"   [Normal] NoOutputInput")

def main():
    """MainFunctionNumber"""
    print("File Comparison Test CaseWeightRecoveryOutputInputModifyRecoveryTool")
    print("="*80)
    
    # ModifyRecoveryWeightRecoveryOutputInput
    fixed_count = fix_duplicate_inputs()
    
    # VerifyModifyRecoveryResult
    verify_fixes()
    
    print(f"\n{'='*80}")
    print("ModifyRecoverySummary:")
    print(f"- TotalModifyRecovery {fixed_count} item(s)WeightRecoveryOutputInputIssue")
    print("- PlaceHasfile_comparisonTest CaseAlreadyCheckCompleteComplete")
    
    return fixed_count > 0

if __name__ == "__main__":
    main()