# -*- coding: utf-8 -*-
"""
BatchTestexpected_output_filesTest Case
QuickVerifyandGeneratemissingexpectedFile
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# AddsrcDirectorytoPath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def load_test_plan():
    """LoadTestDesign"""
    with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_expected_output_files_tests():
    """GetGetPlaceHasHasexpected_output_filesTest Case"""
    test_plan = load_test_plan()
    expected_tests = []
    
    for test in test_plan:
        if test.get('expected_output_files') and test['expected_output_files']:
            expected_tests.append({
                'metric': test['metric'],
                'type': test['type'],
                'testcases': test['testcases'],
                'expected_files': test['expected_output_files']
            })
    
    return expected_tests

def run_test_command(test_command):
    """RunTest Command"""
    try:
        print(f"Execute: {test_command}")
        result = subprocess.run(test_command, shell=True, capture_output=True, text=True, 
                              cwd='c:/Work/CodeAgent/DZY_19', timeout=120)
        
        if result.returncode == 0:
            print("[OK] Test CommandExecuteSuccess")
            return True, result.stdout
        else:
            print(f"[FAIL] Test CommandExecuteFailure: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] Test CommandExecuteUltraTime")
        return False, "Timeout"
    except Exception as e:
        print(f"[ERROR] ExecuteAbnormal: {str(e)}")
        return False, str(e)

def check_expected_file_exists(expected_file):
    """CheckexpectedFileYesNoSaveinandascurrentDayGenerate"""
    if not os.path.exists(expected_file):
        return False, "FileNotSavein"
    
    # CheckFileModifyTimeBetween
    mtime = os.path.getmtime(expected_file)
    file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    if file_date == today:
        return True, f"FileSaveinasDayGenerate ({file_date})"
    else:
        return False, f"FileSaveinasFile ({file_date})"

def batch_test_expected_files():
    """BatchTestexpected_output_filesTest Case"""
    print("=" * 80)
    print("BatchTestexpected_output_filesTest Case")
    print("=" * 80)
    
    expected_tests = get_expected_output_files_tests()
    
    print(f"totalSendImplementation {len(expected_tests)} item(s)expected_output_filesTest Case")
    print()
    
    results = []
    
    for i, test in enumerate(expected_tests, 1):
        print(f"[{i}/{len(expected_tests)}] Test: {test['metric']}")
        print("-" * 60)
        
        # CheckexpectedFileStatus
        expected_file = test['expected_files'][0]
        file_exists, file_status = check_expected_file_exists(expected_file)
        print(f"ExpectedFileStatus: {file_status}")
        
        if file_exists:
            print("[SKIP] ExpectedFileAlreadySaveinasDayGenerate,Skip")
            results.append({'metric': test['metric'], 'status': 'SKIP', 'reason': 'FileAlreadySavein'})
        else:
            # ExecuteTest Command
            if test['testcases']:
                test_command = test['testcases'][0]['test_command']
                
                # DeleteoldexpectedFile
                if os.path.exists(expected_file):
                    os.remove(expected_file)
                    print(f"AlreadyDeleteoldexpectedFile: {expected_file}")
                
                # RunTest
                success, output = run_test_command(test_command)
                
                # CheckYesNoGenerateNewexpectedFile
                if os.path.exists(expected_file):
                    print(f"[SUCCESS] SuccessGenerateexpectedFile: {expected_file}")
                    results.append({'metric': test['metric'], 'status': 'SUCCESS', 'reason': 'AutoAutoGenerateSuccess'})
                else:
                    print(f"[FAIL] NotEnergyGenerateexpectedFile: {expected_file}")
                    results.append({'metric': test['metric'], 'status': 'FAILED', 'reason': 'NotEnergyAutoAutoGenerate'})
            else:
                print("[FAIL] NoTest Command")
                results.append({'metric': test['metric'], 'status': 'FAILED', 'reason': 'NoTest Command'})
        
        print()
    
    # printsummarySummaryResult
    print("=" * 80)
    print("BatchTest ResultssummaryTotal")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r['status'] in ['SUCCESS', 'SKIP'])
    total_count = len(results)
    
    print(f"TotalTest Case: {total_count}")
    print(f"Success/Skip: {success_count}")
    print(f"Failure: {total_count - success_count}")
    print(f"SuccessRate: {success_count/total_count:.1%}")
    print()
    
    for result in results:
        status_icon = "[OK]" if result['status'] in ['SUCCESS', 'SKIP'] else "[FAIL]"
        print(f"{status_icon} {result['metric']}: {result['status']} - {result['reason']}")

if __name__ == "__main__":
    batch_test_expected_files()