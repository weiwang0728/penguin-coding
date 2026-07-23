#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.1.1a&b Data import function - CSVandExcelForformatSupportSupport
Based ontyperitemsModelStyle: Direct interface Test Core functionalityinstead of CLI interaction
"""

import sys
import os
import pandas as pd

# AddsrcDirectory to Pythonpath
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_csv_import():
 """TestCSV formatData import function"""
 print("TestCSV formatData import...")

 try:
 from credit_assessment.data.data_manager import DataManager
 from credit_assessment.utils.config_manager import ConfigManager

 # Initialize data manager
 config = ConfigManager()
 data_manager = DataManager(config)

 # TestCSVFile path
 csv_file = "test_data_csv.csv"

 if not os.path.exists(csv_file):
 print("[FAIL] Test file does not exist: {}".format(csv_file))
 return False

 # Execute CSVImport
 df = data_manager.import_data(csv_file, validate=False)

 # VerifyImport result
 assert isinstance(df, pd.DataFrame), "Import resultNotyesDataFrame"
 assert len(df) > 0, "ImportData as Empty"
 assert len(df.columns) > 0, "ImportDataHas columns"

 print("[PASS] CSV Data Import success")
 print("[INFO] ImportData: {} rows, {} columns".format(len(df), len(df.columns)))
 print("CSV Data Import Test Passed, ProgramclearReportData import success, correctDisplayImportData row count, VerifyCSV formatCompleteAutomaticSupportSupport. ")

 return True

 except Exception as e:
 print("[FAIL] CSV Import test failed: {}".format(e))
 return False

def test_excel_import():
 """TestExcelForformatData import function"""
 print("\n Test ExcelForformatData import...")

 try:
 from credit_assessment.data.data_manager import DataManager
 from credit_assessment.utils.config_manager import ConfigManager

 # Initialize data manager
 config = ConfigManager()
 data_manager = DataManager(config)

 # TestExcelFile path
 excel_file = "test_data_excel.xlsx"

 if not os.path.exists(excel_file):
 print("[FAIL] Test file does not exist: {}".format(excel_file))
 return False

 # ExecuteExcelImport
 df = data_manager.import_data(excel_file, validate=False)

 # VerifyImport result
 assert isinstance(df, pd.DataFrame), "Import resultNotyesDataFrame"
 assert len(df) > 0, "ImportData as Empty"
 assert len(df.columns) > 0, "ImportDataHas columns"

 print("[PASS] ExcelData import success")
 print("[INFO] ImportData: {} rows, {} columns".format(len(df), len(df.columns)))
 print("ExcelForformatImportTest Passed, ProgramclearReport'Import success'DisplayImportData row count, VerifyExcelForformatCompleteAutomaticSupportSupport. ")

 return True

 except Exception as e:
 print("[FAIL] ExcelImport test failed: {}".format(e))
 return False

def test_data_import_formats():
 """Test data ImportForformatSupportSupport function"""
 print("Test data ImportForformatSupportSupport function...")

 csv_result = test_csv_import()
 excel_result = test_excel_import()

 if csv_result and excel_result:
 print("\n[PASS] PlaceHasDataForformatImportTest Passed")
 print("Test Passed: Data import functionSupportSupportCSVandExcelForformatComplete")
 return True
 else:
 print("\n[FAIL] DivideDataForformatImport test failed")
 return False

if __name__ == "__main__":
 success = test_data_import_formats()
 sys.exit(0 if success else 1)