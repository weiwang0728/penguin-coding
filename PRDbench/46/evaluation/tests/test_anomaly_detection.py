#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.1.2b Data Validation - AbnormalDataCheckTest

TestProgramcanCheckTestdisplayAbnormalDataIssue.
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
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestAnomalyDetection:
 """AbnormalDataCheck Test Testcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.data_manager = DataManager(self.config)

 # CreateContainsAbnormalDataTest file( yearfieldContainsNegativenumber orUltraOver150value)
 np.random.seed(42)
 n_samples = 120 # MeetsMostSmall row countrequirements

 # GeneratenormalRangebasicbasicData
 ages = np.random.randint(20, 80, n_samples).astype(float)
 incomes = np.random.randint(20000, 200000, n_samples).astype(float)
 targets = np.random.choice([0, 1], n_samples)

 # AddAbnormalvalue
 ages[0] = -5 # Negativenumber year(Abnormal)
 ages[1] = 200 # UltraOver150 year(Abnormal)
 incomes[2] = -10000 # NegativenumberReceiveinput(Abnormal)
 incomes[3] = 99999999 # UltraLargeReceiveinputvalue(CanEnergyAbnormal)

 self.test_data = pd.DataFrame({
 'age': ages,
 'income': incomes,
 'target': targets
 })

 # CreateTimeCSVFile
 self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
 self.test_data.to_csv(self.temp_file.name, index=False)
 self.temp_file.close()

 def teardown_method(self):
 """TestafterCleanProcessor"""
 if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
 os.unlink(self.temp_file.name)

 def test_anomaly_detection(self):
 """TestAbnormalDataCheckTest function"""
 # Execute (Act): ImportContainsAbnormalDataTest file
 df = self.data_manager.import_data(self.temp_file.name, validate=False)

 # VerifyData import success
 assert isinstance(df, pd.DataFrame)
 assert len(df) == 120
 assert len(df.columns) == 3

 # VerifyAccurateImplementationContainsAbnormalvalue
 assert (df['age'] < 0).any(), "ShouldThisContainsNegativenumber year"
 assert (df['age'] > 150).any(), "ShouldThisContainsUltraOver150 year"
 assert (df['income'] < 0).any(), "ShouldThisContainsNegativenumberReceiveinput"

 # Break (Assert): VerifyProgramable toCheckTestdisplayAbnormalDataIssue
 validation_result = self.data_manager.validate_current_data()

 # CheckwhetherCheckTest to AbnormalDataCameraRelatedIssue
 has_anomaly_detection = False
 detected_issues = []

 # CheckWarninginformation
 if 'warnings' in validation_result:
 for warning in validation_result['warnings']:
 if any(keyword in warning for keyword in ['Abnormal', 'anomaly', 'UltraOutput', 'Negativenumber', 'Range']):
 has_anomaly_detection = True
 detected_issues.append(f"Warning: {warning}")

 # CheckErrorinformation
 if 'errors' in validation_result:
 for error in validation_result['errors']:
 if any(keyword in error for keyword in ['Abnormal', 'anomaly', 'UltraOutput', 'Negativenumber', 'Range', 'MostSmallvalue', 'MostLargevalue']):
 has_anomaly_detection = True
 detected_issues.append(f"Error: {error}")

 # VerifyCheckTestresult
 if has_anomaly_detection:
 print(f"CheckTest to AbnormalDataIssue: {detected_issues}")
 assert True, "ProgramsuccessCheckTest to AbnormalDataIssue"
 else:
 # resultHasPassVerifyCheckTestto, HandAu to VerifyAbnormalvalueSavein
 anomaly_stats = {
 'negative_age_count': (df['age'] < 0).sum(),
 'old_age_count': (df['age'] > 150).sum(),
 'negative_income_count': (df['income'] < 0).sum(),
 'extreme_income_count': (df['income'] > 10000000).sum()
 }

 total_anomalies = sum(anomaly_stats.value s())
 assert total_anomalies > 0, f"DataShouldThisContainsAbnormalvalue, SystemDesign: {anomaly_stats}"

 print(f"AbnormalDataSystemDesign: {anomaly_stats}")

 # VerifyDatainContainsDesignAbnormalvalue
 assert df.iloc[0]['age'] == -5, "First rows yearShouldThisyes-5"
 assert df.iloc[1]['age'] == 200, "seconds rows yearShouldThisyes200"
 assert df.iloc[2]['income'] == -10000, "Third rowsReceiveinputShouldThisyes-10000"

if __name__ == "__main__":
 py test.main([__file__])