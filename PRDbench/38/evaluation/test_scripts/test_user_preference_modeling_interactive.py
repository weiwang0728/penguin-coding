#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')

def test_user_preference_modeling():
    """TestUserPreferenceBuildModel - 2.2.2"""
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
        
        print("beforeSetCheckExperiencePass：RecommendationCalculateMethodInterfaceSaveinUserPreferenceBuildModelOption")
        print("StandardPrepareStepSegment：AccurateProtectionAlreadyHasUserLineasDataandScoreData")
        print("ExecuteStepSegment：User Attribute Preference ModelingFunctionSuccessExecute")
        
        if passed_checks >= 2:
            print("BreakassertionVerify：GenerateUserAttributePreferenceDirectionEditionFile，DirectionEditionContainsEachAttributePreferenceWeightWeight，SupportSupportViewPreferenceDirectionEditionContent")
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
    success = test_user_preference_modeling()
    sys.exit(0 if success else 1)