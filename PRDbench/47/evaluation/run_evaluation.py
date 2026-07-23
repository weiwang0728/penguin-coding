#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutomatedAssessmentScript - ExecuteExistingTestGenerateEvaluation Report
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, timeout=30):
 """ExecuteCommandReturnReturnResult"""
 try:
 result = subprocess.run(
 command, 
 shell=True, 
 capture_output=True, 
 text=True, 
 timeout=timeout,
 encoding='utf-8',
 errors='ignore'
 )
 return {
 'success': result.returncode == 0,
 'returncode': result.returncode,
 'stdout': result.stdout,
 'stderr': result.stderr
 }
 except subprocess.TimeoutExpired:
 return {
 'success': False,
 'returncode': -1,
 'stdout': '',
 'stderr': 'Command timed out'
 }
 except Exception as e:
 return {
 'success': False,
 'returncode': -2,
 'stdout': '',
 'stderr': str(e)
 }

def load_test_plan():
 """LoadTestDesign"""
 with open('evaluation/detailed_test_plan.json', 'r', encoding='utf-8') as f:
 return json.load(f)

def execute_tests():
 """ExecuteExistingTest"""
 test_plan = load_test_plan()
 results = []
 
 print("StartingExecuteLibrary Management SystemAssessment...")
 print("=" * 60)
 
 for i, test_case in enumerate(test_plan, 1):
 metric = test_case['metric']
 test_type = test_case['type']
 description = test_case['description']
 expected_output = test_case['expected_output']
 testcases = test_case.get('testcases', [])
 
 print(f"\n[{i}/42] ExecuteTest: {metric}")
 print(f"TestCategory: {test_type}")
 
 if not testcases:
 result = {
 'metric': metric,
 'type': test_type,
 'status': 'SKIP',
 'score': 0,
 'max_score': 2,
 'message': 'Test CaseNotImplementationImplementation',
 'details': description
 }
 else:
 # ExecuteTest
 test_result = None
 for testcase in testcases:
 command = testcase.get('test_command')
 if command:
 print(f"ExecuteCommand: {command}")
 test_result = run_command(command)
 break
 
 if test_result is None:
 result = {
 'metric': metric,
 'type': test_type,
 'status': 'SKIP',
 'score': 0,
 'max_score': 2,
 'message': 'NoHasEffectTest Command',
 'details': description
 }
 else:
 # AnalysisTest Results
 if test_result['success']:
 if '[PASS]' in test_result['stdout'] or 'Test Passed' in test_result['stdout']:
 status = 'PASS'
 score = 2
 message = 'Test Passed'
 else:
 status = 'PARTIAL'
 score = 1
 message = 'Partially PassedorResultNotAccurate'
 else:
 status = 'FAIL'
 score = 0
 message = f"Test Failed: {test_result['stderr'][:200]}"
 
 result = {
 'metric': metric,
 'type': test_type,
 'status': status,
 'score': score,
 'max_score': 2,
 'message': message,
 'details': {
 'command': command,
 'stdout': test_result['stdout'][:500],
 'stderr': test_result['stderr'][:500],
 'returncode': test_result['returncode']
 }
 }
 
 results.append(result)
 print(f"Result: {result['status']} ({result['score']}/{result['max_score']})")
 
 return results

def generate_report(results):
 """GenerateEvaluation Report"""
 total_tests = len(results)
 passed = len([r for r in results if r['status'] == 'PASS'])
 failed = len([r for r in results if r['status'] == 'FAIL'])
 skipped = len([r for r in results if r['status'] == 'SKIP'])
 partial = len([r for r in results if r['status'] == 'PARTIAL'])
 
 total_score = sum(r['score'] for r in results)
 max_score = sum(r['max_score'] for r in results)
 pass_rate = (passed / total_tests) * 100 if total_tests > 0 else 0
 
 # AccordingTestCategoryDivideGroupSystemDesign
 type_stats = {}
 for result in results:
 test_type = result['type']
 if test_type not in type_stats:
 type_stats[test_type] = {'total': 0, 'pass': 0, 'fail': 0, 'skip': 0, 'partial': 0}
 
 type_stats[test_type]['total'] += 1
 status_key = result['status'].lower()
 if status_key in type_stats[test_type]:
 type_stats[test_type][status_key] += 1
 
 # GenerateMarkdownReport
 report = f"""# Library Management SystemEvaluation Report

## Evaluation Overview

**Project Name**: Library Management System 
**Evaluation Time**: {datetime.now().strftime('%Yyear%mmonth%dday %H:%M:%S')} 
**AssessmentMarkStandard**: evaluation/detailed_test_plan.json 
**TestEnvironment**: Windows 11, Python 3.13, NoMySQLDatabaseEnvironment 

## Evaluation ResultsTotal

| TestCategory | Total | Pass | Failure | Skip | Partially Passed | Pass Rate |
|---------|------|------|------|------|---------|-------|
"""
 
 for test_type, stats in type_stats.items():
 pass_rate_type = (stats['pass'] / stats['total']) * 100 if stats['total'] > 0 else 0
 report += f"| {test_type} | {stats['total']} | {stats['pass']} | {stats['fail']} | {stats['skip']} | {stats['partial']} | {pass_rate_type:.1f}% |\n"
 
 report += f"| **Total** | **{total_tests}** | **{passed}** | **{failed}** | **{skipped}** | **{partial}** | **{pass_rate:.1f}%** |\n\n"
 
 report += f"""
**TotalScore**: {total_score}/{max_score} ({(total_score/max_score)*100:.1f}%)

## Test Results

"""
 
 # AccordingCategoryDivideGroupDisplayResult
 current_section = None
 section_map = {
 '0.': 'ProgramStartandSystemInitialInitialization',
 '1.': 'DatabaseInterfaceandInitialInitialization', 
 '2.': 'User ManagementFunction',
 '3.': 'BookManagementFunction',
 '4.': 'BorrowingManagementFunction',
 '5.': 'QueryandSystemDesignFunction',
 '6.': 'PermissionControlandDataOperation',
 '7.': 'DataVerifyandInterface',
 '8.': 'AbnormalProcessingandSystemDimensionCare'
 }
 
 for result in results:
 metric = result['metric']
 
 # CheckYesNoNewchapterEnergy
 for prefix, section_name in section_map.items():
 if metric.startswith(prefix):
 if current_section != section_name:
 current_section = section_name
 report += f"\n### {current_section}\n\n"
 break
 
 # StatusMarkstatus_mark = {
 'PASS': '✅',
 'FAIL': '❌', 
 'SKIP': '⏭️',
 'PARTIAL': '⚠️'
 }.get(result['status'], '❓')
 
 report += f"#### {metric}\n"
 report += f"- **TestCategory**: {result['type']}\n"
 report += f"- **Test Results**: {status_mark} **{result['status']}** ({result['score']}/{result['max_score']}Divide)\n"
 report += f"- **ResultDescription**: {result['message']}\n"
 
 if result['status'] != 'SKIP' and 'details' in result:
 if isinstance(result['details'], dict):
 if result['details'].get('stdout'):
 report += f"- **OutputContent**: \n```\n{result['details']['stdout'][:300]}...\n```\n"
 if result['details'].get('stderr'):
 report += f"- **ErrorInformation**: \n```\n{result['details']['stderr'][:300]}...\n```\n"
 
 report += "\n"
 
 report += """
## IssueAnalysisandRecommendation

### MainIssue
1. **DatabaseDependDepend**: itemsWeightDependDependMySQLDatabase，TestEnvironmentMissingfewDatabaseCauseLargeEditionTestNoMethodExecute
2. **CodeCodeCapacityness**: DivideOutputSaveinCodeCodeIssue，ShadowResponseinWindowsEnvironmentunderDisplay

### Improvement Recommendations
1. **Environment Configuration**: ConfigureMySQLDatabaseEnvironmentorImplementationImplementationSQLiteCapacityMode
2. **TestEnvironment**: Improved toProvideDockerCapacityDeviceorCompleteEnvironment ConfigurationScript
3. **CodeCodeProcessing**: SystemUsesUTF-8CodeCode，ChangeGoodinTextDisplayCapacityness

### FunctionEvaluate- itemsFrameworkDesignDesignCombineProcessor，ModuleizationProcessRepublicHigh
- GenerationCodeResultStructureCleanClear，SymbolCombinePythonOpenSendRuleRange
- FunctionCoverageCoverageComplete，ContainsBookManagementCoreRequest

---
**AssessmentSuccessfullyTimeBetween**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
 
 return report

def main():
 """FunctionNumber"""
 print("Library Management SystemAutomatedAssessment")
 print("=" * 40)
 
 # ExecuteTest
 results = execute_tests()
 
 # GenerateReport
 report = generate_report(results)
 
 # SaveReport
 with open('evaluation/evaluation_report.md', 'w', encoding='utf-8') as f:
 f.write(report)
 
 print("\n" + "=" * 60)
 print("AssessmentSuccessfully！ReportAlreadySaveto evaluation/evaluation_report.md")
 
 # DisplaySummaryResult
 total_tests = len(results)
 passed = len([r for r in results if r['status'] == 'PASS'])
 total_score = sum(r['score'] for r in results)
 max_score = sum(r['max_score'] for r in results)
 
 print(f"TotalTestNumber: {total_tests}")
 print(f"PassTest: {passed}")
 print(f"TotalScore: {total_score}/{max_score} ({(total_score/max_score)*100:.1f}%)")

if __name__ == '__main__':
 main()