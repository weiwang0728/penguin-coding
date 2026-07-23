import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_old.preprocessor import DataPreprocessor


class TestDataNormalizationEncoding:
    """Data normalization and encoding unit test"""

    def setup_method(self):
        """Setup before test"""
        self.preprocessor = DataPreprocessor()

    def create_raw_features_data(self):
        """Create raw data containing different types of features"""
        np.random.seed(42)

        data = {
            # Numerical features (5 fields)
            'age': np.random.randint(18, 80, 100),
            'income': np.random.normal(50000, 20000, 100),
            'price': np.random.uniform(10, 1000, 100),
            'rating': np.random.uniform(1, 5, 100),
            'quantity': np.random.poisson(5, 100),

            # Categorical features (3 fields)
            'gender': np.random.choice(['Male', 'Female', 'Other'], 100),
            'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books', 'Home'], 100),
            'brand': np.random.choice(['Huawei', 'Apple', 'Xiaomi', 'Samsung', 'OPPO'], 100),

            # Text features (2 fields)
            'title': [f"Product Title {i}" for i in range(100)],
            'description': [f"This is a detailed description of product {i}" for i in range(100)]
        }

        return pd.DataFrame(data)
    
    def test_data_normalization_encoding(self):
        """Test data normalization and encoding functions"""
        # Prepare test data
        df = self.create_raw_features_data()

        # Define feature types
        numerical_columns = ['age', 'income', 'price', 'rating', 'quantity']
        categorical_columns = ['gender', 'category', 'brand']
        text_columns = ['title', 'description']

        # Perform normalization
        normalized_df = self.preprocessor.normalize_numerical_features(df.copy(), numerical_columns)

        # Verify normalization results
        for col in numerical_columns:
            normalized_col = f'{col}_normalized'
            assert normalized_col in normalized_df.columns, f"Should create {normalized_col} column"

            # Verify normalized value range (StandardScaler: mean approximately 0, standard deviation approximately 1)
            normalized_values = normalized_df[normalized_col]
            assert abs(normalized_values.mean()) < 0.1, f"Mean of {normalized_col} should be close to 0"
            assert abs(normalized_values.std() - 1.0) < 0.1, f"Standard deviation of {normalized_col} should be close to 1"

        # Perform categorical encoding
        encoded_df = self.preprocessor.encode_categorical_features(normalized_df, categorical_columns)

        # Verify encoding results
        for col in categorical_columns:
            encoded_col = f'{col}_encoded'
            assert encoded_col in encoded_df.columns, f"Should create {encoded_col} column"

            # Verify encoded values are integers
            assert encoded_df[encoded_col].dtype in [np.int32, np.int64], f"{encoded_col} should be integer type"

            # Verify encoded value range is reasonable
            unique_original = df[col].nunique()
            unique_encoded = encoded_df[encoded_col].nunique()
            assert unique_encoded == unique_original, f"Number of unique values in {encoded_col} should be same as original column"

        # Perform text feature processing
        text_processed_df = self.preprocessor.process_text_features(encoded_df, text_columns)

        # Verify text processing results
        for col in text_columns:
            segmented_col = f'{col}_segmented'
            cleaned_col = f'{col}_cleaned'
            assert segmented_col in text_processed_df.columns, f"Should create {segmented_col} column"
            assert cleaned_col in text_processed_df.columns, f"Should create {cleaned_col} column"

    def test_feature_type_recognition(self):
        """Test automatic feature type recognition"""
        df = self.create_raw_features_data()

        # Identify numerical features
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        expected_numeric = ['age', 'income', 'price', 'rating', 'quantity']

        for feature in expected_numeric:
            assert feature in numeric_features, f"{feature} should be recognized as numerical feature"

        # Identify categorical features
        categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        expected_categorical = ['gender', 'category', 'brand', 'title', 'description']

        for feature in expected_categorical:
            assert feature in categorical_features, f"{feature} should be recognized as categorical feature"

        # Verify feature type recognition accuracy
        total_features = len(df.columns)
        correctly_identified = len(numeric_features) + len(categorical_features)
        accuracy = correctly_identified / total_features

        assert accuracy >= 0.9, f"Feature type recognition accuracy should be ≥90%, actual is {accuracy:.2%}"
    
    def test_normalization_methods(self):
        """Test different normalization methods"""
        # Create test data
        test_data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 100],  # Contains extreme values
            'feature2': [10, 20, 30, 40, 50, 60],  # Normal distribution
            'feature3': [-10, -5, 0, 5, 10, 15]  # Contains negative values
        })

        # Test StandardScaler normalization
        normalized_df = self.preprocessor.normalize_numerical_features(
            test_data.copy(), ['feature1', 'feature2', 'feature3']
        )

        for col in ['feature1', 'feature2', 'feature3']:
            normalized_col = f'{col}_normalized'
            values = normalized_df[normalized_col]

            # Verify statistical properties after standardization
            assert abs(values.mean()) < 0.1, f"Mean of {normalized_col} should be close to 0"
            assert abs(values.std() - 1.0) < 0.1, f"Standard deviation of {normalized_col} should be close to 1"

    def test_encoding_methods(self):
        """Test different encoding methods"""
        # Create test data
        test_data = pd.DataFrame({
            'low_cardinality': ['A', 'B', 'C', 'A', 'B', 'C'],  # Low cardinality
            'high_cardinality': [f'cat_{i}' for i in range(6)],  # High cardinality
            'ordinal_feature': ['Low', 'Medium', 'High', 'Low', 'Medium', 'High']  # Ordinal feature
        })

        # Test label encoding
        encoded_df = self.preprocessor.encode_categorical_features(
            test_data.copy(), ['low_cardinality', 'high_cardinality', 'ordinal_feature']
        )

        # Verify encoding results
        for col in ['low_cardinality', 'high_cardinality', 'ordinal_feature']:
            encoded_col = f'{col}_encoded'

            # Verify encoded value type and range
            assert encoded_df[encoded_col].dtype in [np.int32, np.int64], f"{encoded_col} should be integer type"
            assert encoded_df[encoded_col].min() >= 0, f"Minimum value of {encoded_col} should be ≥0"

            # Verify encoding consistency
            original_unique = test_data[col].nunique()
            encoded_unique = encoded_df[encoded_col].nunique()
            assert encoded_unique == original_unique, f"Number of unique values in {encoded_col} should remain consistent"
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Test empty dataframe
        empty_df = pd.DataFrame()

        result1 = self.preprocessor.normalize_numerical_features(empty_df, [])
        assert len(result1) == 0, "Empty dataframe normalization should return empty result"

        result2 = self.preprocessor.encode_categorical_features(empty_df, [])
        assert len(result2) == 0, "Empty dataframe encoding should return empty result"

        # Test column with only one unique value
        constant_df = pd.DataFrame({
            'constant_num': [5, 5, 5, 5, 5],
            'constant_cat': ['A', 'A', 'A', 'A', 'A']
        })

        # Normalization of constant numerical column
        normalized_constant = self.preprocessor.normalize_numerical_features(
            constant_df.copy(), ['constant_num']
        )
        # Column with standard deviation 0, after normalization should be all 0 or maintain original value
        assert 'constant_num_normalized' in normalized_constant.columns, "Should create normalization column"

        # Encoding of constant categorical column
        encoded_constant = self.preprocessor.encode_categorical_features(
            constant_df.copy(), ['constant_cat']
        )
        encoded_values = encoded_constant['constant_cat_encoded']
        assert encoded_values.nunique() == 1, "Constant categorical column encoding should have only one unique value"
        assert all(encoded_values == encoded_values.iloc[0]), "All values of constant categorical column encoding should be the same"

    def test_comprehensive_pipeline(self):
        """Test complete preprocessing pipeline"""
        # Create complex test data
        df = self.create_raw_features_data()

        # Add some missing values and outliers
        df.loc[0:4, 'age'] = np.nan
        df.loc[5, 'income'] = -50000  # Abnormal negative income
        df.loc[6, 'price'] = 10000   # Abnormal high price

        # Execute complete data cleaning and preprocessing
        processed_df = self.preprocessor.clean_data(df.copy())

        # Continue with feature engineering
        numerical_columns = ['age', 'income', 'price', 'rating', 'quantity']
        categorical_columns = ['gender', 'category', 'brand']
        text_columns = ['title', 'description']

        # Normalize numerical features
        processed_df = self.preprocessor.normalize_numerical_features(processed_df, numerical_columns)

        # Encode categorical features
        processed_df = self.preprocessor.encode_categorical_features(processed_df, categorical_columns)

        # Process text features
        processed_df = self.preprocessor.process_text_features(processed_df, text_columns)

        # Verify final results
        # 1. No missing values
        assert processed_df.isnull().sum().sum() == 0, "Should have no missing values after processing"

        # 2. Contains normalization columns
        for col in numerical_columns:
            assert f'{col}_normalized' in processed_df.columns, f"Should contain {col}_normalized column"

        # 3. Contains encoding columns
        for col in categorical_columns:
            assert f'{col}_encoded' in processed_df.columns, f"Should contain {col}_encoded column"

        # 4. Contains text processing columns
        for col in text_columns:
            assert f'{col}_segmented' in processed_df.columns, f"Should contain {col}_segmented column"
            assert f'{col}_cleaned' in processed_df.columns, f"Should contain {col}_cleaned column"

        # 5. Data integrity
        assert len(processed_df) == len(df), "Number of rows should remain unchanged after processing"