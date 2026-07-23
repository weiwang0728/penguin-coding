#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.1.2a Data Validation - MissingFailvalueCheckTest (UseAutomaticConfigManager)
"""

import py test
import sys
import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# ImportAutomaticConfigureManager
from pytest_safe_config import patch_config_manager

# ShouldUseAutomaticConfigure
SafeConfigManager = patch_config_manager()

# Add project path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

# ImplementationinAutomaticImportDataManager(ConfigManagerAlreadyChange)
from credit_assessment.data.data_manager import DataManager

class TestMissingvalue sDetectionSafe:
 """MissingFailvalueCheck Test Testcategory(UseAutomaticConfigManager)"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = SafeConfigManager()
 self.data_manager = DataManager(self.config)

 # CreateContainsMissingFailvalueTest data
 np.random.seed(42)
 n_samples = 120

 ages = np.random.randint(20, 80, n_samples).astype(float)
 incomes = np.random.randint(20000, 200000, n_samples).astype(float)
 credit_scores = np.random.randint(300, 850, n_samples).astype(float)
 employment_years = np.random.randint(0, 40, n_samples).astype(float)
 targets = np.random.choice([0, 1], n_samples)

 # inageand incomefieldin AddMissingFailvalue
 missing_age_indices = np.random.choice(n_samples, int(n_samples * 0.15), replace=False)
 missing_income_indices = np.random.choice(n_samples, int(n_samples * 0.12), replace=False)

 ages[missing_age_indices] = np.nan
 incomes[missing_income_indices] = np.nan

 self.test_data = pd.DataFrame({
 'age': ages,
 'income': incomes,
 'credit_score': credit_scores,
 'employment_years': employment_years,
 'target': targets
 })

 # CreateTimeCSVFile
 self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
 self.test_data.to_csv(self.temp_file.name, index=False, encoding='utf-8')
 self.temp_file.close()

 def teardown_method(self):
 """TestafterCleanProcessor"""
 if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
 os.unlink(self.temp_file.name)

 def test_missing_value s_detection(self):
 """TestMissingFailvalueCheckTest function"""
 # ImportTest file
 df = self.data_manager.import_data(self.temp_file.name)

 # VerifyData import success
 assert isinstance(df, pd.DataFrame)
 assert len(df) == 120
 assert len(df.columns) == 5

 # VerifyMissingFailvalueCheckTest
 missing_count = df.isnull().sum()
 age_missing = missing_count['age']
 income_missing = missing_count['income']

 assert age_missing > 0, f"agefieldShouldThisHasMissingFailvalue, Implementationinternational: {age_missing}"
 assert income_missing > 0, f"incomefieldShouldThisHasMissingFailvalue, Implementationinternational: {income_missing}"

 # Verifyat least 2fieldHasMissingFailvalue
 fields_with_missing = (missing_count > 0).sum()
 assert fields_with_missing >= 2, f"at least 2fieldShouldThisHasMissingFailvalue, Implementationinternational: {fields_with_missing}"

 print(f"✓ MissingFailvalueCheck Test Test Passed: ageMissingFail{age_missing}items, incomeMissingFail{income_missing}items")

if __name__ == "__main__":
 py test.main([__file__, "-v"])