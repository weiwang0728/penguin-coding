#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.2.2a fieldprocessing - number valueTypeField Type Recognition

TestProgramwhethercorrectDifferentOutputPlaceHasnumber valueTypefield( year, ReceiveinputEqual).
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

class TestNumericFieldRecognition:
 """number valueTypeField Type RecognitionTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.data_manager = DataManager(self.config)

 # CreateContainsclearnumber valueTypeandnumber valueTypefieldTest data
 np.random.seed(42)
 n_samples = 120

 self.test_data = pd.DataFrame({
 # number valueTypefield
 'age': np.random.randint(20, 80, n_samples), # year
 'income': np.random.randint(20000, 200000, n_samples), # Receiveinput
 'credit_score': np.random.randint(300, 850, n_samples), # UseDividenumber
 'employment_years': np.random.randint(0, 40, n_samples), # EngineeringWork yearLimited
 'debt_ratio': np.random.uniform(0, 1, n_samples), # BiferExample

 # ClassificationTypefield
 'gender': np.random.choice(['Male', 'Female'], n_samples), # nessDifferent
 'education': np.random.choice(['High School', 'Bachelor', 'Master'], n_samples), # Average
 'job_category': np.random.choice(['IT', 'Finance', 'Healthcare'], n_samples), # categoryDifferent

 # target
 'target': np.random.choice([0, 1], n_samples)
 })

 # CreateTimeCSVFile
 self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
 self.test_data.to_csv(self.temp_file.name, index=False)
 self.temp_file.close()

 def teardown_method(self):
 """TestafterCleanProcessor"""
 if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
 os.unlink(self.temp_file.name)

 def test_numeric_field_recognition(self):
 """Testnumber valueTypeField Type Recognition function"""
 # Execute (Act): ImportDatafieldcategoryTypeDifferentresult
 df = self.data_manager.import_data(self.temp_file.name, validate=False)

 # VerifyData import success
 assert isinstance(df, pd.DataFrame)
 assert len(df) == 120

 # Break (Assert): VerifyProgramwhethercorrectDifferentOutputPlaceHasnumber valueTypefield

 # 1. GetGetpand as Au to Au to Differentnumber valueTypefield
 numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

 # 2. Periodnumber valueTypefieldList
 expected_numeric_fields = ['age', 'income', 'credit_score', 'employment_years', 'debt_ratio', 'target']

 print(f"DifferentOutputnumber valueTypefield: {numeric_columns}")
 print(f"Periodnumber valueTypefield: {expected_numeric_fields}")

 # 3. VerifyKeynumber valueTypefieldcorrectDifferent
 critical_numeric_fields = ['age', 'income', 'credit_score']
 for field in critical_numeric_fields:
 assert field in numeric_columns, f"Keynumber valueTypefield '{field}' ShouldThisDifferentasnumber valueType"

 # 4. Verifynumber valueTypefieldHasDifferent
 categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
 expected_categorical_fields = ['gender', 'education', 'job_category']

 for field in expected_categorical_fields:
 assert field in categorical_columns, f"ClassificationTypefield '{field}' NotShouldThisDifferentasnumber valueType"
 assert field not in numeric_columns, f"ClassificationTypefield '{field}' NotShouldThisinnumber valueTypefieldin"

 # 5. Verifynumber valueTypefieldDatacategoryType
 for field in ['age', 'income', 'credit_score', 'employment_years']:
 if field in df.columns:
 assert pd.api.types.is_numeric_dtype(df[field]), f"{field}fieldShouldThisyesnumber value categoryType"

 # Verifynumber valueRangeCombineProcessor
 field_value s = df[field].dropna()
 assert len(field_value s) > 0, f"{field}fieldShouldThisHasHasEffectnumber value"

 if field == 'age':
 assert field_value s.min() >= 18, " yearMostSmallvalueShouldThis>=18"
 assert field_value s.max() <= 100, " yearMostLargevalueShouldThis<=100"
 elif field == 'income':
 assert field_value s.min() >= 0, "ReceiveinputShouldThis>=0"
 assert field_value s.max() <= 500000, "ReceiveinputMostLargevalueShouldThisCombineProcessor"

 # 6. calculateDifferentAccuracy
 correctly_identified_numeric = len(set(critical_numeric_fields) & set(numeric_columns))
 numeric_accuracy = correctly_identified_numeric / len(critical_numeric_fields)

 assert numeric_accuracy >= 1.0, f"number valueTypeField Type RecognitionAccuracyShouldThis100%, Implementationinternational{numeric_accuracy:.1%}"

 print(f"Field Type Recognitionresult: number valueType{len(numeric_columns)}items, ClassificationType{len(categorical_columns)}items")
 print(f"number valueTypeField Type RecognitionAccuracy: {numeric_accuracy:.1%}")
 print("number valueTypeField Type RecognitionTest Passed: ProgramcorrectDifferentOutputPlaceHasnumber valueTypefield, fieldcategoryTypeDifferentStand ard Accurate")

if __name__ == "__main__":
 py test.main([__file__])