#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info
import pandas as pd

class TestDataProcessing:
    
    def test_data_type_handling(self):
        """Test data type handling and aggregated results."""
        # Prepare test data
        test_data = [
            ['ZhangSam', 'Beijing', '19900101', '0', '175.5', 'Bachelor', 'Engineer', 'Manager', '', '0', '1', 'Male'],
            ['LiSi', 'Shanghai', '19850615', '20201212', '168.0', 'ResearchGraduate', 'Teacher', 'Director', '', '0', '1', 'Female'],
            ['WangWu', 'Guangzhou', '19750320', '0', '180.2', 'HighSchool', 'Driver', 'TeamLead', '', '0', '1', 'Male']
        ]
        
        # Save to a temporary file
        temp_file = 'temp_test_data.csv'
        df = pd.DataFrame(test_data, columns=[
            'name', 'born_place', 'born_date', 'dead_date', 'height', 
            'edu_bg', 'pos', 'top_pos', 'born_rela', 'rela_ship', 'layer', 'sex'
        ])
        df.to_csv(temp_file, index=False, encoding='utf-8')
        
        try:
            # Read test data and convert value types
            df_read = pd.read_csv(temp_file, encoding='utf-8')
            
            # Verify data type processing
            assert len(df_read) == 3
            
            # Verify numeric conversion for height
            heights = df_read['height'].astype(float)
            assert all(isinstance(h, float) for h in heights)
            
            # Verify date string formatting
            birth_dates = df_read['born_date'].astype(str)
            assert all(len(date) == 8 for date in birth_dates if date != '0')
            
            # Verify aggregated gender counts
            male_count = len(df_read[df_read['sex'] == 'Male'])
            female_count = len(df_read[df_read['sex'] == 'Female'])
            assert male_count + female_count == len(df_read)
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == '__main__':
    pytest.main([__file__])