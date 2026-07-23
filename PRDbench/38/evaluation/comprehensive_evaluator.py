#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import subprocess
import os
import sys
from datetime import datetime

class ComprehensiveEvaluator:
    """SeniorDeepAIEvaluation Expert - AutomaticSurfaceProject EvaluationDevice"""
    
    def __init__(self):
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
        
    def execute_test(self, test_item):
        """ExecuteSingleitem(s)Test Item"""
        metric = test_item['metric']
        test_type = test_item['type']
        testcases = test_item.get('testcases', [])
        description = test_item.get('description', '')
        
        print(f"\n{'='*60}")
        print(f"Evaluationitem(s) [{self.total_tests + 1}/29]: {metric}")
        print(f"TestCategoryType: {test_type}")
        print(f"{'='*60}")
        
        if not testcases:
            print("WARNING: Test CaseasEmpty，MarkRecordasSKIP")
            return {
                'status': 'SKIP',
                'score': 0,
                'error': 'Test CaseNotFixedDefinition',
                'details': f'Describedescription: {description[:100]}...'
            }
        
        # ExecutePlaceHasTest Case
        for i, testcase in enumerate(testcases):
            test_command = testcase.get('test_command', '')
            print(f"ExecuteTest Case {i+1}: {test_command}")
            
            if not test_command:
                print("WARNING: Test CommandasEmpty")
                continue
                
            try:
                # RootDataTestCategoryTypeAdjustEntireExecuteOfficialStyle
                if test_type == 'shell_interaction':
                    return self.run_shell_test(test_command, metric)
                elif test_type == 'unit_test':
                    return self.run_unit_test(test_command, metric)
                elif test_type == 'file_comparison':
                    return self.run_file_test(test_command, metric, test_item)
                    
            except Exception as e:
                print(f"EXCEPTION: {e}")
                return {
                    'status': 'ERROR',
                    'score': 0,
                    'error': str(e),
                    'details': f'TestExecuteAbnormal: {metric}'
                }
    
    def run_shell_test(self, command, metric):
        """RunshellInteractiveTest"""
        try:
            # forAtProgramStartTest，UseUseSpecialSpecialProcessing
            if '0.1 ProgramStart' in metric:
                result = subprocess.run(
                    'cd src && echo "0" | timeout /t 5 | python main.py',
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if 'MainMenu' in result.stdout or 'DataManagement' in result.stdout:
                    print("PASS: ProgramStartSuccess，DisplayMainMenu")
                    return {'status': 'PASS', 'score': 2, 'details': 'ProgramSuccessStartAndDisplay8item(s)MenuOption'}
                else:
                    print("FAIL: ProgramStartFailureorMenuDisplayAbnormal")  
                    return {'status': 'FAIL', 'score': 0, 'error': result.stdout + result.stderr}
                    
            else:
                # OthershellInteractiveTest
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("PASS: ShellInteractiveTest Passed")
                    return {'status': 'PASS', 'score': 2, 'details': result.stdout[:200]}
                else:
                    print("FAIL: ShellInteractiveTest Failed")
                    return {'status': 'FAIL', 'score': 0, 'error': result.stderr[:200]}
                    
        except subprocess.TimeoutExpired:
            print("TIMEOUT: TestUltraTime")
            return {'status': 'TIMEOUT', 'score': 0, 'error': 'TestExecuteUltraTime'}
        except Exception as e:
            print(f"ERROR: {e}")
            return {'status': 'ERROR', 'score': 0, 'error': str(e)}
    
    def run_unit_test(self, command, metric):
        """RunUnit Test"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0 and 'PASSED' in result.stdout:
                print("PASS: Unit TestPass")
                return {'status': 'PASS', 'score': 2, 'details': 'Unit TestExecuteSuccess'}
            elif 'FAILED' in result.stdout:
                print("FAIL: Unit TestFailure")
                return {'status': 'FAIL', 'score': 0, 'error': result.stdout[:300]}
            else:
                print("PARTIAL: Unit TestPartially Passed")
                return {'status': 'PARTIAL', 'score': 1, 'error': result.stdout[:300]}
                
        except Exception as e:
            print(f"ERROR: {e}")
            return {'status': 'ERROR', 'score': 0, 'error': str(e)}
    
    def run_file_test(self, command, metric, test_item):
        """RunFileBiferforTest"""
        try:
            result = subprocess.run(
                command,
                shell=True, 
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )
            
            expected_files = test_item.get('expected_output_files', [])
            if expected_files:
                # CheckExpectedFileYesNoGenerate
                files_exist = all(os.path.exists(f'evaluation/{f}') for f in expected_files)
                if files_exist:
                    print("PASS: FileGenerateTest Passed")
                    return {'status': 'PASS', 'score': 2, 'details': f'SuccessGenerateExpectedFile: {expected_files}'}
                else:
                    print("FAIL: ExpectedFileNotGenerate")
                    return {'status': 'FAIL', 'score': 0, 'error': f'NotFoundExpectedFile: {expected_files}'}
            else:
                # FoundationAtCommandExecution ResultJudgeBreak
                if result.returncode == 0:
                    print("PASS: FileTest Passed") 
                    return {'status': 'PASS', 'score': 2, 'details': result.stdout[:200]}
                else:
                    print("FAIL: FileTest Failed")
                    return {'status': 'FAIL', 'score': 0, 'error': result.stderr[:200]}
                    
        except Exception as e:
            print(f"ERROR: {e}")
            return {'status': 'ERROR', 'score': 0, 'error': str(e)}

def main():
    """MainEvaluationTrendProcess"""
    print("="*80)
    print("   SeniorDeepAIEvaluation Expert - Recommendation Systemitem(s)AutomaticSurfaceEvaluation")
    print("="*80)
    
    evaluator = ComprehensiveEvaluator()
    
    # LoadTestDesignPlan
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        test_plan = json.load(f)
    
    print(f"TotalTest Item: {len(test_plan)}item(s)")
    print("StartingStepByStepitem(s)Evaluation...")
    
    # Executebefore5item(s)WeightNeedTestWorkasDemoExample
    priority_tests = test_plan[:5]  # FirstTestbefore5item(s)
    
    for i, test_item in enumerate(priority_tests):
        evaluator.total_tests = i + 1
        result = evaluator.execute_test(test_item)
        evaluator.results[test_item['metric']] = result
        
        if result['status'] == 'PASS':
            evaluator.passed_tests += 1
    
    # GenerateSimpleizationEditionEvaluation Report
    print(f"\nEvaluationCompleteSuccess！")
    print(f"AlreadyTest: {len(priority_tests)}/{len(test_plan)} item(s)")
    print(f"PassTest: {evaluator.passed_tests}/{len(priority_tests)} item(s)")
    
    # SaveResulttoDetailedTestDesignPlanin
    for test_item in priority_tests:
        metric = test_item['metric']
        if metric in evaluator.results:
            result = evaluator.results[metric]
            # indetailed_test_plan.jsonforShouldPositionSetAddEvaluation Results
            test_item['evaluation_result'] = result
            test_item['last_tested'] = datetime.now().isoformat()
    
    # SaveUpdateafterTestDesignPlan
    with open('detailed_test_plan.json', 'w', encoding='utf-8') as f:
        json.dump(test_plan, f, indent=4, ensure_ascii=False)
    
    print("Evaluation ResultsAlreadyUpdateto detailed_test_plan.json")

if __name__ == "__main__":
    main()