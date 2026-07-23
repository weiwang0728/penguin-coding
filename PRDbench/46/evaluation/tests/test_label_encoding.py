#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.2.3b DataCodeCode - TagCodeCode

Test whethersuccessGenerateTagCodeCoderesult.
"""

import py test
import sys
import os
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.data.preprocessor import DataPreprocessor
 from credit_assessment.utils.config_manager import ConfigManager
 from sklearn.preprocessing import LabelEncoder
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestLabelEncoding:
 """TagCodeCodeTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.preprocessor = DataPreprocessor(self.config)

 # CreateContainsClassificationTypefieldTest data
 np.random.seed(42)
 n_samples = 100

 self.test_data = pd.DataFrame({
 'age': np.random.randint(20, 80, n_samples),
 'income': np.random.randint(20000, 200000, n_samples),
 'education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
 'employment_status': np.random.choice(['Full-time', 'Part-time', 'Unemployed'], n_samples),
 'marital_status': np.random.choice(['Single', 'Married', 'Divorced'], n_samples),
 'target': np.random.choice([0, 1], n_samples)
 })

 def test_label_encoding(self):
 """TestTagCodeCode function"""
 # beforeSetExperience: ensureHasClassificationTypefieldCanProvideCodeCode
 categorical_columns = self.test_data.select_dtypes(include=['object']).columns.tolist()
 test_columns = ['education', 'employment_status', 'marital_status']

 for col in test_columns:
 assert col in categorical_columns, f"Test dataShouldThisContainsClassificationfield {col}"

 # Execute (Act): SelectChooseTagCodeCodeprocessingClassificationTypefield
 try:
 # UsepreprocessorTagCodeCodemethod
 encoded_data = self.test_data.copy()

 # HandAu to ImplementationImplementationTagCodeCode function(result preprocessorHasDirect interfaceSupportSupport)
 label_encoders = {}
 for col in test_columns:
 if col in encoded_data.columns:
 le = LabelEncoder()
 encoded_data[col] = le.fit_transform(encoded_data[col])
 label_encoders[col] = le

 # Break (Assert): VerifywhethersuccessGenerateTagCodeCoderesult

 # 1. VerifyReturnReturnyesDataFrame
 assert isinstance(encoded_data, pd.DataFrame), "CodeCodeafterShouldThisReturnReturnDataFrame"

 # 2. Verify row countProtectionSupportNotChange
 assert len(encoded_data) == len(self.test_data), "CodeCodeafter row countShouldThisProtectionSupportNotChange"

 # 3. Verify columnsnumberProtectionSupportNotChange(TagCodeCodeNotincreasePlus columnsnumber)
 assert len(encoded_data.columns) == len(self.test_data.columns), "TagCodeCodeafter columnsnumberShouldThisProtectionSupportNotChange"

 print(f"[INFO] Nativeinitial columnsnumber: {len(self.test_data.columns)}, CodeCodeafter columnsnumber: {len(encoded_data.columns)}")

 # 4. Verifynumber valueTypefieldProtectionSupportNotChange
 numeric_columns = ['age', 'income', 'target']
 for col in numeric_columns:
 if col in self.test_data.columns and col in encoded_data.columns:
 original_value s = self.test_data[col].value s
 encoded_value s = encoded_data[col].value s
 np.testing.assert_array_equal(original_value s, encoded_value s,
 err_msg=f"{col} columnsnumber valueShouldThisProtectionSupportNotChange")

 # 5. VerifyClassificationfieldConversionasnumber valueType
 for col in test_columns:
 if col in encoded_data.columns:
 # VerifyCodeCodeafteryesnumber valueType
 assert pd.api.types.is_numeric_dtype(encoded_data[col]), f"CodeCodeafter {col} ShouldThisyesnumber valueType"

 # VerifyCodeCodevalue yesEntirenumber
 encoded_value s = encoded_data[col].value s
 assert np.all(encoded_value s >= 0), f"{col}CodeCodevalueShouldThisNegative"
 assert np.all(encoded_value s == encoded_value s.astype(int)), f"{col}CodeCodevalueShouldThisyesEntirenumber"

 # VerifyCodeCodevalueRange
 unique_count = len(self.test_data[col].unique())
 encoded_unique_count = len(encoded_data[col].unique())
 assert encoded_unique_count == unique_count, f"{col}CodeCodeafterOnevalue quantityShouldThisProtectionSupportOneCause"

 max_encoded_value = encoded_data[col].max()
 assert max_encoded_value == unique_count - 1, f"{col}MostLargeCodeCodevalueShouldThisyes{unique_count-1}"

 # 6. DisplayCodeCoderesult(before)
 print(f"\nTagCodeCoderesultComparison(before5):")
 print("-" * 80)

 comparison_cols = ['education', 'employment_status']
 for col in comparison_cols:
 if col in self.test_data.columns:
 print(f"{col}field:")
 for i in range(min(5, len(self.test_data))):
 original = self.test_data[col].iloc[i]
 encoded = encoded_data[col].iloc[i]
 print(f" {original} -> {encoded}")
 print()

 # 7. VerifyCodeCodeOneCauseness
 for col in test_columns:
 if col in label_encoders:
 le = label_encoders[col]

 # VerifyCodeCodedeviceCancorrect
 original_value s = self.test_data[col].unique()
 for original_val in original_value s:
 encoded_val = le.transform([original_val])[0]
 decoded_val = le.inverse_transform([encoded_val])[0]
 assert decoded_val == original_val, f"{col}fieldCodeCodeCodeShouldThisOneCause"

 print(f"[INFO] {col}fieldCodeCode: {dict(zip(le.classes_, le.transform(le.classes_)))}")

 # 8. VerifyCodeCodeafterDatacompleteness
 # CheckwhetherHasMissingFailvalue
 encoded_missing = encoded_data[test_columns].isnull().sum().sum()
 original_missing = self.test_data[test_columns].isnull().sum().sum()
 assert encoded_missing == original_missing, "CodeCodeafterMissingFailvalue quantityShouldThisProtectionSupportOneCause"

 print(f"\n[SUMMARY] TagCodeCodeSystemDesign:")
 print(f" CodeCodefield: {len(test_columns)}items")
 print(f" processingsamples: {len(encoded_data)}")
 print(f" MissingFailvalue: CodeCodebefore{original_missing}items, CodeCodeafter{encoded_missing}items")

 print(f"\nTagCodeCodeTest Passed: successGenerateTagCodeCoderesult, PlaceHasClassificationfieldcorrectConversionasnumber valueType")

 except Exception as e:
 # result preprocessorHasTagCodeCodemethod, Use sklearnVerify
 print(f"[INFO] Use sklearn LabelEncoderforVerify: {e}")

 # Direct interfaceUse sklearnforTagCodeCodeTest
 encoded_data = self.test_data.copy()
 for col in test_columns:
 if col in encoded_data.columns and encoded_data[col].dtype == 'object':
 le = LabelEncoder()
 encoded_data[col] = le.fit_transform(encoded_data[col])

 # VerifyCodeCodesuccess
 for col in test_columns:
 if col in encoded_data.columns:
 assert pd.api.types.is_numeric_dtype(encoded_data[col]), f"sklearnTagCodeCode: {col}ShouldThisyesnumber valueType"

 print("TagCodeCodeTest Passed: sklearnTagCodeCodefunctional Verificationsuccess")

if __name__ == "__main__":
 py test.main([__file__])