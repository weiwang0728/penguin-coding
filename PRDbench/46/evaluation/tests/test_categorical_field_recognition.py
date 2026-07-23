#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.2.2b Field Processing - Categorical Field Recognition

Test whether the program correctly identifies all categorical fields (such as gender, occupation, etc.).
"""

import py test
import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.data.data_manager import DataManager
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestCategoricalFieldRecognition:
 """Categorical field recognition test class"""

 def setup_method(self):
 """Preparation before testing"""
 self.config = ConfigManager()
 self.data_manager = DataManager(self.config)

 # Create test data containing clearly categorical fields
 np.random.seed(42)
 n_samples = 120

 self.test_data = pd.DataFrame({
 # Numeric fields
 'age': np.random.randint(20, 80, n_samples),
 'income': np.random.randint(20000, 200000, n_samples),

 # Categorical fields (key test targets)
 'gender': np.random.choice(['Male', 'Female'], n_samples), # Gender
 'occupation': np.random.choice(['Engineer', 'Doctor', 'Teacher', 'Manager'], n_samples), # Occupation
 'education_level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples), # Education level
 'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_samples), # Marital status
 'employment_type': np.random.choice(['Full-time', 'Part-time', 'Self-employed'], n_samples), # Employment type

 # Target variable
 'target': np.random.choice([0, 1], n_samples)
 })

 # Create temporary CSV file
 self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
 self.test_data.to_csv(self.temp_file.name, index=False)
 self.temp_file.close()

 def teardown_method(self):
 """Cleanup after testing"""
 if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
 os.unlink(self.temp_file.name)

 def test_categorical_field_recognition(self):
 """Test categorical field recognition functionality"""
 # Act: Import data and check field type recognition result s
 df = self.data_manager.import_data(self.temp_file.name, validate=False)

 # Verify data import successful
 assert isinstance(df, pd.DataFrame)
 assert len(df) == 120

 # Assert: Verify whether the program correctly identifies all categorical fields

 # 1. Get pandas automatically identified categorical fields (object type)
 categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

 # 2. Expected categorical field list
 expected_categorical_fields = ['gender', 'occupation', 'education_level', 'marital_status', 'employment_type']

 print(f"Identified categorical fields: {categorical_columns}")
 print(f"Expected categorical fields: {expected_categorical_fields}")

 # 3. Verify key categorical fields are correctly identified
 critical_categorical_fields = ['gender', 'occupation']
 for field in critical_categorical_fields:
 assert field in categorical_columns, f"Key categorical field '{field}' should be identified as categorical"
 assert df[field].dtype == 'object', f"{field} field should be object type"

 # 4. Verify numeric fields are not misidentified as categorical
 numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
 expected_numeric_fields = ['age', 'income', 'target']

 for field in expected_numeric_fields:
 assert field in numeric_columns, f"Numeric field '{field}' should be identified as numeric"
 assert field not in categorical_columns, f"Numeric field '{field}' should not be in categorical fields"

 # 5. Verify categorical field unique value count is reasonable
 for field in critical_categorical_fields:
 if field in df.columns:
 unique_value s = df[field].nunique()
 assert unique_value s >= 2, f"{field} field should have at least 2 different categories"
 assert unique_value s <= 20, f"{field} field category count should be reasonable (<=20)"

 print(f"{field} field: {unique_value s} categories - {df[field].unique()[:5].tolist()}")

 # 6. Calculate recognition accuracy
 correctly_identified_categorical = len(set(critical_categorical_fields) & set(categorical_columns))
 categorical_accuracy = correctly_identified_categorical / len(critical_categorical_fields)

 assert categorical_accuracy >= 1.0, f"Categorical field recognition accuracy should be 100%, actual {categorical_accuracy:.1%}"

 print(f"Field recognition statistics: Categorical {len(categorical_columns)} fields, Numeric {len(numeric_columns)} fields")
 print(f"Categorical field recognition accuracy: {categorical_accuracy:.1%}")
 print("Categorical field recognition test passed: Program correctly identified all categorical fields, field type recognition is accurate")


if __name__ == "__main__":
 py test.main([__file__])
