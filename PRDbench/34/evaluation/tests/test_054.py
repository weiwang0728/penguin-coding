#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pandas as pd
import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info

def test_function():
    """Test data saving, file format, and column order."""
    # SaveNativeInitialFileName
    original_filename = info.cur_filename
    test_filename = "test_data_054.csv"
    info.cur_filename = test_filename
    
    # Clear existing data before the test
    info.alist = []
    info.blist = []
    
    # Add one test member
    info.add("ZhangSam", "Beijing", "19900101", "0", "175.5", "Bachelor", "SoftwareEngineer", "SeniorEngineer", "", "0", "Male")
    info.save_file(info.blist)
    
    # Verify the file was saved
    assert os.path.exists(test_filename), "The data file should be saved"
    
    # Verify file encoding and format
    try:
        # Try reading the file with UTF-8 encoding
        df = pd.read_csv(test_filename, encoding='utf-8')
        
        # Verify the column order matches the PRD requirements
        expected_columns = ["name", "born_place", "born_date", "dead_date", "height", "edu_bg", "pos", "top_pos", "born_rela", "rela_ship", "sex"]
        actual_columns = df.columns.tolist()
        
        assert actual_columns == expected_columns, f"Column order is incorrect. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Verify the CSV contains data
        assert len(df) > 0, "The file should contain data"
        
        # Verify the saved content
        assert df.iloc[0]['name'] == 'ZhangSam', "The saved data content should be correct"
        
    except UnicodeDecodeError:
        pytest.fail("The file encoding is not UTF-8")
    except Exception as e:
        pytest.fail(f"File format validation failed: {e}")
    
    # Clean up test data
    info.alist = []
    info.blist = []
    info.cur_filename = original_filename
    
    # Delete the test file
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("The data file uses UTF-8 encoding, comma-separated CSV format, and the expected column order.")

if __name__ == "__main__":
    test_function()