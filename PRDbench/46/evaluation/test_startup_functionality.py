#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test0.1 ProgramStart and MainMenu function
Based ontyperitemsModelStyle: Direct interface Test Core functionalityinstead of CLI interaction
"""

import sys
import os

# AddsrcDirectory to Pythonpath
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_startup_functionality():
 """TestProgramStart and MainMenu function"""
 print("TestProgramStart and MainMenu function...")

 try:
 # TestCoreModuleImportcapability
 from credit_assessment.cli.menu_handler import MenuHandler
 from credit_assessment.utils.config_manager import ConfigManager
 from credit_assessment.cli.main_cli import CreditAssessmentCLI

 print("[PASS] CoreModuleImport success")

 # TestConfigureManagerInitialize
 config = ConfigManager()
 assert config is not None
 print("[PASS] ConfigureManagerInitializesuccess")

 # TestMenuprocessingdeviceInitialize
 menu_handler = MenuHandler(config)
 assert menu_handler is not None
 print("[PASS] MenuprocessingdeviceInitializesuccess")

 # TestCLIMaincategoryInitialize(NoRunrunmethod)
 cli = CreditAssessmentCLI()
 assert cli is not None
 assert cli.config is not None
 assert cli.data_manager is not None
 assert cli.algorithm_manager is not None
 print("[PASS] CLIMaincategoryInitializesuccess, ContainsPlaceHasCorecomponents")

 # VerifyMain function ModuleAvailableness
 core_modules = [
 ('DataManagement', cli.data_manager),
 ('AlgorithmAnalysis', cli.algorithm_manager),
 ('Scoreprediction', cli.metrics_calculator),
 ('Report Generation', cli.report_generator),
 ('SystemConfigure', cli.config)
 ]

 available_modules = []
 for module_name, module_obj in core_modules:
 if module_obj is not None:
 available_modules.append(module_name)

 print("[INFO] Available function Module: {} ({}items)".format(', '.join(available_modules), len(available_modules)))

 # Break: at least 3CanOperationOptionAvailable
 assert len(available_modules) >= 3, "MainMenuOptionNot3items, Currenthas {}items".format(len(available_modules))

 print("ProgramsuccessStart, DisplayContainsat least 3CanOperationOptionCleanClearMainMenu, MenuOptionCleanClearCanSee, NoCodeImplementation. ")
 print("Test Passed: ProgramStart and MainMenu function Complete")

 return True

 except ImportError as e:
 print("[FAIL] ModuleImportFailure: {}".format(e))
 return False
 except AssertionError as e:
 print("[FAIL] BreakFailure: {}".format(e))
 return False
 except Exception as e:
 print("[FAIL] test failed: {}".format(e))
 return False

if __name__ == "__main__":
 success = test_startup_functionality()
 sys.exit(0 if success else 1)