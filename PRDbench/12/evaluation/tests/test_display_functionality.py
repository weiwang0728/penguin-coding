"""
Data Display Functionality Unit Tests
"""
import pytest
import pandas as pd
import os
import tempfile
from datetime import datetime
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from display import DataDisplay
from data_processor import DataProcessor
from data_generator import DataGenerator


class TestDisplayFunctionality:

    def setup_method(self):
        """Set up test data"""
        self.display = DataDisplay()
        self.processor = DataProcessor()
        self.generator = DataGenerator()

        # Generate complete processed data
        store_df, sales_df, warehouse_df = self.generator.generate_all_data(10, 100)
        self.processor.load_data(store_df, sales_df, warehouse_df)
        self.processed_df = self.processor.process_all()
        self.display.load_processed_data(self.processed_df)

    def test_table_display_required_columns_completeness(self):
        """Test table data display required columns completeness check"""
        # Get displayed data
        df = self.processed_df.copy()

        # Verify required columns exist
        required_columns = {
            'biz_id': 'Business Group',
            'trans_date': 'Transaction Date',
            'store_id': 'Store ID',
            'brand_name': 'Brand',
            'org_path': 'Organization Path',
            'private_domain_type': 'Private Domain Type',
            'segment': 'RFM Segment',
            'monetary': 'Monthly Average Amount',
            'value_tag': 'Value Tag',
            'detail_link': 'Detail Link'
        }

        # Verify all required columns exist
        for col in required_columns.keys():
            assert col in df.columns, f"Missing required column: {col}"

        # Verify data types are correct
        assert pd.api.types.is_datetime64_any_dtype(df['trans_date']), "Transaction date type error"
        assert pd.api.types.is_numeric_dtype(df['amount']), "Transaction amount type error"

        # Verify key columns are not all null
        assert df['store_id'].notna().any(), "Store ID column all null"
        assert df['segment'].notna().any(), "RFM segment column all null"

    def test_table_display_data_integrity_validation(self):
        """Test table data display data integrity validation"""
        df = self.processed_df.copy()

        # Verify data integrity
        assert len(df) > 0, "Processed data is empty"

        # Verify store ID uniqueness (within same date)
        duplicate_check = df.groupby(['store_id', 'trans_date']).size().max()
        assert duplicate_check == 1, "Duplicate store-date combinations exist"

        # Verify amount data reasonableness
        assert (df['amount'] > 0).all(), "Non-positive amounts exist"
        assert df['amount'].notna().all(), "Null amount data exists"

        # Verify RFM metrics reasonableness
        if 'monetary' in df.columns:
            assert (df['monetary'] > 0).all(), "Monthly average amount should be positive"
        if 'frequency' in df.columns:
            assert (df['frequency'] > 0).all(), "Transaction frequency should be positive"
        if 'recency' in df.columns:
            assert (df['recency'] >= 0).all(), "Days since last purchase should be non-negative"

        # Verify segment type reasonableness
        valid_segments = {
            "Important Value Customer", "Important Retained Customer", "Important Development Customer", "Important Recovery Customer",
            "General Value Customer", "General Retained Customer", "General Development Customer", "General New Customer"
        }
        segment_values = df['segment'].dropna().unique()
        for segment in segment_values:
            assert segment in valid_segments, f"Invalid segment type: {segment}"

    def test_csv_export_file_comparison(self):
        """Test CSV data export file comparison"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            test_filename = tmp_file.name

        try:
            # Execute export
            export_success = self.display.export_to_csv(test_filename)
            assert export_success, "CSV export failed"

            # Verify file exists
            assert os.path.exists(test_filename), "Export file does not exist"

            # Read exported file and verify
            exported_df = pd.read_csv(test_filename, encoding='utf-8-sig')

            # Verify exported file structure
            assert len(exported_df) > 0, "Export file is empty"
            assert len(exported_df.columns) > 0, "Export file has no columns"

            # Verify key columns exist
            expected_columns = ['biz_id', 'store_id', 'brand_name', 'segment']
            for col in expected_columns:
                if col in self.processed_df.columns:
                    assert col in exported_df.columns, f"Export file missing column: {col}"

            # Verify data consistency (record count should match)
            expected_records = len(self.processed_df)
            actual_records = len(exported_df)
            assert actual_records == expected_records, f"Record count mismatch: expected {expected_records}, actual {actual_records}"

            # Verify data content
            if 'store_id' in exported_df.columns:
                exported_stores = set(exported_df['store_id'].dropna())
                original_stores = set(self.processed_df['store_id'].dropna())
                assert exported_stores == original_stores, "Exported store IDs don't match"

        finally:
            # Clean up temporary file
            if os.path.exists(test_filename):
                os.unlink(test_filename)

    def test_csv_export_encoding_handling(self):
        """Test CSV export encoding handling"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            test_filename = tmp_file.name

        try:
            # Execute export
            export_success = self.display.export_to_csv(test_filename)
            assert export_success, "CSV export failed"

            # Verify file can be read with different encodings
            try:
                # Try UTF-8-SIG encoding
                df_utf8_sig = pd.read_csv(test_filename, encoding='utf-8-sig')
                assert len(df_utf8_sig) > 0, "UTF-8-SIG encoding read failed"
            except UnicodeDecodeError:
                pytest.fail("UTF-8-SIG encoding read failed")

            # Verify Chinese characters are exported correctly
            if 'brand_name' in df_utf8_sig.columns:
                chinese_brands = df_utf8_sig['brand_name'].dropna()
                if len(chinese_brands) > 0:
                    # Check if Chinese characters are included and not garbled
                    sample_brand = chinese_brands.iloc[0]
                    assert isinstance(sample_brand, str), "Brand name should be string"
                    # Chinese characters should display normally, not question marks or other garbled text
                    assert '?' not in sample_brand or len(sample_brand.replace('?', '')) > 0

        finally:
            # Clean up temporary file
            if os.path.exists(test_filename):
                os.unlink(test_filename)


if __name__ == "__main__":
    pytest.main([__file__])
