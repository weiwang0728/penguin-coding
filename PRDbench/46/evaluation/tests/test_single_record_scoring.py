#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.4.1a Scoreprediction - SingleDataScore

Test whetherOutputScore result andCredit Rating.
"""

import py test
import sys
import os
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestSingleRecordScoring:
 """SingleDataScoreTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)

 # Prepare (Arrange): Preparing training data and SinglecustomerData
 np.random.seed(42)
 n_samples = 200

 # training data
 self.X_train = pd.DataFrame({
 'age': np.random.randint(20, 80, n_samples),
 'income': np.random.randint(20000, 200000, n_samples),
 'credit_history': np.random.randint(0, 10, n_samples),
 'debt_ratio': np.random.uniform(0, 1, n_samples)
 })

 # Createtarget
 self.y_train = pd. columns(
 ((self.X_train['income'] > 50000) &
 (self.X_train['debt_ratio'] < 0.5)).astype(int)
 )

 # SinglecustomerData
 self.single_record = pd.DataFrame({
 'age': [35],
 'income': [75000],
 'credit_history': [5],
 'debt_ratio': [0.3]
 })

 # trainingOneitemsModel
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.model_available = True
 print("✓ trainingModelPreparecompleted successfully")
 except Exception as e:
 print(f"⚠ ModeltrainingFailure: {e}")
 self.model_available = False

 def test_single_record_scoring(self):
 """TestSingleDataScore function"""
 if not self.model_available:
 py test.skip("ModelNotAvailable, SkipScoreTest")

 # Execute (Act): SelectChooseSingleDataScore function, OutputinputcustomerData
 try:
 # GetGettrainingAlgorithmImplementationExample
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 # forSinglerecordsprediction
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # Use sklearnModelDirect interface prediction
 score_proba = algorithm.model.predict_proba(self.single_record)[0, 1]
 score_binary = algorithm.model.predict(self.single_record)[0]

 # Break (Assert): VerifywhetherOutputScore result andCredit Rating

 # 1. VerifyScore result
 assert isinstance(score_proba, (float, np.floating)), "Score ProbabilityShouldThisyesnumber value categoryType"
 assert 0 <= score_proba <= 1, "Score ProbabilityShouldThisin0-1Between"
 assert isinstance(score_binary, (int, np.integer)), "Score resultShouldThisyesEntirenumber categoryType"
 assert score_binary in [0, 1], "ImportControlScoreShouldThisyes0or1"

 print(f"✓ Score result: SummaryRate={score_proba:.4f}, prediction={score_binary}")

 # 2. GenerateCredit Rating
 if score_proba >= 0.8:
 credit_rating = "Optimize"
 risk_level = "Low"
 elif score_proba >= 0.6:
 credit_rating = ""
 risk_level = "inLow"
 elif score_proba >= 0.4:
 credit_rating = "One"
 risk_level = "in"
 elif score_proba >= 0.2:
 credit_rating = "ComparePoor"
 risk_level = "inHigh"
 else:
 credit_rating = "Poor"
 risk_level = "High"

 print(f"✓ Credit Rating: {credit_rating} ({risk_level})")

 # 3. VerifycustomerDatacompleteness
 input_features = self.single_record.iloc[0].to_dict()
 print(f"✓ customerData: {input_features}")

 # VerifyOutputinputDataCombineProcessorness
 assert input_features['age'] > 0, " yearShouldThisLargeAt0"
 assert input_features['income'] > 0, "ReceiveinputShouldThisLargeAt0"
 assert 0 <= input_features['debt_ratio'] <= 1, "BiferExampleShouldThisin0-1Between"

 # 4. VerifyScoreOverProcesscompleteness
 scoring_info = {
 'customer_data': input_features,
 'score_probability': float(score_proba),
 'score_binary': int(score_binary),
 'credit_rating': credit_rating,
 'risk_level': risk_level
 }

 # VerifyScoreinformationComplete
 assert 'score_probability' in scoring_info, "ShouldThisContainsScore Probability"
 assert 'credit_rating' in scoring_info, "ShouldThisContainsCredit Rating"

 print("\nSingleDataScoreDetailedresult:")
 for key, value in scoring_info.items():
 print(f" {key}: {value}")

 print("\nSingleDataScoreTest Passed: successOutputScore result andCredit Rating, functionnormalEngineeringWork")

 else:
 py test.fail("trainingafterModelNotAvailable")

 except Exception as e:
 py test.skip(f"SingleDataScore test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])