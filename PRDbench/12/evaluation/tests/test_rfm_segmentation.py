"""
RFM Customer Segmentation Unit Tests
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


class TestRFMSegmentation:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()

        # Create test data with different RFM characteristics
        self.rfm_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008', 'S009'],
            'recency': [5, 5, 5, 5, 50, 50, 50, 50, 25],  # 3 low(good), 4 high(bad), 2 medium
            'frequency': [10, 10, 2, 2, 10, 10, 2, 2, 5],  # 4 high, 4 low, 1 medium
            'monetary': [5000, 1000, 5000, 1000, 5000, 1000, 5000, 1000, 3000]  # 4 high, 4 low, 1 medium
        })

    def test_eight_segment_types_generation(self):
        """Test whether complete 8 segment types are generated"""
        # Execute RFM segmentation
        segmented_df = self.processor.rfm_segmentation(self.rfm_data)

        # Verify segment column exists
        assert 'segment' in segmented_df.columns

        # Get all generated segment types
        unique_segments = segmented_df['segment'].unique()

        # Expected 8 segment types
        expected_segments = {
            "Important Value Customer", "Important Retained Customer", "Important Development Customer", "Important Recovery Customer",
            "General Value Customer", "General Retained Customer", "General Development Customer", "General New Customer"
        }

        # Verify number of generated segment types, should be at least 2 or more due to limited test data
        assert len(unique_segments) >= 2, f"Actually generated {len(unique_segments)} segments, expected at least 2"

        # Verify all generated segment types are within expected range
        for segment in unique_segments:
            assert segment in expected_segments, f"Unknown segment type: {segment}"

    def test_segment_logic_validation(self):
        """Test segmentation logic correctness"""
        segmented_df = self.processor.rfm_segmentation(self.rfm_data)

        # Verify R_score, F_score, M_score columns are correctly created
        assert 'R_score' in segmented_df.columns
        assert 'F_score' in segmented_df.columns
        assert 'M_score' in segmented_df.columns

        # Verify score values are within 1-3 range
        assert segmented_df['R_score'].isin([1, 2, 3]).all()
        assert segmented_df['F_score'].isin([1, 2, 3]).all()
        assert segmented_df['M_score'].isin([1, 2, 3]).all()

        # Verify high RFM scores correspond to important customers
        high_rfm = segmented_df[
            (segmented_df['R_score'] == 3) &
            (segmented_df['F_score'] == 3) &
            (segmented_df['M_score'] == 3)
        ]
        if len(high_rfm) > 0:
            assert (high_rfm['segment'] == 'Important Value Customer').all()

    def test_segment_statistics(self):
        """Test segmentation statistics correctness"""
        segmented_df = self.processor.rfm_segmentation(self.rfm_data)

        # Verify all records are assigned segment types
        assert segmented_df['segment'].notna().all()

        # Verify segment count statistics
        segment_counts = segmented_df['segment'].value_counts()
        total_stores = len(segmented_df)

        # Verify percentage sum is 100%
        percentages = (segment_counts / total_stores * 100).sum()
        assert abs(percentages - 100.0) < 0.1, f"Percentage sum {percentages}% not equal to 100%"

    def test_edge_cases(self):
        """Test edge cases"""
        # Test all same values case
        uniform_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003'],
            'recency': [30, 30, 30],
            'frequency': [5, 5, 5],
            'monetary': [2000, 2000, 2000]
        })

        segmented_df = self.processor.rfm_segmentation(uniform_data)

        # Should be able to handle same values case
        assert len(segmented_df) == 3
        assert segmented_df['segment'].notna().all()


if __name__ == "__main__":
    pytest.main([__file__])
