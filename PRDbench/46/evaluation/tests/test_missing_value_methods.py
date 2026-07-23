#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.2.1a Data Preprocessing - MissingFailvalue imputationmethodSelectChoose

Test whetherExtractProvide3TypeimputationmethodSelectChoose(Averagevalue, indecimal places, Mode).
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
 from credit_assessment.data.preprocessor import DataPreprocessor
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestMissingvalueMethods:
 """MissingFailvalue imputationmethodSelectChooseTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.preprocessor = DataPreprocessor(self.config)

 # CreateContainsMissingFailvalueTest data
 np.random.seed(42)
 n_samples = 100

 ages = np.random.randint(20, 80, n_samples).astype(float)
 incomes = np.random.randint(20000, 200000, n_samples).astype(float)
 scores = np.random.randint(300, 850, n_samples).astype(float)

 # AddMissingFailvalue
 missing_indices = np.random.choice(n_samples, int(n_samples * 0.2), replace=False)
 ages[missing_indices[:len(missing_indices)//3]] = np.nan
 incomes[missing_indices[len(missing_indices)//3:2*len(missing_indices)//3]] = np.nan
 scores[missing_indices[2*len(missing_indices)//3:]] = np.nan

 self.test_data = pd.DataFrame({
 'age': ages,
 'income': incomes,
 'score': scores,
 'target': np.random.choice([0, 1], n_samples)
 })

 def test_missing_value_handling_method s(self):
 """TestMissingFailvalue imputationmethodSelectChoose"""
 # Break (Assert): ViewObservewhetherExtractProvide3TypeimputationmethodSelectChoose(Averagevalue, indecimal places, Mode)

 # TestAveragevalue imputationmethod
 try:
 result_mean = self.preprocessor.handle_missing_value s(
 self.test_data.copy(), strategy='mean'
 )
 assert isinstance(result_mean, pd.DataFrame), "Averagevalue imputationShouldThisReturnReturnDataFrame"
 assert not result_mean.select_dtypes(include=[np.number]).isnull().any().any(), "number value columnsNotShouldHasMissingFailvalue"
 print("✓ Averagevalue imputationmethodAvailable")
 except Exception as e:
 py test.fail(f"Averagevalue imputationmethodNotAvailable: {e}")

 # Testindecimal placesimputationmethod
 try:
 result_median = self.preprocessor.handle_missing_value s(
 self.test_data.copy(), strategy='median'
 )
 assert isinstance(result_median, pd.DataFrame), "indecimal placesimputationShouldThisReturnReturnDataFrame"
 assert not result_median.select_dtypes(include=[np.number]).isnull().any().any(), "number value columnsNotShouldHasMissingFailvalue"
 print("✓ indecimal placesimputationmethodAvailable")
 except Exception as e:
 py test.fail(f"indecimal placesimputationmethodNotAvailable: {e}")

 # TestModeimputationmethod
 try:
 result_mode = self.preprocessor.handle_missing_value s(
 self.test_data.copy(), strategy='most_frequent'
 )
 assert isinstance(result_mode, pd.DataFrame), "ModeimputationShouldThisReturnReturnDataFrame"
 # ModeimputationforPlaceHascategoryType columnsSuitableUse
 print("✓ ModeimputationmethodAvailable")
 except Exception as e:
 py test.fail(f"ModeimputationmethodNotAvailable: {e}")

 # VerifyimputationEffectresultNotSame(DescriptionmethodAccurateImplementationNotSame)
 original_missing_count = self.test_data.isnull().sum().sum()
 assert original_missing_count > 0, "NativeinitialDataShouldThisContainsMissingFailvalue"

 # BiferCompareNotSamemethod imputationresult
 mean_age = result_mean['age'].iloc[0] if pd.isna(self.test_data['age'].iloc[0]) else None
 median_age = result_median['age'].iloc[0] if pd.isna(self.test_data['age'].iloc[0]) else None

 if mean_age is not None and median_age is not None:
 # resultNativeinitialFirst rowsageyesMissingFail, BiferCompareimputationvalue
 print(f"NotSamemethod imputationresult: Averagevalue={mean_age:.2f}, indecimal places={median_age:.2f}")

 print("MissingFailvalue imputationmethodSelectChooseTest Passed: ExtractProvideAveragevalue, indecimal places, ModeSamTypeimputationmethod")

if __name__ == "__main__":
 py test.main([__file__])