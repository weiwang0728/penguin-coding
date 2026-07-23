"""
RFM Metric Calculation - Frequency Calculation Unit Tests
Test the Frequency (monthly average transaction count) calculation logic in the data processor
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processor import DataProcessor


class TestRFMFrequencyCalculation:
    """RFM Frequency Calculation Test Class"""

    def setup_method(self):
        """Pre-test setup"""
        self.processor = DataProcessor()

    def test_frequency_calculation_basic(self):
        """Test basic Frequency calculation functionality"""
        # Prepare test data
        current_date = datetime.now()

        # Create test data with different transaction frequencies
        test_data = {
            'store_id': ['S001', 'S001', 'S001', 'S002', 'S002', 'S003'],
            'trans_date': [
                current_date - timedelta(days=90),  # S001: 3 months ago
                current_date - timedelta(days=60),  # S001: 2 months ago
                current_date - timedelta(days=30),  # S001: 1 month ago (3 transactions in 3 months)
                current_date - timedelta(days=60),  # S002: 2 months ago
                current_date - timedelta(days=30),  # S002: 1 month ago (2 transactions in 2 months)
                current_date - timedelta(days=15),  # S003: 15 days ago (1 transaction)
            ],
            'amount': [100.0, 200.0, 150.0, 120.0, 180.0, 300.0]
        }

        df = pd.DataFrame(test_data)

        # Execute RFM calculation
        rfm_result = self.processor.calculate_rfm_metrics(df)

        # Verify calculation results
        assert rfm_result is not None
        assert len(rfm_result) == 3  # 3 stores
        assert 'frequency' in rfm_result.columns

        # Verify specific Frequency values
        store_s001_freq = rfm_result[rfm_result['store_id'] == 'S001']['frequency'].iloc[0]
        store_s002_freq = rfm_result[rfm_result['store_id'] == 'S002']['frequency'].iloc[0]
        store_s003_freq = rfm_result[rfm_result['store_id'] == 'S003']['frequency'].iloc[0]

        # S001: 3 transactions, time span 90-30=60 days=2 months, frequency=3/2=1.5 times/month
        assert 1.4 <= store_s001_freq <= 1.6  # Allow reasonable error

        # S002: 2 transactions, time span 60-30=30 days=1 month, frequency=2/1=2 times/month
        assert 1.8 <= store_s002_freq <= 2.2

        # S003: 1 transaction, minimum calculated as 1 month, frequency=1/1=1 time/month
        assert 0.9 <= store_s003_freq <= 1.1

        print(f"[OK] Frequency calculation test passed")
        print(f"  - Store S001 Frequency: {store_s001_freq:.2f} times/month")
        print(f"  - Store S002 Frequency: {store_s002_freq:.2f} times/month")
        print(f"  - Store S003 Frequency: {store_s003_freq:.2f} times/month")

    def test_frequency_calculation_single_transaction(self):
        """Test Frequency calculation for single transaction"""
        current_date = datetime.now()

        # Store with only one transaction
        test_data = {
            'store_id': ['S001'],
            'trans_date': [current_date - timedelta(days=15)],
            'amount': [100.0]
        }

        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)

        # For single transaction store, frequency should be 1.0 (calculated as minimum 1 month)
        frequency_value = rfm_result[rfm_result['store_id'] == 'S001']['frequency'].iloc[0]
        assert frequency_value == 1.0

        print(f"[OK] Single transaction test passed")
        print(f"  - Single transaction Frequency: {frequency_value} times/month")

    def test_frequency_calculation_high_frequency(self):
        """Test Frequency calculation for high frequency transactions"""
        current_date = datetime.now()

        # Create high frequency transaction data (10 transactions in 2 months)
        test_data = {
            'store_id': ['S001'] * 10,
            'trans_date': [
                current_date - timedelta(days=60),
                current_date - timedelta(days=55),
                current_date - timedelta(days=50),
                current_date - timedelta(days=45),
                current_date - timedelta(days=40),
                current_date - timedelta(days=35),
                current_date - timedelta(days=30),
                current_date - timedelta(days=25),
                current_date - timedelta(days=20),
                current_date - timedelta(days=15),
            ],
            'amount': [100.0] * 10
        }

        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)

        frequency_value = rfm_result[rfm_result['store_id'] == 'S001']['frequency'].iloc[0]

        # 10 transactions in about 1.5 months, monthly average should be about 6-7 times
        assert 4.0 <= frequency_value <= 8.0

        print(f"[OK] High frequency transaction test passed")
        print(f"  - High frequency transaction Frequency: {frequency_value:.2f} times/month")

    def test_frequency_data_types(self):
        """Test Frequency calculation result data types"""
        current_date = datetime.now()

        test_data = {
            'store_id': ['S001', 'S001'],
            'trans_date': [
                current_date - timedelta(days=30),
                current_date - timedelta(days=15)
            ],
            'amount': [100.0, 200.0]
        }

        df = pd.DataFrame(test_data)
        rfm_result = self.processor.calculate_rfm_metrics(df)

        # Verify result data type
        assert isinstance(rfm_result, pd.DataFrame)
        assert 'frequency' in rfm_result.columns
        assert pd.api.types.is_numeric_dtype(rfm_result['frequency'])

        frequency_value = rfm_result['frequency'].iloc[0]
        # Check if it's numeric type
        assert pd.api.types.is_numeric_dtype(type(frequency_value)) or isinstance(frequency_value, (int, float))
        assert float(frequency_value) > 0  # Frequency should be positive

        print(f"[OK] Data type test passed")
        print(f"  - Frequency value type: {type(frequency_value)}")
        print(f"  - Frequency value: {frequency_value:.2f}")


if __name__ == "__main__":
    # Can run this file directly for testing
    test_instance = TestRFMFrequencyCalculation()
    test_instance.setup_method()

    try:
        test_instance.test_frequency_calculation_basic()
        test_instance.test_frequency_calculation_single_transaction()
        test_instance.test_frequency_calculation_high_frequency()
        test_instance.test_frequency_data_types()
        print("\n[SUCCESS] All RFM Frequency calculation tests passed!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        raise
