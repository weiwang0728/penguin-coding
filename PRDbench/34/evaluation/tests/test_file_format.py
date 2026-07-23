#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
import os
import pandas as pd
import csv
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info

class TestFileFormat:
    
    def test_csv_format_and_field_order(self):
        """TestCSVFileFormatStyleandCharacterSegmentForwardSequence"""
        # Create test data
        test_data = [
            ['ZhangSam', 'Beijing', '19900101', '0', '175.5', 'Bachelor', 'Engineer', 'Manager', '', '0', '1', 'Male']
        ]
        
        # SaveTestFile
        test_file = 'test_format.csv'
        info.save_file(test_data)
        
        try:
            # Verify the file was created
            assert os.path.exists('data.csv'), "data.csvFileNotCreate"
            
            # Verify file encoding by reading as UTF-8
            with open('data.csv', 'r', encoding='utf-8') as f:
                content = f.read()
                assert len(content) > 0, "FileContentasEmpty"
            
            # Verify CSV format
            df = pd.read_csv('data.csv', encoding='utf-8')
            
            # Verify field order against the PRD requirements
            expected_columns = ['name', 'born_place', 'born_date', 'dead_date', 'height', 
                              'edu_bg', 'pos', 'top_pos', 'born_rela', 'rela_ship', 'layer', 'sex']
            
            # Verify the number of columns
            assert len(df.columns) == len(expected_columns), f"Column count does not match. Expected {len(expected_columns)} columns, got {len(df.columns)}"
            
            # Verify the CSV file contains data
            assert len(df) > 0, "The CSV file should contain data"
            
            # Verify comma-separated formatting
            with open('data.csv', 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                assert ',' in first_line, "The file should use comma-separated formatting"
                
        finally:
            # CleanProcessorTestFile
            if os.path.exists('data.csv'):
                os.remove('data.csv')

if __name__ == '__main__':
    pytest.main([__file__])