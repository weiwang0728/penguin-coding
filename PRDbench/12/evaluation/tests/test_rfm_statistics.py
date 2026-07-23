"""
RFM Segmentation Result Statistics Unit Tests
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
from display import DataDisplay


class TestRFMStatistics:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()
        self.display = DataDisplay()

        # Create complete test data with RFM and amount information
        self.test_data = pd.DataFrame({
            'store_id': ['S001', 'S002', 'S003', 'S004', 'S005', 'S006', 'S007', 'S008'],
            'recency': [5, 10, 60, 15, 45, 8, 30, 90],
            'frequency': [15, 12, 3, 10, 5, 18, 7, 2],
            'monetary': [8000, 6000, 1000, 5000, 2000, 9000, 3000, 800],
            'amount': [120000, 72000, 3000, 50000, 10000, 162000, 21000, 1600],  # Total transaction amount
            'segment': ['Important Value Customer', 'Important Value Customer', 'General New Customer', 'Important Retained Customer',
                       'General Development Customer', 'Important Value Customer', 'General Retained Customer', 'General New Customer']
        })

    def test_segment_count_percentage_calculation(self):
        """Test segmentation result count percentage calculation"""
        # Calculate segment statistics
        segment_stats = self.test_data.groupby('segment').agg({
            'store_id': 'count',
            'amount': 'sum'
        }).reset_index()
        segment_stats.columns = ['segment', 'store_count', 'total_amount']

        # Calculate percentage
        total_stores = len(self.test_data)
        segment_stats['percentage'] = (segment_stats['store_count'] / total_stores * 100).round(1)

        # Verify percentage calculation correctness
        assert abs(segment_stats['percentage'].sum() - 100.0) < 0.1, "Percentage sum should equal 100%"

        # Verify each segment type percentage
        for _, row in segment_stats.iterrows():
            expected_percentage = (row['store_count'] / total_stores) * 100
            assert abs(row['percentage'] - expected_percentage) < 0.1, f"Segment type {row['segment']} percentage calculation error"

        # Verify Important Value Customer percentage (3 stores, should be 37.5%)
        important_customers = segment_stats[segment_stats['segment'] == 'Important Value Customer']
        if len(important_customers) > 0:
            expected_percentage = 3 / 8 * 100  # 37.5%
            actual_percentage = important_customers.iloc[0]['percentage']
            assert abs(actual_percentage - expected_percentage) < 0.1, "Important Value Customer percentage calculation error"

    def test_transaction_amount_contribution_percentage(self):
        """Test segmentation result transaction amount contribution percentage"""
        # Calculate amount contribution percentage
        segment_stats = self.test_data.groupby('segment').agg({
            'store_id': 'count',
            'amount': 'sum'
        }).reset_index()
        segment_stats.columns = ['segment', 'store_count', 'total_amount']

        # Calculate amount contribution percentage
        total_amount = segment_stats['total_amount'].sum()
        segment_stats['amount_percentage'] = (segment_stats['total_amount'] / total_amount * 100).round(1)

        # Verify amount percentage sum is 100%
        assert abs(segment_stats['amount_percentage'].sum() - 100.0) < 0.1, "Amount percentage sum should equal 100%"

        # Verify Important Value Customers have highest amount contribution
        important_customers = segment_stats[segment_stats['segment'] == 'Important Value Customer']
        if len(important_customers) > 0:
            important_amount_pct = important_customers.iloc[0]['amount_percentage']
            max_amount_pct = segment_stats['amount_percentage'].max()
            assert important_amount_pct == max_amount_pct, "Important Value Customers should have highest amount contribution percentage"

        # Verify amount contribution percentage calculation correctness for each segment type
        for _, row in segment_stats.iterrows():
            expected_percentage = (row['total_amount'] / total_amount) * 100
            assert abs(row['amount_percentage'] - expected_percentage) < 0.1, f"Segment type {row['segment']} amount percentage calculation error"

    def test_segment_filtering_by_type(self):
        """Test filtering by segment type functionality"""
        # Test filtering Important Value Customers
        important_customers = self.test_data[self.test_data['segment'] == 'Important Value Customer']
        assert len(important_customers) == 3, "Important Value Customer count incorrect"

        # Verify filtering result data integrity
        assert important_customers['store_id'].notna().all(), "Filtering result contains null store IDs"
        assert important_customers['monetary'].notna().all(), "Filtering result contains null monthly average amounts"

        # Verify Important Value Customer characteristics
        avg_monetary = important_customers['monetary'].mean()
        overall_avg_monetary = self.test_data['monetary'].mean()
        assert avg_monetary > overall_avg_monetary, "Important Value Customers' average monthly amount should be higher than overall average"

        # Test filtering General New Customers
        new_customers = self.test_data[self.test_data['segment'] == 'General New Customer']
        assert len(new_customers) == 2, "General New Customer count incorrect"

        # Verify General New Customer characteristics
        avg_monetary_new = new_customers['monetary'].mean()
        assert avg_monetary_new < overall_avg_monetary, "General New Customers' average monthly amount should be lower than overall average"

    def test_comprehensive_segment_statistics(self):
        """Test comprehensive segment statistics"""
        # Create complete statistics
        segment_stats = self.test_data.groupby('segment').agg({
            'store_id': 'count',
            'amount': ['sum', 'mean'],
            'monetary': 'mean',
            'frequency': 'mean',
            'recency': 'mean'
        }).round(2)

        # Flatten column names
        segment_stats.columns = ['store_count', 'total_amount', 'avg_amount', 'avg_monetary', 'avg_frequency', 'avg_recency']
        segment_stats = segment_stats.reset_index()

        # Calculate percentages
        total_stores = len(self.test_data)
        total_amount = segment_stats['total_amount'].sum()
        segment_stats['store_percentage'] = (segment_stats['store_count'] / total_stores * 100).round(1)
        segment_stats['amount_percentage'] = (segment_stats['total_amount'] / total_amount * 100).round(1)

        # Verify statistics completeness
        assert len(segment_stats) > 0, "Statistics result is empty"
        assert segment_stats['store_count'].sum() == total_stores, "Store count statistics error"
        assert abs(segment_stats['store_percentage'].sum() - 100.0) < 0.1, "Store percentage sum error"
        assert abs(segment_stats['amount_percentage'].sum() - 100.0) < 0.1, "Amount percentage sum error"

        # Verify average value calculation reasonableness
        assert (segment_stats['avg_monetary'] > 0).all(), "Monthly average amount should be positive"
        assert (segment_stats['avg_frequency'] > 0).all(), "Average frequency should be positive"
        assert (segment_stats['avg_recency'] >= 0).all(), "Average days since last purchase should be non-negative"

    def test_segment_business_insights(self):
        """Test segmentation result business insights"""
        # Verify RFM segmentation business logic reasonableness
        segment_insights = self.test_data.groupby('segment').agg({
            'monetary': 'mean',
            'frequency': 'mean',
            'recency': 'mean'
        }).round(2)

        # Important Value Customers should have best RFM metrics
        if 'Important Value Customer' in segment_insights.index:
            important_customers = segment_insights.loc['Important Value Customer']

            # Compare with General New Customers
            if 'General New Customer' in segment_insights.index:
                new_customers = segment_insights.loc['General New Customer']

                # Important Value Customers should have higher monthly average amount and frequency, lower days since last purchase
                assert important_customers['monetary'] > new_customers['monetary'], "Important Value Customers' monthly average amount should be higher"
                assert important_customers['frequency'] > new_customers['frequency'], "Important Value Customers' transaction frequency should be higher"
                assert important_customers['recency'] < new_customers['recency'], "Important Value Customers' days since last purchase should be lower"


if __name__ == "__main__":
    pytest.main([__file__])
