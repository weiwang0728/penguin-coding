#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# AddsrcDirectorytoPythonPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from data_manager import DataManager

def test_csv_import():
    """TestCSVData ImportFunction"""
    try:
        data_manager = DataManager()
        # DirectInterfaceAdjustUseImportFunction
        result = data_manager.import_csv_data('../evaluation/test_users.csv', data_type='users')
        if result is not None and not result.empty:
            print("SUCCESS: CSVData ImportSuccess")
            print(f"ImportRecordNumber: {len(result)}")
            return True
        else:
            print("ERROR: CSVData ImportFailure")
            return False
    except Exception as e:
        print(f"ERROR: ImportOverProcessOutputWrong: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_import()
    sys.exit(0 if success else 1)
