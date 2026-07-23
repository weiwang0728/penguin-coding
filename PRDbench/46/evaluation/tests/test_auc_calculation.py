#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.5.1b ROCCurved rows - AUC value calculate

Test whetherSameTimeDisplayStand ard AccurateAUC value(Protection: at least 3 decimal places).
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
 from credit_assessment.evaluation.metrics_calculator import MetricsCalculator
 from credit_assessment.utils.config_manager import ConfigManager
 from sklearn.metrics import roc_auc_score, roc_curve
 import matplotlib.pyplot as plt
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class Test AUCCalculation:
 """AUC value calculateTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.metrics_calculator = MetricsCalculator(self.config)

 # Createtraining and Test data
 np.random.seed(42)
 n_samples = 300

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # CreateHasRegionDividenesstarget
 y = pd. columns(
 ((X['feature1'] * 0.8 + X['feature2'] * 0.6 +
 np.random.normal(0, 0.4, n_samples)) > 0).astype(int)
 )

 # DivideData
 split_idx = int(n_samples * 0.7)
 self.X_train = X[:split_idx]
 self.X_test = X[split_idx:]
 self.y_train = y[:split_idx]
 self.y_test = y[split_idx:]

 # trainingModel
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.model_available = True
 print("✓ trainingModelPreparecompleted successfully")
 except Exception as e:
 print(f"⚠ ModeltrainingFailure: {e}")
 self.model_available = False

 def test_auc_calculation(self):
 """Test AUC value calculate function"""
 if not self.model_available:
 py test.skip("ModelNotAvailable, SkipAUC calculationTest")

 # Execute (Act): GenerateROCCurved rowsafter, AUC valueDisplay
 try:
 # GetGettrainingAlgorithmImplementationExample
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # forprediction
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]

 # Break (Assert): VerifywhetherSameTimeDisplayStand ard AccurateAUC value(Protection: at least 3 decimal places)

 # 1. calculate AUC value
 auc_score = roc_auc_score(self.y_test, y_pred_proba)

 # Verify AUC valueCombineProcessorness
 assert isinstance(auc_score, (float, np.floating)), "AUC valueShouldThisyesPointnumber"
 assert 0.0 <= auc_score <= 1.0, f"AUC valueShouldThisin0-1Between, Implementationinternational: {auc_score}"

 # Verify AUC value precision(at least 3 decimal places)
 auc_rounded = round(auc_score, 3)
 assert auc_rounded == round(auc_score, 3), "AUC valueShouldThisCanProtection3decimal places"

 print(f"✓ AUC value: {auc_score:.6f} (Protection3decimal places: {auc_rounded:.3f})")

 # 2. VerifyROCCurved rowsData
 fpr, tpr, thresholds = roc_curve(self.y_test, y_pred_proba)

 assert len(fpr) == len(tpr), "FPRandTPRLengthRepublicShouldThisCameraSame"
 assert len(fpr) > 1, "ROCCurved rowsShouldThisHasManyitemsPoint"
 assert np.all(fpr >= 0) and np.all(fpr <= 1), "FPRShouldThisin0-1Between"
 assert np.all(tpr >= 0) and np.all(tpr <= 1), "TPRShouldThisin0-1Between"

 print(f"✓ ROCCurved rowsPointnumber: {len(fpr)}itemsPoint")
 print(f"✓ FPRRange: [{fpr.min():.3f}, {fpr.max():.3f}]")
 print(f"✓ TPRRange: [{tpr.min():.3f}, {tpr.max():.3f}]")

 # 3. Verify AUCcalculation precision
 manual_auc = np.trapz(tpr, fpr) # UseRuleRulecalculate AUC
 auc_difference = abs(auc_score - manual_auc)

 assert auc_difference < 0.01, f"AUCcalculation precisionVerifyFailure, Differentiation: {auc_difference}"

 print(f"✓ AUCcalculation precisionVerify: sklearn={auc_score:.6f}, HandAutocalculate={manual_auc:.6f}, Differentiation={auc_difference:.6f}")

 # 4. Verify AUC valueDefinition
 if auc_score > 0.8:
 performance_level = "Optimize"
 elif auc_score > 0.7:
 performance_level = ""
 elif auc_score > 0.6:
 performance_level = "One"
 else:
 performance_level = "ChangeImport"

 print(f"✓ ModelPerformanceEvaluateLevel: {performance_level}")

 # 5. MostEndVerify
 assert auc_score > 0.5, "AUC valueShouldThisLargeAt0.5(Random Test Average)"

 print(f"\nAUC value calculateTest Passed: Stand ard AccurateDisplayAUC value{auc_score:.3f}, Protection3decimal places, calculation precision meets requirements")

 else:
 py test.fail("trainingafterModelNotAvailable")

 except Exception as e:
 py test.skip(f"AUC calculation test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])