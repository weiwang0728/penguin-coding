#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Specialized Test Script: fieldcategoryTypeDifferentFunctional Test

Direct interface with Data Preprocessing function, Testnumber valueType and ClassificationTypeField Type Recognitioncapability
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Add project path
project_root = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(project_root))

try:
 from credit_assessment.data import DataPreprocessor
 from credit_assessment.utils import ConfigManager

 def test_field_type_recognition():
 """TestfieldcategoryTypeDifferent function"""
 print("=== fieldcategoryTypeDifferentTest ===")

 # Initializepreprocessor
 config = ConfigManager()
 preprocessor = DataPreprocessor(config)

 # Load test data
 csv_file = Path(__file__).parent.parent / "test_data_csv.csv"

 if not csv_file.exists():
 print(f"Error: Test data file does not exist - {csv_file}")
 return False

 try:
 # GetData
 print(f"Load test data: {csv_file}")
 data = pd.read_csv(csv_file)

 print("\nfieldcategoryTypeDifferentresult: ")

 # Testnumber valueTypeField Type Recognition
 numeric_fields = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
 print(f"Differentnumber valueTypefield: {numeric_fields}")

 # VerifyPeriodnumber valueTypefield
 expected_numeric = ['age', 'income', 'employment_years', 'debt_ratio', 'target']
 recognized_numeric = set(numeric_fields)
 expected_numeric_set = set(expected_numeric)

 # TestClassificationTypeField Type Recognition
 categorical_fields = data.select_dtypes(include=['object']).columns.tolist()
 print(f"DifferentClassificationTypefield: {categorical_fields}")

 # VerifyPeriodClassificationTypefield
 expected_categorical = ['credit_history']
 recognized_categorical = set(categorical_fields)
 expected_categorical_set = set(expected_categorical)

 # VerifyDifferentStand ard Accurateness
 numeric_correct = len(expected_numeric_set.intersection(recognized_numeric))
 categorical_correct = len(expected_categorical_set.intersection(recognized_categorical))

 print(f"\nDifferentStand ard AccuratenessVerify: ")
 print(f"number valueTypefieldcorrectDifferent: {numeric_correct}/{len(expected_numeric_set)}")
 print(f"ClassificationTypefieldcorrectDifferent: {categorical_correct}/{len(expected_categorical_set)}")

 if numeric_correct >= len(expected_numeric_set) * 0.8:
 print("✓ number valueTypeField Type RecognitionStand ard Accurate")
 numeric_pass = True
 else:
 print("✗ number valueTypeField Type RecognitionNotStand ard Accurate")
 numeric_pass = False

 if categorical_correct >= len(expected_categorical_set) * 0.8:
 print("✓ ClassificationTypeField Type RecognitionStand ard Accurate")
 categorical_pass = True
 else:
 print("✗ ClassificationTypeField Type RecognitionNotStand ard Accurate")
 categorical_pass = False

 return numeric_pass and categorical_pass

 except Exception as e:
 print(f"✗ fieldcategoryTypeDifferent test failed: {str(e)}")
 return False

 # Execute test
 if __name__ == "__main__":
 success = test_field_type_recognition()
 sys.exit(0 if success else 1)

except ImportError as e:
 print(f"ModuleImportFailure: {str(e)}")
 sys.exit(1)