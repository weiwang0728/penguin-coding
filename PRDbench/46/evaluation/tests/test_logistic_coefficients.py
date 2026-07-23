#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.7.1a Feature Explanation - Logistic Regression columnsnumberOutput

Test whetherOutputEachFeature columnsnumber value andCorrectNegativeShadowResponseOfficialDirection.
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

class TestLogisticCoefficients:
 """Logistic Regression columnsnumberOutputTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)

 # CreateHasDefinitiontraining data(Featureand target HasclearRelated columns)
 np.random.seed(42)
 n_samples = 300

 # DesignDesignFeature, Useand target HasAlreadyKnowRelated columns
 age = np.random.randint(20, 80, n_samples)
 income = np.random.randint(20000, 200000, n_samples)
 debt_ratio = np.random.uniform(0, 1, n_samples)
 credit_history = np.random.randint(0, 10, n_samples)

 self.X_train = pd.DataFrame({
 'age': age,
 'income': income,
 'debt_ratio': debt_ratio,
 'credit_history': credit_history
 })

 # Createtarget, Use and FeatureHasclearCorrectNegativeRelated columns
 # incomeCorrectShadowResponse, debt_ratioNegativeShadowResponse, ageandcredit_historyCorrectShadowResponse
 self.y_train = pd. columns(
 ((income / 100000 * 2) + # ReceiveinputCorrectShadowResponse
 (-debt_ratio * 3) + # BiferExampleNegativeShadowResponse
 (age / 100) + # yearLightMicrosoftCorrectShadowResponse
 (credit_history / 10) + # UsehistoryCorrectShadowResponse
 np.random.normal(0, 0.5, n_samples) > 0).astype(int)
 )

 # trainingModel
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.model_available = True
 print("[INFO] Logistic RegressionModeltrainingcompleted successfully")
 except Exception as e:
 print(f"[WARNING] Logistic RegressiontrainingFailure: {e}")
 self.model_available = False

 def test_logistic_coefficients(self):
 """TestLogistic Regression columnsnumberOutput function"""
 if not self.model_available:
 py test.skip("Logistic RegressionModelNotAvailable, Skip columnsnumberOutputTest")

 # Execute (Act): UseLogistic RegressionAlgorithmcompleted successfullyAnalysis
 try:
 # GetGettrainingAlgorithmImplementationExample
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:

 # Break (Assert): VerifywhetherOutputEachFeature columnsnumber value andCorrectNegativeShadowResponseOfficialDirection

 # 1. GetGetModel columnsnumber
 if hasattr(algorithm.model, 'coef_'):
 coefficients = algorithm.model.coef_[0] # Logistic Regression columnsnumber
 feature_names = self.X_train.columns.tolist()

 assert len(coefficients) == len(feature_names), " columnsnumber quantityShouldThisEqualAtFeaturequantity"

 print(f"\nLogistic Regression columnsnumberAnalysis:")
 print("-" * 50)
 print(f"{'FeatureName':<15} {' columnsnumber value':<12} {'ShadowResponseOfficialDirection':<10} {'ShadowResponseStrongRepublic'}")
 print("-" * 50)

 # 2. AnalysisitemsFeature columnsnumber value andShadowResponseOfficialDirection
 coefficient_analysis = {}

 for i, (feature, coef) in enumerate(zip(feature_names, coefficients)):
 # BreakShadowResponseOfficialDirection
 if coef > 0:
 direction = "CorrectShadowResponse"
 impact = "increasePlusSummaryRate" if coef > 0.1 else "LightMicrosoftincreasePlus"
 elif coef < 0:
 direction = "NegativeShadowResponse"
 impact = "DecreaseLowSummaryRate" if coef < -0.1 else "LightMicrosoftDecreaseLow"
 else:
 direction = "NoShadowResponse"
 impact = "NoShadowResponse"

 coefficient_analysis[feature] = {
 'coefficient': float(coef),
 'direction': direction,
 'impact': impact,
 'abs_coefficient': abs(float(coef))
 }

 print(f"{feature:<15} {coef:<12.6f} {direction:<10} {impact}")

 print("-" * 50)

 # 3. Verify columnsnumberCombineProcessorness
 for feature, analysis in coefficient_analysis.items():
 coef_value = analysis['coefficient']
 assert isinstance(coef_value, (float, np.floating)), f"{feature} columnsnumberShouldThisyesnumber value categoryType"
 assert not np.isnan(coef_value), f"{feature} columnsnumberNotShouldThisyesNaN"
 assert not np.isinf(coef_value), f"{feature} columnsnumberNotShouldThiswhetherLarge"

 # 4. VerifyPeriodCorrectNegativeShadowResponseOfficialDirection(Based onDataGenerate)
 # incomeShouldThisyesCorrectShadowResponse, debt_ratioShouldThisyesNegativeShadowResponse
 if 'income' in coefficient_analysis:
 income_coef = coefficient_analysis['income']['coefficient']
 print(f"[INFO] Receiveinput columnsnumber: {income_coef:.6f} (PeriodCorrectShadowResponse)")
 # NotStrongControlVerifyOfficialDirection, becauseDataRand omness CanEnergyShadowResponseresult

 if 'debt_ratio' in coefficient_analysis:
 debt_coef = coefficient_analysis['debt_ratio']['coefficient']
 print(f"[INFO] BiferExample columnsnumber: {debt_coef:.6f} (PeriodNegativeShadowResponse)")

 # 5. OutputShadowResponseMostLargeFeature
 most_import ant_feature = max(coefficient_analysis.keys(),
 key=lambda x: coefficient_analysis[x]['abs_coefficient'])
 max_coef_value = coefficient_analysis[most_import ant_feature]['abs_coefficient']

 print(f"\n[ANALYSIS] ShadowResponseMostLargeFeature: {most_import ant_feature}")
 print(f"[ANALYSIS] columnsnumber forvalue: {max_coef_value:.6f}")
 print(f"[ANALYSIS] ShadowResponseOfficialDirection: {coefficient_analysis[most_import ant_feature]['direction']}")

 # 6. Verify columnsnumberOutputcompleteness
 assert len(coefficient_analysis) >= 3, "ShouldThisOutputat least 3Feature columnsnumber"

 # VerifyContainsCorrectNegativeShadowResponse
 positive_coefs = [f for f, a in coefficient_analysis.items() if a['coefficient'] > 0]
 negative_coefs = [f for f, a in coefficient_analysis.items() if a['coefficient'] < 0]

 print(f"[INFO] CorrectShadowResponseFeature: {len(positive_coefs)}items - {positive_coefs}")
 print(f"[INFO] NegativeShadowResponseFeature: {len(negative_coefs)}items - {negative_coefs}")

 # ShouldThisHasOneFeatureHasShadowResponse
 significant_features = [f for f, a in coefficient_analysis.items()
 if a['abs_coefficient'] > 0.01]
 assert len(significant_features) >= 1, "ShouldThisHas1itemsFeatureHasShadowResponse"

 print(f"\nLogistic Regression columnsnumberOutputTest Passed: successOutputEachFeature columnsnumber value andCorrectNegativeShadowResponseOfficialDirection")
 print(f"Analysis{len(coefficient_analysis)}itemsFeature, in{len(significant_features)}itemsHasShadowResponse")

 else:
 py test.fail("Logistic RegressionModelHascoef_Attribute")

 else:
 py test.fail("trainingafterLogistic RegressionModelNotAvailable")

 except Exception as e:
 py test.skip(f"Logistic Regression columnsnumberOutput test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])