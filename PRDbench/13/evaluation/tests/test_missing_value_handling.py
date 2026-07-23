import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data.preprocessor import DataPreprocessor


class TestMissingValueHandling:
    """Missing value handling unit tests"""

    def setup_method(self):
        """Test setup"""
        self.preprocessor = DataPreprocessor()
        
    def create_data_with_missing_values(self):
        """Create test data with missing values"""
        np.random.seed(42)

        # Create base data
        data = {
            'user_id': range(1, 101),
            'age': np.random.normal(30, 10, 100),
            'income': np.random.normal(50000, 15000, 100),
            'rating': np.random.uniform(1, 5, 100),
            'category': ['electronics', 'clothing', 'food', 'books', 'home'] * 20,
            'description': ['Product description' + str(i) for i in range(100)]
        }

        df = pd.DataFrame(data)

        # Insert different proportions of missing values
        # 10% missing rate
        missing_10_indices = np.random.choice(df.index, size=10, replace=False)
        df.loc[missing_10_indices, 'age'] = np.nan

        # 30% missing rate
        missing_30_indices = np.random.choice(df.index, size=30, replace=False)
        df.loc[missing_30_indices, 'income'] = np.nan

        # 50% missing rate
        missing_50_indices = np.random.choice(df.index, size=50, replace=False)
        df.loc[missing_50_indices, 'category'] = np.nan

        # Few missing values
        df.loc[0:4, 'rating'] = np.nan
        df.loc[95:99, 'description'] = np.nan

        return df
    
    def test_missing_value_handling(self):
        """Test missing value handling function"""
        # Prepare test data
        df = self.create_data_with_missing_values()

        # Record missing value statistics before processing
        missing_before = df.isnull().sum()

        # Execute data cleaning (includes missing value handling)
        cleaned_df = self.preprocessor.clean_data(df.copy())

        # Record missing value statistics after processing
        missing_after = cleaned_df.isnull().sum()

        # Assertion: all missing values should be handled
        assert missing_after.sum() == 0, "There should be no missing values after processing"

        # Verify numeric columns use mean filling
        original_age_mean = df['age'].mean()
        filled_age_values = cleaned_df.loc[df['age'].isnull(), 'age']
        assert all(abs(val - original_age_mean) < 0.001 for val in filled_age_values), "Numeric missing values should be filled with mean"

        # Verify categorical columns use mode filling
        original_category_mode = df['category'].mode()[0]
        filled_category_values = cleaned_df.loc[df['category'].isnull(), 'category']
        assert all(val == original_category_mode for val in filled_category_values), "Categorical missing values should be filled with mode"

        # Verify data integrity
        assert len(cleaned_df) == len(df), "Missing value handling should not delete data rows"
        assert cleaned_df.columns.equals(df.columns), "Missing value handling should not change column structure"
    
    def test_missing_value_strategies(self):
        """Test different missing value handling strategies"""
        # Create test data
        df = pd.DataFrame({
            'numeric_col': [1, 2, np.nan, 4, 5, np.nan, 7, 8, 9, 10],
            'categorical_col': ['A', 'B', np.nan, 'A', 'A', np.nan, 'C', 'A', 'B', 'A']
        })

        # Handle missing values
        result_df = self.preprocessor.clean_data(df.copy())

        # Verify numeric column: mean filling
        expected_mean = df['numeric_col'].mean()  # (1+2+4+5+7+8+9+10)/8 = 5.75
        filled_values = result_df.loc[df['numeric_col'].isnull(), 'numeric_col']
        assert all(abs(val - expected_mean) < 0.001 for val in filled_values), f"Numeric column should be filled with mean {expected_mean}"

        # Verify categorical column: mode filling ('A' appears most)
        expected_mode = 'A'
        filled_values = result_df.loc[df['categorical_col'].isnull(), 'categorical_col']
        assert all(val == expected_mode for val in filled_values), f"Categorical column should be filled with mode {expected_mode}"
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Test empty dataframe
        empty_df = pd.DataFrame()
        result = self.preprocessor.clean_data(empty_df)
        assert len(result) == 0, "Empty dataframe should return empty result"

        # Test column with all missing values
        all_missing_df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'all_missing': [np.nan, np.nan, np.nan]
        })
        result = self.preprocessor.clean_data(all_missing_df)
        # Categorical column with all missing should be filled with 'unknown'
        assert all(result['all_missing'] == 'unknown'), "Categorical column with all missing should be filled with 'unknown'"

        # Test data with no missing values
        no_missing_df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        result = self.preprocessor.clean_data(no_missing_df)
        pd.testing.assert_frame_equal(result, no_missing_df, check_dtype=False), "Data with no missing values should not be modified"
    
    def test_missing_value_statistics(self):
        """Test missing value statistics"""
        df = self.create_data_with_missing_values()

        # Count missing values before processing
        missing_stats_before = {
            'age': df['age'].isnull().sum(),
            'income': df['income'].isnull().sum(),
            'category': df['category'].isnull().sum(),
            'rating': df['rating'].isnull().sum(),
            'description': df['description'].isnull().sum()
        }

        # Verify the missing value proportions we created are correct
        assert missing_stats_before['age'] == 10, "age column should have 10 missing values (10%)"
        assert missing_stats_before['income'] == 30, "income column should have 30 missing values (30%)"
        assert missing_stats_before['category'] == 50, "category column should have 50 missing values (50%)"
        assert missing_stats_before['rating'] == 5, "rating column should have 5 missing values"
        assert missing_stats_before['description'] == 5, "description column should have 5 missing values"

        # Handle missing values
        cleaned_df = self.preprocessor.clean_data(df)

        # Verify all missing values are handled
        missing_stats_after = cleaned_df.isnull().sum()
        assert missing_stats_after.sum() == 0, "All columns should have no missing values after processing"