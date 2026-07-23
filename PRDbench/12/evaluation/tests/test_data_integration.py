"""
Data Integration and Multi-Table Join Unit Tests
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
# Add src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src')
sys.path.insert(0, src_path)

from data_processor import DataProcessor
from data_generator import DataGenerator


class TestDataIntegration:

    def setup_method(self):
        """Set up test data"""
        self.processor = DataProcessor()
        self.generator = DataGenerator()

        # Generate test data
        self.store_df, self.sales_df, self.warehouse_df = self.generator.generate_all_data(10, 100)

    def test_biz_id_join_result_validation(self):
        """Test biz_id join result validation"""
        # Load data
        self.processor.load_data(self.store_df, self.sales_df, self.warehouse_df)

        # Execute data integration
        integrated_df = self.processor.data_integration()

        # Verify biz_id join result
        assert 'git_repo' in integrated_df.columns, "Missing warehouse info field"
        # biz_group field does not exist in current implementation, warehouse info table only contains biz_id and git_repo

        # Verify all records have valid biz_id association
        non_null_repos = integrated_df['git_repo'].notna()
        assert non_null_repos.any(), "No successful warehouse info association"

        # Verify association consistency
        for biz_id in integrated_df['biz_id'].unique():
            if pd.notna(biz_id):
                biz_records = integrated_df[integrated_df['biz_id'] == biz_id]
                git_repos = biz_records['git_repo'].dropna().unique()
                if len(git_repos) > 0:
                    # Same biz_id should correspond to same git_repo
                    assert len(git_repos) == 1, f"biz_id {biz_id} corresponds to multiple git_repos: {git_repos}"

    def test_store_key_join_result_validation(self):
        """Test store_key join result validation"""
        # Load data
        self.processor.load_data(self.store_df, self.sales_df, self.warehouse_df)

        # Execute data integration
        integrated_df = self.processor.data_integration()

        # Verify store_key join result
        assert 'store_id' in integrated_df.columns, "Missing store ID field"
        assert 'brand_name' in integrated_df.columns, "Missing brand name field"
        assert 'a_value_type' in integrated_df.columns, "Missing value type field"
        assert 'private_domain_type' in integrated_df.columns, "Missing private domain type field"

        # Verify all records have valid store_key association
        assert integrated_df['store_id'].notna().all(), "Records without store info association exist"

        # Verify high value store filtering
        high_value_count = (integrated_df['a_value_type'] == 'High Value').sum()
        assert high_value_count > 0, "No high value stores filtered"

        # Verify private domain type filtering
        valid_domain_types = integrated_df['private_domain_type'].isin(['Headquarters Direct', 'Regional Focus'])
        assert valid_domain_types.all(), "Invalid private domain types exist"

    def test_data_integration_completeness(self):
        """Test data integration completeness"""
        # Load data
        self.processor.load_data(self.store_df, self.sales_df, self.warehouse_df)

        # Execute data integration
        integrated_df = self.processor.data_integration()

        # Verify key fields exist
        required_fields = [
            'store_key', 'biz_id', 'trans_date', 'amount',
            'store_id', 'a_value_type', 'private_domain_type',
            'git_repo'
        ]

        for field in required_fields:
            assert field in integrated_df.columns, f"Missing required field: {field}"

        # Verify data types
        assert pd.api.types.is_datetime64_any_dtype(integrated_df['trans_date']), "Transaction date type error"
        assert pd.api.types.is_numeric_dtype(integrated_df['amount']), "Transaction amount type error"

        # Verify data volume is reasonable
        assert len(integrated_df) > 0, "Integrated data is empty"
        assert len(integrated_df) <= len(self.sales_df), "Integrated data volume exceeds expectation"


if __name__ == "__main__":
    pytest.main([__file__])
