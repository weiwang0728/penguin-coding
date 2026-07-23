#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.2.1b Data Preprocessing - MissingFailvalue processingExecute

TestVerifyprocessingafterDatawhethercorrectimputationMissingFailvalue, DisplayprocessingresultSystemDesign.
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

class TestMissingvalueExecution:
 """MissingFailvalue processingExecute testcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.preprocessor = DataPreprocessor(self.config)

 # Prepare (Arrange): SelectChooseOneTypeimputationmethod(Averagevalue imputation)
 # CreateContainsMissingFailvalueTest data
 np.random.seed(42)
 n_samples = 100

 ages = np.random.normal(40, 15, n_samples)
 incomes = np.random.normal(50000, 20000, n_samples)
 scores = np.random.normal(650, 100, n_samples)

 # AddMissingFailvalue
 missing_indices_age = np.random.choice(n_samples, 15, replace=False)
 missing_indices_income = np.random.choice(n_samples, 10, replace=False)
 missing_indices_score = np.random.choice(n_samples, 8, replace=False)

 ages[missing_indices_age] = np.nan
 incomes[missing_indices_income] = np.nan
 scores[missing_indices_score] = np.nan

 self.test_data = pd.DataFrame({
 'age': ages,
 'income': incomes,
 'score': scores,
 'category': np.random.choice(['A', 'B', 'C'], n_samples),
 'target': np.random.choice([0, 1], n_samples)
 })

 # RecordNativeinitialMissingFailvalueSystemDesign
 self.original_missing_stats = {
 'age': self.test_data['age'].isnull().sum(),
 'income': self.test_data['income'].isnull().sum(),
 'score': self.test_data['score'].isnull().sum(),
 'total': self.test_data.isnull().sum().sum()
 }

 def test_missing_value_execution(self):
 """TestMissingFailvalue processingExecute"""
 # VerifyNativeinitialDataAccurateImplementationContainsMissingFailvalue
 assert self.original_missing_stats['total'] > 0, "NativeinitialDataShouldThisContainsMissingFailvalue"

 print(f"NativeinitialMissingFailvalueSystemDesign: {self.original_missing_stats}")

 # Execute (Act): ExecuteMissingFailvalue processingOperation
 processed_data = self.preprocessor.handle_missing_value s(
 self.test_data.copy(), strategy='mean'
 )

 # Break (Assert): VerifyprocessingafterDatawhethercorrectimputationMissingFailvalue, DisplayprocessingresultSystemDesign

 # 1. VerifyDatastructureProtectionSupportNotChange
 assert isinstance(processed_data, pd.DataFrame), "processingafterShouldThisReturnReturnDataFrame"
 assert len(processed_data) == len(self.test_data), "Data row countShouldThisProtectionSupportNotChange"
 assert len(processed_data.columns) == len(self.test_data.columns), "Data columnsnumberShouldThisProtectionSupportNotChange"

 # 2. Verifynumber value columnsMissingFailvalue correctimputation
 numeric_columns = self.test_data.select_dtypes(include=[np.number]).columns
 for col in numeric_columns:
 if col != 'target': # target columnsCommonConstantNotimputation
 original_missing = self.test_data[col].isnull().sum()
 processed_missing = processed_data[col].isnull().sum()

 if original_missing > 0:
 assert processed_missing == 0, f"{col} columnsMissingFailvalueShouldThisCompleteAutomaticimputation"

 # Verifyimputationvalue yesCombineProcessor(interfaceAveragevalue)
 original_mean = self.test_data[col].mean()
 filled_value s = processed_data.loc[self.test_data[col].isnull(), col]

 # imputationvalueShouldThisEqualAtorinterfaceNativeinitialDataAveragevalue
 for filled_val in filled_value s:
 assert abs(filled_val - original_mean) < 1e-10, f"{col} columnsimputationvalueShouldThisEqualAtAveragevalue"

 # 3. DisplayprocessingresultSystemDesign
 processed_missing_stats = {
 'age': processed_data['age'].isnull().sum(),
 'income': processed_data['income'].isnull().sum(),
 'score': processed_data['score'].isnull().sum(),
 'total': processed_data.isnull().sum().sum()
 }

 print(f"processingafterMissingFailvalueSystemDesign: {processed_missing_stats}")

 # 4. VerifyMissingFailvalue quantity
 assert processed_missing_stats['total'] < self.original_missing_stats['total'], "TotalMissingFailvalue quantityShouldThis"

 # 5. calculateDisplayprocessingEffectresult
 filled_count = self.original_missing_stats['total'] - processed_missing_stats['total']
 fill_rate = (filled_count / self.original_missing_stats['total']) * 100 if self.original_missing_stats['total'] > 0 else 0

 print(f"imputationSystemDesign: NativeinitialMissingFail{self.original_missing_stats['total']}items, imputation{filled_count}items, imputationRate{fill_rate:.1f}%")

 # 6. VerifyprocessingEffectresult meetPeriod
 assert fill_rate >= 80, f"number value columnsimputationRateShouldThis80%, Implementationinternational{fill_rate:.1f}%"

 print("MissingFailvalue processingExecute test Passed: processingafterDatacorrectimputationMissingFailvalue, processingresultSystemDesignmeetPeriod")

if __name__ == "__main__":
 py test.main([__file__])