#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Comparison TestScriptGenerateDevice
inevaluation/FileFolderunderBatchGenerateandExecutePlaceHasfile_comparisonTest
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def load_test_plan():
    """LoadTestDesignPlan"""
    with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_single_test_script(metric, description, testcase, expected_files):
    """asSingleitem(s)file_comparisonTestGenerateTestScript"""
    test_command = testcase.get('test_command', '')
    test_input = testcase.get('test_input', '')
    
    # GenerateAutoAutomaticFileName
    safe_name = (metric.replace(' ', '_')
                      .replace('.', '_')
                      .replace('-', '_')
                      .replace('/', '_'))
    
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoAutoGenerateFile ComparisonTestScript
Test Item: {metric}
"""

import subprocess
import sys
import os
from pathlib import Path

def test_{safe_name}():
    """Execute{metric}Test"""
    print("="*80)
    print("Test Item: {metric}")
    print("="*80)
    
    test_command = "{test_command}"
    test_input = "{test_input}"
    expected_files = {expected_files}
    
    print(f"Command: {{test_command}}")
    print(f"OutputInputSequenceSeries: {{test_input}}")
    print(f"Expected OutputFile: {{expected_files}}")
    print("-"*80)
    
    try:
        if test_input and "echo -e" in test_command:
            # ProcessingInteractiveCommand
            input_text = test_input.replace('\\\\n', '\\n')
            
            # ExtractGetImplementationInternationalExecuteCommandandEngineeringWorkDirectory
            if "cd src &&" in test_command:
                cmd = ["python", "main.py"]
                cwd = "../src"
            elif "cd evaluation &&" in test_command:
                parts = test_command.split("cd evaluation && ")[-1]
                cmd = parts.split()
                cwd = "."
            else:
                print("[Error] NoMethodParseCommandFormatStyle")
                return False
            
            print(f"ImplementationInternationalExecute: {{' '.join(cmd)}} (EngineeringWorkDirectory: {{cwd}})")
            print(f"OutputInputContent: {{repr(input_text)}}")
            
            # ExecuteCommand
            result = subprocess.run(
                cmd,
                input=input_text,
                text=True,
                capture_output=True,
                cwd=cwd,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            
        else:
            # DirectInterfaceExecuteCommand（SuitableUseAtevaluationDirectoryunderPythonScript）
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
        
        print(f"ExitCode: {{result.returncode}}")
        
        # DisplayOutput（LimitedControlLengthRepublicAvoidOverManyContent）
        if result.stdout:
            stdout_preview = result.stdout[:800] + ("...（Truncated）" if len(result.stdout) > 800 else "")
            print(f"MarkStandardOutput:\\n{{stdout_preview}}")
        
        if result.stderr:
            stderr_preview = result.stderr[:400] + ("...（Truncated）" if len(result.stderr) > 400 else "")
            print(f"MarkStandardError:\\n{{stderr_preview}}")
        
        # CheckYesNoSavein"NoEffectSelectChoose"Error
        has_invalid_choice = ("NoEffectSelectChoose" in result.stdout or 
                             "NoEffectSelectChoose" in result.stderr)
        
        if has_invalid_choice:
            print("[Failure] StillSavein'NoEffectSelectChoose'Error!")
            return False
        
        # CheckProgramYesNoNormalResultBundle
        normal_exit = (result.returncode == 0 or 
                      "InfectionThanksUseUseRecommendation System" in result.stdout or
                      "TestCompleteSuccess" in result.stdout)
        
        if not normal_exit:
            print(f"[Warning] ProgramAbnormalExit，ExitCode: {{result.returncode}}")
        
        # CheckExpectedOutputFile
        files_check_passed = True
        if expected_files:
            for expected_file in expected_files:
                # TryManyitem(s)CanEnergyFilePath
                possible_paths = [
                    expected_file,  # WhenbeforeDirectory
                    f"../{{expected_file}}",  # onLevelDirectory
                    f"../evaluation/{{expected_file}}",  # evaluationDirectory
                ]
                
                file_found = False
                for file_path in possible_paths:
                    if os.path.exists(file_path):
                        print(f"[CheckPass] ExpectedFile {{expected_file}} in {{file_path}} Found")
                        
                        # DisplayFileInformation
                        try:
                            file_size = os.path.getsize(file_path)
                            print(f"FileLargeSmall: {{file_size}} CharacterEnergy")
                            
                            if file_size > 0:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    preview = content[:150] + ("..." if len(content) > 150 else "")
                                    print(f"FileContentPreview: {{preview}}")
                        except Exception as e:
                            print(f"ReadFileInformationFailure: {{e}}")
                        
                        file_found = True
                        break
                
                if not file_found:
                    print(f"[Warning] ExpectedFile {{expected_file}} NotFound")
                    files_check_passed = False
        
        # ComprehensiveCombineJudgeBreakTest Results
        if has_invalid_choice:
            test_result = False
            result_msg = "Failure - SaveinNoEffectSelectChooseError"
        elif normal_exit:
            test_result = True
            result_msg = "Pass - ProgramNormalExecute"
        else:
            test_result = False
            result_msg = "Failure - ProgramAbnormalExit"
        
        print(f"\\n[{{result_msg}}]")
        return test_result
        
    except subprocess.TimeoutExpired:
        print("[Failure] TestUltraTime（60Second）")
        return False
    except Exception as e:
        print(f"[Failure] ExecuteAbnormal: {{e}}")
        return False

if __name__ == "__main__":
    success = test_{safe_name}()
    print("="*80)
    print(f"Test Results: {{'Pass' if success else 'Failure'}}")
    sys.exit(0 if success else 1)
'''
    
    return script_content, f"test_{safe_name}.py"

def generate_all_test_scripts():
    """GeneratePlaceHasfile_comparisonTestScript"""
    tests = load_test_plan()
    file_comparison_tests = [test for test in tests if test.get('type') == 'file_comparison']
    
    print(f"Found {len(file_comparison_tests)} item(s)file_comparisonTest")
    
    # CreateTestScriptDirectory
    test_dir = Path("generated_file_comparison_tests")
    test_dir.mkdir(exist_ok=True)
    
    generated_scripts = []
    
    for i, test in enumerate(file_comparison_tests, 1):
        metric = test['metric']
        description = test['description']
        testcase = test['testcases'][0]  # GetFirstitem(s)Test Case
        expected_files = test.get('expected_output_files', [])
        
        # GenerateScriptContent
        script_content, script_name = generate_single_test_script(
            metric, description, testcase, expected_files
        )
        
        # WriteInputScriptFile
        script_path = test_dir / script_name
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        generated_scripts.append({
            'name': metric,
            'script_path': str(script_path),
            'description': description
        })
        
        print(f"{i:2d}. AlreadyGenerate: {script_path}")
    
    return generated_scripts

def execute_all_tests(test_scripts):
    """BatchExecutePlaceHasGenerateTestScript"""
    print(f"\n{'='*80}")
    print("StartingBatchExecuteFile ComparisonTest")
    print('='*80)
    
    results = []
    
    for i, test_script in enumerate(test_scripts, 1):
        print(f"\n[{i}/{len(test_scripts)}] ExecuteTest: {test_script['name']}")
        print(f"ScriptPath: {test_script['script_path']}")
        
        try:
            result = subprocess.run(
                [sys.executable, test_script['script_path']],
                capture_output=True,
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='ignore'
            )
            
            success = result.returncode == 0
            results.append({
                'name': test_script['name'],
                'success': success,
                'output': result.stdout,
                'error': result.stderr
            })
            
            status = "[Pass]" if success else "[Failure]"
            print(f"{status} {test_script['name']}")
            
        except subprocess.TimeoutExpired:
            print(f"[UltraTime] {test_script['name']}")
            results.append({
                'name': test_script['name'],
                'success': False,
                'output': "",
                'error': "TestUltraTime（120Second）"
            })
        except Exception as e:
            print(f"[Error] {test_script['name']}: {e}")
            results.append({
                'name': test_script['name'],
                'success': False,
                'output': "",
                'error': str(e)
            })
    
    return results

def generate_test_report(results):
    """GenerateDetailedTestReport"""
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    report_content = f"""# File Comparison TestReport

## TestSummaryOverview
- **ExecuteTimeBetween**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **TotalTestNumber**: {total}
- **PassNumber**: {passed}
- **FailureNumber**: {failed}
- **SuccessRate**: {passed/total*100:.1f}%

## Test ResultsDetails

"""
    
    for result in results:
        status_icon = "✅" if result['success'] else "❌"
        report_content += f"### {status_icon} {result['name']}\n\n"
        
        if result['success']:
            report_content += "**Status**: Test Passed\n\n"
        else:
            report_content += "**Status**: Test Failed\n\n"
            if result['error']:
                report_content += f"**ErrorInformation**: \n```\n{result['error']}\n```\n\n"
        
        report_content += "---\n\n"
    
    # SaveReport
    report_path = "file_comparison_test_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\nDetailedTestReportAlreadyGenerate: {report_path}")
    return report_path

def main():
    """MainFunctionNumber"""
    print("File Comparison TestScriptGenerateDeviceandExecuteDevice")
    print("="*80)
    
    # FirstStep：GeneratePlaceHasTestScript
    print("\nFirstStep：GenerateTestScript")
    print("-"*40)
    test_scripts = generate_all_test_scripts()
    
    # SecondStep：ExecutePlaceHasTest
    print("\nSecondStep：BatchExecuteTest")
    print("-"*40)
    results = execute_all_tests(test_scripts)
    
    # ThirdStep：GenerateTestReport
    print("\nThirdStep：GenerateTestReport")
    print("-"*40)
    report_path = generate_test_report(results)
    
    # FourthStep：OutputMostEndSystemDesign
    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed
    
    print(f"\n{'='*80}")
    print("MostEndTest ResultsSystemDesign")
    print('='*80)
    print(f"TotalTestNumber: {total}")
    print(f"PassNumber: {passed}")
    print(f"FailureNumber: {failed}")
    print(f"SuccessRate: {passed/total*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 PlaceHasFile ComparisonTestAverageAlreadyPass！")
        return True
    else:
        print(f"\n⚠️  Has {failed} item(s)Test Failed，PleaseViewDetailsReport: {report_path}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)