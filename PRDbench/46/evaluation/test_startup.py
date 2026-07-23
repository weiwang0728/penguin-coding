#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProgramStartTest Script

Atsrc/GenerationCodeinImportIssue, CreateTest ScriptVerifyProgramStartup functionality
"""

import sys
import os
import subprocess
from pathlib import Path

def test_program_startup():
 """TestProgramStart and MainMenu"""
 print("=== 0.1 ProgramStart and MainMenuTest ===")

 # Direct interfaceRunmain.pyGetOutput
 src_path = Path(__file__).parent.parent / "src"
 main_py = src_path / "main.py"
 test_input = Path(__file__).parent / "test_01_startup.in"

 try:
 # UsesubprocessRunProgram
 result = subprocess.run(
 [sys.executable, str(main_py)],
 input="0\ny\n", # Direct interfaceOutputinputExitCommand
 text=True,
 capture_output=True,
 timeout=30,
 cwd=str(src_path.parent),
 encoding='utf-8',
 errors='ignore'
 )

 stdout = result.stdout if result.stdout else ""
 stderr = result.stderr if result.stderr else ""
 output = stdout + stderr

 print("ProgramOutput:")
 print("-" * 50)
 print(output)
 print("-" * 50)

 # CheckwhethersuccessStart
 startup_indicators = [
 "Silver rowsitemsPersonUseEnergyAssessmentSystem",
 "MainMenu",
 "Data",
 "Algorithm",
 "Assessment"
 ]

 found_indicators = []
 for indicator in startup_indicators:
 if indicator in output:
 found_indicators.append(indicator)

 print(f"\nStartCheckresult:")
 print(f"toKeyWord: {found_indicators}")

 # CheckwhetherContainsat least 3CanOperationOption
 menu_options = 0
 if "1" in output or "Data" in output:
 menu_options += 1
 if "2" in output or "Algorithm" in output:
 menu_options += 1
 if "3" in output or "Assessment" in output or "prediction" in output:
 menu_options += 1
 if "4" in output or "Report" in output or "Visualization" in output:
 menu_options += 1
 if "5" in output or "settings" in output:
 menu_options += 1

 print(f"CheckTest to MenuOptionnumber: {menu_options}")

 # BreakTest result s
 if len(found_indicators) >= 2 and menu_options >= 3:
 print("✓ ProgramStartTest Passed")
 print("✓ DisplayContainsat least 3CanOperationOptionCleanClearMainMenu")
 return True, "ProgramsuccessStart, DisplayContainsat least 3CanOperationOptionCleanClearMainMenu, MenuOptionCleanClearCanSee, NoCodeImplementation. "
 elif len(found_indicators) >= 1:
 print("⚠ ProgramDivideStart, MenuNotComplete")
 return False, f"ProgramStartMenuDisplayNotComplete, CheckTestto{menu_options}itemsOption(at least 3)"
 else:
 print("✗ ProgramStartFailure")
 return False, f"ProgramStartFailureorNoMethodcorrectDisplayMenu: {output[:200]}..."

 except subprocess.TimeoutExpired:
 print("✗ ProgramStartUltraTime")
 return False, "ProgramStartUltraTime, CanEnergySaveinNoLimitedEnvironmentorEqualWaitOutputinputIssue"
 except Exception as e:
 print(f"✗ TestExecuteError: {str(e)}")
 return False, f"TestExecuteError: {str(e)}"

def test_module_import s():
 """TestModuleImportSituation"""
 print("\n=== ModuleImportCheck ===")

 src_path = Path(__file__).parent.parent / "src"
 sys.path.insert(0, str(src_path))

 import_result s = {}

 # TestEachModuleImport
 modules_to_test = [
 "credit_assessment",
 "credit_assessment.utils",
 "credit_assessment.data",
 "credit_assessment.algorithms",
 "credit_assessment.evaluation",
 "credit_assessment.cli"
 ]

 for module_name in modules_to_test:
 try:
 __import__(module_name)
 import_result s[module_name] = "success"
 print(f"✓ {module_name}")
 except Exception as e:
 import_result s[module_name] = f"Failure: {str(e)}"
 print(f"✗ {module_name}: {str(e)}")

 return import_result s

if __name__ == "__main__":
 print("StartingProgramStart and MainMenuTest...")

 # CheckModuleImport
 import_result s = test_module_import s()

 # after Test ProgramStart
 success, message = test_program_startup()

 print(f"\n=== Test result sTotal ===")
 print(f"StartTest: {'Pass' if success else 'Failure'}")
 print(f"resultDescribe: {message}")

 sys.exit(0 if success else 1)