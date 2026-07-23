"""
RFM Monetary Metric Calculation Unit Tests
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


class TestRFMMonetary:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()

        # Create test data
        dates = pd.date_range('2023-01-01', periods=30, freq='D')
        self.test_data = pd.DataFrame({
            'store_id': ['S001', 'S001', 'S001', 'S002', 'S002'],
            'trans_date': [dates[0], dates[15], dates[29], dates[5], dates[20]],
            'amount': [1000, 1500, 2000, 800, 1200]
        })

    def test_monetary_calculation_logic(self):
        """Test Monetary metric calculation logic"""
        # Calculate RFM metrics
        rfm_result = self.processor.calculate_rfm_metrics(self.test_data)

        # Verify results
        assert len(rfm_result) == 2  # Two stores
        assert 'monetary' in rfm_result.columns

        # Verify S001 store Monetary value
        s001_monetary = rfm_result[rfm_result['store_id'] == 'S001']['monetary'].iloc[0]
        # S001: Total amount 4500, time span 29 days about 1 month, monthly average should be about 4500
        assert s001_monetary > 4000

        # Verify S002 store Monetary value
        s002_monetary = rfm_result[rfm_result['store_id'] == 'S002']['monetary'].iloc[0]
        # S002: Total amount 2000, time span 15 days, but code has months minimum 1, so monthly average is 2000
        assert s002_monetary == 2000.0

    def test_monetary_with_single_transaction(self):
        """Test Monetary calculation for single transaction"""
        single_data = pd.DataFrame({
            'store_id': ['S003'],
            'trans_date': [datetime.now()],
            'amount': [1500]
        })

        rfm_result = self.processor.calculate_rfm_metrics(single_data)

        # Monthly average for single transaction should equal transaction amount
        assert rfm_result.iloc[0]['monetary'] == 1500

    def test_monetary_with_zero_amount(self):
        """Test handling of zero amount transactions"""
        zero_data = pd.DataFrame({
            'store_id': ['S004', 'S004'],
            'trans_date': [datetime.now(), datetime.now() - timedelta(days=1)],
            'amount': [0, 1000]
        })

        rfm_result = self.processor.calculate_rfm_metrics(zero_data)

        # Should be able to handle data with zero amounts
        assert len(rfm_result) == 1
        assert rfm_result.iloc[0]['monetary'] >= 0


if __name__ == "__main__":
    pytest.main([__file__])
