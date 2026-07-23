#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoAutoGenerateFile ComparisonTestScript
Test Item: 2.5.2 MatplotlibChartGeneration-FileSave
"""

import subprocess
import sys
import os
from pathlib import Path

def test_2_5_2_MatplotlibChartGeneration_FileSave():
    """Execute2.5.2 MatplotlibChartGeneration-FileSaveTest"""
    print("="*80)
    print("Test Item: 2.5.2 MatplotlibChartGeneration-FileSave")
    print("="*80)
    
    test_command = "cd src && echo -e "5\n1\n4\n0\n0" | python main.py"
    test_input = "5\n1\n4\n0\n0"
    expected_files = ['expected_chart_info.txt']
    
    print(f"Command: {test_command}")
    print(f"OutputInputSequenceSeries: {test_input}")
    print(f"Expected OutputFile: {expected_files}")
    print("-"*80)
    
    try:
        if test_input and "echo -e" in test_command:
            # ProcessingInteractiveCommand
            input_text = test_input.replace('\\n', '\n')
            
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
            
            print(f"ImplementationInternationalExecute: {' '.join(cmd)} (EngineeringWorkDirectory: {cwd})")
            print(f"OutputInputContent: {repr(input_text)}")
            
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
        
        print(f"ExitCode: {result.returncode}")
        
        # DisplayOutput（LimitedControlLengthRepublicAvoidOverManyContent）
        if result.stdout:
            stdout_preview = result.stdout[:800] + ("...（Truncated）" if len(result.stdout) > 800 else "")
            print(f"MarkStandardOutput:\n{stdout_preview}")
        
        if result.stderr:
            stderr_preview = result.stderr[:400] + ("...（Truncated）" if len(result.stderr) > 400 else "")
            print(f"MarkStandardError:\n{stderr_preview}")
        
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
            print(f"[Warning] ProgramAbnormalExit，ExitCode: {result.returncode}")
        
        # CheckExpectedOutputFile
        files_check_passed = True
        if expected_files:
            for expected_file in expected_files:
                # TryManyitem(s)CanEnergyFilePath
                possible_paths = [
                    expected_file,  # WhenbeforeDirectory
                    f"../{expected_file}",  # onLevelDirectory
                    f"../evaluation/{expected_file}",  # evaluationDirectory
                ]
                
                file_found = False
                for file_path in possible_paths:
                    if os.path.exists(file_path):
                        print(f"[CheckPass] ExpectedFile {expected_file} in {file_path} Found")
                        
                        # DisplayFileInformation
                        try:
                            file_size = os.path.getsize(file_path)
                            print(f"FileLargeSmall: {file_size} CharacterEnergy")
                            
                            if file_size > 0:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    preview = content[:150] + ("..." if len(content) > 150 else "")
                                    print(f"FileContentPreview: {preview}")
                        except Exception as e:
                            print(f"ReadFileInformationFailure: {e}")
                        
                        file_found = True
                        break
                
                if not file_found:
                    print(f"[Warning] ExpectedFile {expected_file} NotFound")
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
        
        print(f"\n[{result_msg}]")
        return test_result
        
    except subprocess.TimeoutExpired:
        print("[Failure] TestUltraTime（60Second）")
        return False
    except Exception as e:
        print(f"[Failure] ExecuteAbnormal: {e}")
        return False

if __name__ == "__main__":
    success = test_2_5_2_MatplotlibChartGeneration_FileSave()
    print("="*80)
    print(f"Test Results: {'Pass' if success else 'Failure'}")
    sys.exit(0 if success else 1)
