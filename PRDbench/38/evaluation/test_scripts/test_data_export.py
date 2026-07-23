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
import pandas as pd

def test_csv_export():
    """TestCSVData ExportFunction"""
    try:
        data_manager = DataManager()
        
        # CreateTestData
        test_users = pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'age': [25, 30, 28, 35, 22],
            'gender': ['M', 'F', 'M', 'F', 'M'],
            'registration_date': ['2023-01-01'] * 5
        })
        
        # ExportData
        output_path = '../evaluation/exported_users.csv'
        result = data_manager.export_csv_data(test_users, output_path)
        
        if os.path.exists(output_path):
            print("SUCCESS: CSVData ExportSuccess")
            print(f"ExportFile: {output_path}")
            print(f"ExportRecordNumber: {len(test_users)}")
            return True
        else:
            print("ERROR: CSVData ExportFailure")
            return False
            
    except Exception as e:
        print(f"ERROR: ExportOverProcessOutputWrong: {e}")
        return False

if __name__ == "__main__":
    success = test_csv_export()
    sys.exit(0 if success else 1)
