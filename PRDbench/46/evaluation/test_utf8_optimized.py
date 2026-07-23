#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Missing Values Detection Test under UTF-8 Environment
"""
import sys
import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# Add project path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from credit_assessment.data.data_manager import DataManager
from credit_assessment.utils.config_manager import ConfigManager


def test_missing_value s_detection():
 """Test missing value s detection function - UTF-8 optimized version"""
 # Create configuration and data manager
 config = ConfigManager()
 data_manager = DataManager(config)

 # Create test data
 np.random.seed(42)
 n_samples = 120

 ages = np.random.randint(20, 80, n_samples).astype(float)
 incomes = np.random.randint(20000, 200000, n_samples).astype(float)
 credit_scores = np.random.randint(300, 850, n_samples).astype(float)
 employment_years = np.random.randint(0, 40, n_samples).astype(float)
 targets = np.random.choice([0, 1], n_samples)

 # Add missing value s
 missing_age_indices = np.random.choice(n_samples, int(n_samples * 0.15), replace=False)
 missing_income_indices = np.random.choice(n_samples, int(n_samples * 0.12), replace=False)

 ages[missing_age_indices] = np.nan
 incomes[missing_income_indices] = np.nan

 test_data = pd.DataFrame({
 'age': ages,
 'income': incomes,
 'credit_score': credit_scores,
 'employment_years': employment_years,
 'target': targets
 })

 # Create temporary file
 temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
 test_data.to_csv(temp_file.name, index=False, encoding='utf-8')
 temp_file.close()

 try:
 # Import data
 df = data_manager.import_data(temp_file.name)

 # Verify result s
 assert isinstance(df, pd.DataFrame)
 assert len(df) == 120
 assert len(df.columns) == 5

 missing_count = df.isnull().sum()
 age_missing = missing_count['age']
 income_missing = missing_count['income']

 assert age_missing > 0
 assert income_missing > 0
 assert (missing_count > 0).sum() >= 2

 print(f"SUCCESS: Missing value s detected - age: {age_missing}, income: {income_missing}")

 finally:
 if os.path.exists(temp_file.name):
 os.unlink(temp_file.name)


if __name__ == "__main__":
 test_missing_value s_detection()
 print("Test completed successfully!")
