#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Specialized Test Script: MissingFailvalue processingExecuteFunctional Test

Direct interface with Data Preprocessing function, TestMissingFailvalue processingcapability
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

 def test_missing_value_processing():
 """TestMissingFailvalue processingExecute function"""
 print("=== MissingFailvalue processingExecute test ===")

 # Initializepreprocessor
 config = ConfigManager()
 preprocessor = DataPreprocessor(config)

 # LoadContainsMissingFailvalueTest data
 missing_file = Path(__file__).parent.parent / "test_data_missing.csv"

 if not missing_file.exists():
 print(f"Error: Test data file does not exist - {missing_file}")
 return False

 try:
 # GetData
 print(f"Load test data: {missing_file}")
 data = pd.read_csv(missing_file)

 print("NativeinitialDataMissingFailvalueSituation: ")
 missing_before = data.isnull().sum()
 for column, count in missing_before.items():
 if count > 0:
 print(f" - {column}: {count} itemsMissingFailvalue")

 # UseAveragevalue imputationOmitprocessingMissingFailvalue
 print("\nExecuteMissingFailvalue processing(Averagevalue imputation)...")
 processed_data = preprocessor.handle_missing_value s(data, strategy='mean')

 # Verifyprocessingresult
 missing_after = processed_data.isnull().sum()
 total_missing_after = missing_after.sum()

 print("\nprocessingresultSystemDesign: ")
 print(f"processingbeforeTotalMissingFailvalue: {missing_before.sum()}")
 print(f"processingafterTotalMissingFailvalue: {total_missing_after}")

 if total_missing_after == 0:
 print("✓ MissingFailvalue processingsuccess: PlaceHasMissingFailvalueAlreadycorrectimputation")
 print("✓ DisplayDetailedprocessingresultSystemDesign")
 return True
 else:
 print("✗ MissingFailvalue processingNotComplete: HasMissingFailvalueSavein")
 return False

 except Exception as e:
 print(f"✗ MissingFailvalue processing test failed: {str(e)}")
 return False

 # Execute test
 if __name__ == "__main__":
 success = test_missing_value_processing()
 sys.exit(0 if success else 1)

except ImportError as e:
 print(f"ModuleImportFailure: {str(e)}")
 sys.exit(1)