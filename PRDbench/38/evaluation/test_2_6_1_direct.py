#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DirectInterfaceTest2.6.1Core Operation LogRecord
"""

import subprocess
import sys
import os

def test_operation_log():
    """TestoperationWorkLogRecord"""
    print("=" * 60)
    print("2.6.1 Core Operation Log-Complete Record Test")
    print("=" * 60)
    
    # OutputInputSequenceSeries：DataManagement(1) → InitialInitializationSampleData(3) → AccurateCertified(y) → ReturnReturn(0) → Exit(0)
    inputs = "1\n3\ny\n0\n0\n"
    
    print(f"OutputInputSequenceSeries: {repr(inputs)}")
    print("Explanation: DataManagement → InitialInitializationSampleData → AccurateCertified → ReturnReturn → Exit")
    
    try:
        # ExecuteTest
        result = subprocess.run(
            ['python', 'main.py'],
            input=inputs,
            text=True,
            capture_output=True,
            cwd='../src',
            timeout=60,
            encoding='utf-8',
            errors='ignore'
        )
        
        print(f"ExitCode: {result.returncode}")
        
        # CheckYesNoHasNoEffectSelectChooseError
        has_invalid_choice = "NoEffectSelectChoose" in result.stdout
        has_normal_exit = "InfectionThanksUseUseRecommendation System" in result.stdout
        
        print(f"YesNoHas'NoEffectSelectChoose'Error: {'Yes' if has_invalid_choice else 'No'}")
        print(f"ProgramNormalExit: {'Yes' if has_normal_exit else 'No'}")
        
        # DisplayRelatedKeyOutput
        if result.stdout:
            print("\nRelatedKeyOutputChipSegment:")
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['DataManagement', 'InitialInitialization', 'SampleData', 'AccurateCertified', 'ReturnReturn']):
                    print(f"  {line}")
        
        # CheckLogFile
        log_path = '../src/logs/system.log'
        if os.path.exists(log_path):
            print(f"\nCheckLogFile: {log_path}")
            
            # ReadMostNewLogEntries
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                
            # FindTodayDayLog
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            
            recent_logs = []
            for line in log_content.split('\n'):
                if today in line and any(keyword in line for keyword in ['InitialInitialization', 'Create', 'Load']):
                    recent_logs.append(line)
            
            print(f"FoundTodayJapaneseCameraRelatedLog: {len(recent_logs)}  records")
            if recent_logs:
                print("MostNewLogDiversityBook:")
                for log in recent_logs[-5:]:  # DisplayMostNew5 records
                    print(f"  {log}")
                
                # CheckYesNoContainsTestRequirements4CategoryInformation
                has_time = any('2025-' in log for log in recent_logs)
                has_operation = any('INFO' in log for log in recent_logs)
                has_params = any('Create' in log or 'Load' in log for log in recent_logs)
                has_results = any('CompleteSuccess' in log or 'records' in log for log in recent_logs)
                
                print(f"\nLogContentCheck:")
                print(f"  ContainsoperationWorkTimeBetween: {'Yes' if has_time else 'No'}")
                print(f"  ContainsoperationWorkCategoryType: {'Yes' if has_operation else 'No'}")
                print(f"  ContainsOutputInputParameter: {'Yes' if has_params else 'No'}")
                print(f"  ContainsProcessingResult: {'Yes' if has_results else 'No'}")
                
                criteria_met = sum([has_time, has_operation, has_params, has_results])
                print(f"  Meets recordsPiece: {criteria_met}/4item(s)")
                
            return not has_invalid_choice and has_normal_exit and len(recent_logs) > 0
        else:
            print(f"LogFileNotSavein: {log_path}")
            return False
            
    except Exception as e:
        print(f"TestExecuteFailure: {e}")
        return False

if __name__ == "__main__":
    success = test_operation_log()
    print(f"\nTest Results: {'Pass' if success else 'Failure'}")
    sys.exit(0 if success else 1)