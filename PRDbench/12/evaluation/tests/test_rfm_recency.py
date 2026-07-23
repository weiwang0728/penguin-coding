"""
RFM Metric Calculation - Recency Calculation Unit Tests
Test the Recency (days since last purchase) calculation logic in the data processor
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processor import DataProcessor


class TestRFMRecencyCalculation:
    """RFM Recency Calculation Test Class"""

    def setup_method(self):
        """Pre-test setup"""
        self.processor = DataProcessor()

    def test_recency_calculation_basic(self):
        """Test basic Recency calculation functionality"""
        # Prepare test data
        current_date = datetime.now()

        # Create test data with different transaction dates
        test_data = {
            'store_id': ['S001', 'S001', 'S002', 'S002', 'S003'],
            'trans_date': [
                current_date - timedelta(days=30),  # 30 days ago
                current_date - timedelta(days=10),  # 10 days ago (most recent)
                current_date - timedelta(days=45),  # 45 days ago (most recent)
                current_date - timedelta(days=60),  # 60 days ago
                current_date - timedelta(days=5),   # 5 days ago (most recent)
            ],
            'amount': [100.0, 200.0, 150.0, 80.0, 300.0]
        }

        df = pd.DataFrame(test_data)

        # Execute RFM calculation
        rfm_result = self.processor.calculate_rfm_metrics(df)

        # Verify calculation results
        assert rfm_result is not None
        assert len(rfm_result) == 3  # 3 stores
        assert 'recency' in rfm_result.columns

        # Verify specific Recency values
        store_s001_recency = rfm_result[rfm_result['store_id'] == 'S001']['recency'].iloc[0]
        store_s002_recency = rfm_result[rfm_result['store_id'] == 'S002']['recency'].iloc[0]
        store_s003_recency = rfm_result[rfm_result['store_id'] == 'S003']['recency'].iloc[0]

        # S001's most recent transaction is 10 days ago
        assert abs(store_s001_recency - 10) <= 1  # Allow 1 day error

        # S002's most recent transaction is 45 days ago
        assert abs(store_s002_recency - 45) <= 1

        # S003's most recent transaction is 5 days ago
        assert abs(store_s003_recency - 5) <= 1

        print(f"[OK] Recency calculation test passed")
        print(f"  - Store S001 Recency: {store_s001_recency} days")
        print(f"  - Store S002 Recency: {store_s002_recency} days")
        print(f"  - Store S003 Recency: {store_s003_recency} days")

    def test_recency_calculation_edge_cases(self):
        """Test Recency calculation edge cases"""
        current_date = datetime.now()

        # Test only today's transactions
        test_data_today = {
            'store_id': ['S001', 'S001'],
            'trans_date': [current_date, current_date - timedelta(hours=2)],
            'amount': [100.0, 50.0]
        }

        df_today = pd.DataFrame(test_data_today)
        rfm_result_today = self.processor.calculate_rfm_metrics(df_today)

        # For today's transactions, Recency should be 0 or close to 0
        today_recency = rfm_result_today[rfm_result_today['store_id'] == 'S001']['recency'].iloc[0]
        assert today_recency <= 1  # At most 1 day

        print(f"[OK] Edge case test passed")
        print(f"  - Same day transaction Recency: {today_recency} days")

    def test_recency_data_types(self):
        """Test Recency calculation result data types"""
        current_date = datetime.now()

        test_data = {
            'store_id': ['S001'],
            'trans_date': [current_date - timedelta(days=15)],
            'amount': [100.0]
        }

        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)

        # Verify result data type
        assert isinstance(rfm_result, pd.DataFrame)
        assert 'recency' in rfm_result.columns
        assert pd.api.types.is_numeric_dtype(rfm_result['recency'])

        recency_value = rfm_result['recency'].iloc[0]
        # Check if it's numeric type (including numpy types)
        assert pd.api.types.is_numeric_dtype(type(recency_value)) or isinstance(recency_value, (int, float))
        assert float(recency_value) >= 0  # Recency should not be negative

        print(f"[OK] Data type test passed")
        print(f"  - Recency value type: {type(recency_value)}")
        print(f"  - Recency value: {recency_value}")


if __name__ == "__main__":
    # Can run this file directly for testing
    test_instance = TestRFMRecencyCalculation()
    test_instance.setup_method()

    try:
        test_instance.test_recency_calculation_basic()
        test_instance.test_recency_calculation_edge_cases()
        test_instance.test_recency_data_types()
        print("\n[SUCCESS] All RFM Recency calculation tests passed!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        raise
