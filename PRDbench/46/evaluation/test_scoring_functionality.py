#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.4.1a&b Scoreprediction function - SingleDataScore and BatchDataScore
Based ontyperitemsModelStyle: Direct interface Test Core functionalityinstead of CLI interaction
"""

import sys
import os
import pandas as pd
import numpy as np

# AddsrcDirectory to Pythonpath
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_single_record_scoring():
 """TestSingleDataScore function"""
 print("TestSingleDataScore function...")

 try:
 from credit_assessment.data.data_manager import DataManager
 from credit_assessment.algorithms.logistic_regression import LogisticRegressionAnalyzer
 from credit_assessment.utils.config_manager import ConfigManager

 # Initialize components
 config = ConfigManager()
 data_manager = DataManager(config)
 algorithm = LogisticRegressionAnalyzer(config)

 # Preparing training data
 np.random.seed(42)
 n_samples = 100
 n_features = 5

 X_train = pd.DataFrame(np.random.randn(n_samples, n_features),
 columns=[f'feature_{i}' for i in range(n_features)])
 y_train = pd. columns(np.random.choice([0, 1], n_samples))

 # trainingModel
 model = algorithm.train(X_train, y_train)
 assert model is not None, "ModeltrainingFailure"

 # PrepareSingleTest data
 single_record = pd.DataFrame({
 f'feature_{i}': [np.random.randn()] for i in range(n_features)
 })

 # ExecuteSingleScore
 prediction s = algorithm.predict(single_record)

 # Verifyprediction result
 assert prediction s is not None, "predictionFailure"
 assert len(prediction s) == 1, "prediction result quantityNotcorrect"
 assert 0 <= prediction s[0] <= 1, "prediction probabilityUltraOutputRange[0,1]"

 # GetGetScore and EvaluateLevel
 score = prediction s[0] * 1000 # Conversionas1000DivideControl
 if score >= 800:
 grade = "Optimize"
 elif score >= 650:
 grade = ""
 elif score >= 500:
 grade = "One"
 elif score >= 350:
 grade = "ComparePoor"
 else:
 grade = "UltraPoor"

 print("[PASS] SingleDataScoresuccess")
 print("[INFO] Score result: {:.2f}Divide, Credit Rating: {}".format(score, grade))
 print("Scoreprediction functionnormal, OutputScore result andCredit Rating. ")

 return True

 except Exception as e:
 print("[FAIL] SingleDataScore test failed: {}".format(e))
 return False

def test_batch_scoring():
 """TestBatchDataScore function"""
 print("\n Test BatchDataScore function...")

 try:
 from credit_assessment.data.data_manager import DataManager
 from credit_assessment.algorithms.logistic_regression import LogisticRegressionAnalyzer
 from credit_assessment.utils.config_manager import ConfigManager

 # Initialize components
 config = ConfigManager()
 data_manager = DataManager(config)
 algorithm = LogisticRegressionAnalyzer(config)

 # Preparing training data
 np.random.seed(42)
 n_samples = 100
 n_features = 5

 X_train = pd.DataFrame(np.random.randn(n_samples, n_features),
 columns=[f'feature_{i}' for i in range(n_features)])
 y_train = pd. columns(np.random.choice([0, 1], n_samples))

 # trainingModel
 model = algorithm.train(X_train, y_train)
 assert model is not None, "ModeltrainingFailure"

 # PrepareBatchTest data(10on)
 batch_size = 15
 batch_data = pd.DataFrame(np.random.randn(batch_size, n_features),
 columns=[f'feature_{i}' for i in range(n_features)])

 # AddcustomerID
 batch_data['customer_id'] = [f'C{i:03d}' for i in range(1, batch_size + 1)]

 # ExecuteBatchScore
 features_only = batch_data.drop(columns=['customer_id'])
 prediction s = algorithm.predict(features_only)

 # Verifyprediction result
 assert prediction s is not None, "BatchpredictionFailure"
 assert len(prediction s) == batch_size, "prediction result quantityNotcorrect"

 # CreateCompleteresult
 result s = []
 for i, prob in enumerate(prediction s):
 customer_id = batch_data.iloc[i]['customer_id']
 score = prob * 1000
 algorithm_type = "Logistic Regression"

 result s.append({
 'customer_id': customer_id,
 'probability': prob,
 'score': score,
 'algorithm': algorithm_type
 })

 result s_df = pd.DataFrame(result s)

 print("[PASS] BatchDataScoresuccess")
 print("[INFO] successScore{}Data".format(len(result s_df)))
 print("[INFO] resultContains: customerID, Score Probability, Score, AlgorithmcategoryDifferent")
 print("BatchDataScoreTest Passed, successforPlaceHasDataforScore, OutputContainscustomerID, Score Probability, AlgorithmcategoryDifferentCompleteresult. ")

 return True

 except Exception as e:
 print("[FAIL] BatchDataScore test failed: {}".format(e))
 return False

def test_scoring_functionality():
 """TestScoreprediction function"""
 print("TestScoreprediction function...")

 single_result = test_single_record_scoring()
 batch_result = test_batch_scoring()

 if single_result and batch_result:
 print("\n[PASS] PlaceHasScoreFunctional TestPass")
 print("Test Passed: Scoreprediction function Complete")
 return True
 else:
 print("\n[FAIL] DivideScoreFunctional TestFailure")
 return False

if __name__ == "__main__":
 success = test_scoring_functionality()
 sys.exit(0 if success else 1)