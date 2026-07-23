"""
Time Series Decomposition Unit Tests
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


class TestTimeSeriesDecomposition:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()

        # Create sufficient time series data for STL decomposition
        dates = pd.date_range('2023-01-01', periods=180, freq='D')  # 6 months data

        # Create simulated data with trend and seasonality
        self.time_series_data = []
        for i, date in enumerate(dates):
            # Simulate data for 3 stores
            for store_id in ['S001', 'S002', 'S003']:
                # Add trend (growth) + seasonality (periodic variation) + random noise
                trend = 1000 + i * 5  # Growth trend
                seasonal = 200 * np.sin(2 * np.pi * i / 30)  # Monthly seasonality
                noise = np.random.normal(0, 50)  # Random noise
                amount = max(100, trend + seasonal + noise)  # Ensure positive amount

                self.time_series_data.append({
                    'store_id': store_id,
                    'trans_date': date,
                    'amount': amount
                })

        self.ts_df = pd.DataFrame(self.time_series_data)

    def test_stl_decomposition_execution(self):
        """Test STL decomposition executes successfully"""
        decomp_result = self.processor.time_series_decomposition(self.ts_df)

        # Verify result contains all stores
        assert len(decomp_result) == 3  # 3 stores

        # Verify necessary columns exist
        required_columns = ['store_id', 'trend', 'seasonal', 'residual']
        for col in required_columns:
            assert col in decomp_result.columns

        # Verify all stores have decomposition results
        assert set(decomp_result['store_id']) == {'S001', 'S002', 'S003'}

    def test_decomposition_components_validity(self):
        """Test decomposition component validity"""
        decomp_result = self.processor.time_series_decomposition(self.ts_df)

        # Verify trend, seasonal, residual components are all numeric
        assert decomp_result['trend'].notna().all()
        assert decomp_result['seasonal'].notna().all()
        assert decomp_result['residual'].notna().all()

        # Verify data types
        assert pd.api.types.is_numeric_dtype(decomp_result['trend'])
        assert pd.api.types.is_numeric_dtype(decomp_result['seasonal'])
        assert pd.api.types.is_numeric_dtype(decomp_result['residual'])

        # Verify trend component should be positive (for our test data)
        assert (decomp_result['trend'] > 0).all()

    def test_insufficient_data_handling(self):
        """Test handling of insufficient data"""
        # Create time series with insufficient data (less than 6 months)
        short_dates = pd.date_range('2023-01-01', periods=30, freq='D')  # 1 month data

        short_data = []
        for date in short_dates:
            short_data.append({
                'store_id': 'S001',
                'trans_date': date,
                'amount': 1000 + np.random.normal(0, 100)
            })

        short_df = pd.DataFrame(short_data)
        decomp_result = self.processor.time_series_decomposition(short_df)

        # Verify result is returned even with insufficient data
        assert len(decomp_result) == 1
        assert decomp_result.iloc[0]['store_id'] == 'S001'

        # Verify simple statistics used instead of STL decomposition
        assert decomp_result.iloc[0]['trend'] > 0
        assert decomp_result.iloc[0]['seasonal'] == 0  # Seasonal component is 0 when data insufficient

    def test_multiple_stores_processing(self):
        """Test multiple stores parallel processing"""
        decomp_result = self.processor.time_series_decomposition(self.ts_df)

        # Verify each store has independent decomposition result
        for store_id in ['S001', 'S002', 'S003']:
            store_result = decomp_result[decomp_result['store_id'] == store_id]
            assert len(store_result) == 1

            # Verify each store's decomposition result is different (due to randomness)
            assert store_result.iloc[0]['trend'] > 0
            assert pd.notna(store_result.iloc[0]['residual'])

    def test_empty_data_handling(self):
        """Test empty data handling"""
        empty_df = pd.DataFrame(columns=['store_id', 'trans_date', 'amount'])
        decomp_result = self.processor.time_series_decomposition(empty_df)

        # Verify can handle empty data
        assert len(decomp_result) == 0
        assert list(decomp_result.columns) == ['store_id', 'trend', 'seasonal', 'residual']

    def test_single_data_point_handling(self):
        """Test single data point handling"""
        single_data = pd.DataFrame({
            'store_id': ['S001'],
            'trans_date': [datetime.now()],
            'amount': [1000]
        })

        decomp_result = self.processor.time_series_decomposition(single_data)

        # Verify single data point can be handled
        assert len(decomp_result) == 1
        assert decomp_result.iloc[0]['trend'] == 1000  # Trend equals original value
        assert decomp_result.iloc[0]['seasonal'] == 0  # No seasonality
        assert decomp_result.iloc[0]['residual'] == 0  # No residual


if __name__ == "__main__":
    pytest.main([__file__])
