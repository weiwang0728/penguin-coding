"""
Data Cleaning Unit Tests
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
# Add src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from data_processor import DataProcessor


class TestDataCleaning:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()

        # Create test data with various data issues
        self.dirty_data = pd.DataFrame({
            'biz_id': ['B001', 'B002', 'B003', 'B004', 'B005', 'B006'],
            'trans_date': pd.to_datetime([
                '2023-06-15', '2023-06-16', '2023-05-10',  # Normal dates
                '2023-03-01', '2023-06-17', '2023-06-15'   # Before opening date, normal, duplicate
            ]),
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S001'],
            'brand_name': ['Brand A', None, 'Brand C', 'Brand D', '', 'Brand A'],  # Contains null values
            'amount': [1000, 1500, None, -500, 2000, 1000],  # Contains null and negative values
            'opening_date': pd.to_datetime([
                '2023-05-01', '2023-05-01', '2023-05-01',
                '2023-05-01', '2023-05-01', '2023-05-01'
            ])
        })

    def test_missing_value_handling(self):
        """Test missing value handling"""
        cleaned_data = self.processor.data_cleaning(self.dirty_data.copy())

        # Verify brand_name missing values are filled
        assert cleaned_data['brand_name'].notna().all()
        assert 'Unknown Brand' in cleaned_data['brand_name'].values

        # Verify records with null amount are removed
        assert cleaned_data['amount'].notna().all()

        # Verify record count is reasonable after cleaning (removes nulls, negatives, early transactions, etc.)
        assert len(cleaned_data) <= len(self.dirty_data)
        assert len(cleaned_data) > 0  # Ensure there's still valid data

    def test_anomaly_filtering(self):
        """Test anomaly filtering"""
        cleaned_data = self.processor.data_cleaning(self.dirty_data.copy())

        # Verify negative amounts are filtered
        assert (cleaned_data['amount'] > 0).all()

        # Verify transactions before opening date are filtered
        assert (cleaned_data['trans_date'] >= cleaned_data['opening_date']).all()

    def test_duplicate_removal(self):
        """Test duplicate removal"""
        # Create explicit duplicate data
        duplicate_data = pd.DataFrame({
            'biz_id': ['B001', 'B001', 'B002'],
            'trans_date': pd.to_datetime(['2023-06-15', '2023-06-15', '2023-06-16']),
            'store_id': ['S001', 'S001', 'S002'],
            'brand_name': ['Brand A', 'Brand A', 'Brand B'],
            'amount': [1000, 1000, 1500],
            'opening_date': pd.to_datetime(['2023-05-01', '2023-05-01', '2023-05-01'])
        })

        cleaned_data = self.processor.data_cleaning(duplicate_data.copy())

        # Verify duplicates are removed (based on composite_key)
        # composite_key = biz_id + trans_date + store_id
        composite_keys = cleaned_data['biz_id'] + '_' + cleaned_data['trans_date'].dt.strftime('%Y%m%d') + '_' + cleaned_data['store_id']
        assert len(composite_keys) == len(composite_keys.unique())

    def test_data_integrity_after_cleaning(self):
        """Test data integrity after cleaning"""
        cleaned_data = self.processor.data_cleaning(self.dirty_data.copy())

        # Verify required columns still exist
        required_columns = ['biz_id', 'trans_date', 'store_id', 'brand_name', 'amount']
        for col in required_columns:
            assert col in cleaned_data.columns

        # Verify data types are correct
        assert pd.api.types.is_datetime64_any_dtype(cleaned_data['trans_date'])
        assert pd.api.types.is_numeric_dtype(cleaned_data['amount'])

        # Verify record count is reasonable after cleaning
        assert len(cleaned_data) > 0
        assert len(cleaned_data) <= len(self.dirty_data)

    def test_empty_dataset_handling(self):
        """Test empty dataset handling"""
        empty_data = pd.DataFrame(columns=['biz_id', 'trans_date', 'store_id', 'brand_name', 'amount', 'opening_date'])

        # Should handle empty dataset without error
        cleaned_data = self.processor.data_cleaning(empty_data.copy())
        assert len(cleaned_data) == 0
        assert list(cleaned_data.columns) == list(empty_data.columns)


if __name__ == "__main__":
    pytest.main([__file__])
