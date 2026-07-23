"""
High Value Attribute Tag Generation Unit Tests
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


class TestValueTagGeneration:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()

        # Create RFM test data
        self.rfm_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005'],
            'recency': [5, 30, 60, 10, 45],
            'frequency': [15, 8, 3, 12, 5],
            'monetary': [8000, 3000, 1000, 6000, 2000]
        })

        # Create decomposition result data
        self.decomp_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005'],
            'trend': [7500, 2800, 1200, 5800, 1800],
            'seasonal': [100, 50, 0, 80, 20],
            'residual': [200, 150, 100, 180, 120],
            'decomposition_method': ['STL', 'STL', 'Enhanced Statistics', 'STL', 'Enhanced Statistics']
        })

    def test_value_tag_generation_execution(self):
        """Test value tag generation executes successfully"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)

        # Verify result contains all stores
        assert len(result_df) == 5

        # Verify value_tag column exists
        assert 'value_tag' in result_df.columns

        # Verify all stores have tags
        assert result_df['value_tag'].notna().all()

    def test_value_tag_types(self):
        """Test value tag type correctness"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)

        # Get all generated tag types
        tag_types = result_df['value_tag'].unique()

        # Expected tag types
        expected_tags = {
            "Growth High Value", "Stable High Value", "Potential High Value",
            "Development High Value", "Watch High Value", "Insufficient Data"
        }

        # Verify all generated tags are within expected range
        for tag in tag_types:
            assert tag in expected_tags, f"Unknown value tag: {tag}"

    def test_high_value_tag_logic(self):
        """Test high value tag generation logic"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)

        # S001 should be high value store (high monetary, high frequency, low recency, positive trend)
        s001_tag = result_df[result_df['store_id'] == 'S001']['value_tag'].iloc[0]
        assert s001_tag in ["Growth High Value", "Stable High Value"]

        # S003 should be Watch High Value (all metrics are low)
        s003_tag = result_df[result_df['store_id'] == 'S003']['value_tag'].iloc[0]
        assert s003_tag == "Watch High Value"

    def test_missing_data_handling(self):
        """Test missing data handling"""
        # Create decomposition data with missing values
        missing_decomp = self.decomp_data.copy()
        missing_decomp.loc[0, 'trend'] = np.nan

        result_df = self.processor.generate_value_tags(self.rfm_data, missing_decomp)

        # Verify missing data is handled correctly
        s001_tag = result_df[result_df['store_id'] == 'S001']['value_tag'].iloc[0]
        assert s001_tag == "Insufficient Data"

    def test_tag_distribution(self):
        """Test tag distribution reasonableness"""
        result_df = self.processor.generate_value_tags(self.rfm_data, self.decomp_data)

        # Verify tag distribution
        tag_counts = result_df['value_tag'].value_counts()

        # Each tag should have at least 1 store (based on our test data)
        assert len(tag_counts) >= 1
        assert tag_counts.sum() == len(result_df)


if __name__ == "__main__":
    pytest.main([__file__])
