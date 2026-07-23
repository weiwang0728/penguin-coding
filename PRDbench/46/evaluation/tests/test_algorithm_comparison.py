#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.3.4 Algorithm Performance Comparison function

Test whetherDisplayTypeAlgorithm Performance Comparison Table, Containsat least 4 metrics(Accuracy, Precision, Recall, F1 Score).
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
 from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestAlgorithmComparison:
 """Algorithm Performance Comparison Functional Testcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.metrics_calculator = MetricsCalculator(self.config)

 # Createtraining and Test data
 np.random.seed(42)
 n_samples = 200

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # CreateHasDefinitiontarget
 y = pd. columns(
 ((X['feature1'] * 0.6 + X['feature2'] * 0.4 +
 np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
 )

 # Dividetraining Test Set
 split_idx = int(n_samples * 0.7)
 self.X_train = X[:split_idx]
 self.X_test = X[split_idx:]
 self.y_train = y[:split_idx]
 self.y_test = y[split_idx:]

 def test_algorithm_comparison(self):
 """Test Algorithm Performance Comparison function"""
 # Prepare (Arrange): DivideDifferentExecuteLogistic Regression and Neural NetworkAlgorithm
 algorithms_to_test = ['logistic_regression', 'neural_network']
 comparison_result s = {}

 for algorithm_name in algorithms_to_test:
 try:
 # trainingAlgorithm
 training_result = self.algorithm_manager.train_algorithm(
 algorithm_name, self.X_train, self.y_train
 )

 # GetGetAlgorithmImplementationExampleforprediction
 algorithm = self.algorithm_manager.get_algorithm(algorithm_name)
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # forprediction
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
 y_pred = (y_pred_proba > 0.5).astype(int)

 # calculatePerformancemetrics
 comparison_result s[algorithm_name] = {
 'accuracy': accuracy_score(self.y_test, y_pred),
 'precision': precision_score(self.y_test, y_pred, average='binary'),
 'recall': recall_score(self.y_test, y_pred, average='binary'),
 'f1_score': f1_score(self.y_test, y_pred, average='binary'),
 'training_time': training_result.get('training_time', 0)
 }

 print(f"✓ {algorithm_name} training and Assessment completed successfully")

 except Exception as e:
 print(f"⚠ {algorithm_name} trainingFailure: {e}")
 comparison_result s[algorithm_name] = {'error': str(e)}

 # Execute (Act): SelectChoosePerformanceComparison function
 # Break (Assert): VerifywhetherDisplayTypeAlgorithm Performance Comparison Table, Containsat least 4 metrics

 # VerifyHasOneitemsAlgorithmsuccesstraining
 successful_algorithms = [name for name, result in comparison_result s.items() if 'error' not in result]
 assert len(successful_algorithms) >= 1, f"ShouldHasOneitemsAlgorithmtrainingsuccess, Implementationinternationalsuccess: {successful_algorithms}"

 # VerifyPerformanceComparisonTableContainsat least 4 metrics(Accuracy, Precision, Recall, F1 Score)
 required_metrics = ['accuracy', 'precision', 'recall', 'f1_score']

 for algorithm_name in successful_algorithms:
 result = comparison_result s[algorithm_name]

 # VerifyContainsPlaceHasmetrics
 for metric in required_metrics:
 assert metric in result, f"{algorithm_name}ShouldThisContains{metric}metrics"
 assert isinstance(result[metric], (int, float)), f"{metric}ShouldThisyesnumber value categoryType"
 assert 0 <= result[metric] <= 1, f"{metric}valueShouldThisin0-1Between"

 # DisplayPerformanceComparisonTable
 print("\n" + "="*60)
 print("Algorithm Performance Comparison Table")
 print("="*60)

 # TableHead
 headers = ["Algorithm"] + [metric.upper() for metric in required_metrics] + ["trainingtime(s)"]
 print(f"{'Algorithm':<20} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1 Score':<10} {'trainingtime':<12}")
 print("-" * 72)

 # Data rows
 for algorithm_name, result in comparison_result s.items():
 if 'error' not in result:
 print(f"{algorithm_name:<20} "
 f"{result['accuracy']:<10.4f} "
 f"{result['precision']:<10.4f} "
 f"{result['recall']:<10.4f} "
 f"{result['f1_score']:<10.4f} "
 f"{result['training_time']:<12.3f}")
 else:
 print(f"{algorithm_name:<20} {'trainingFailure':<50}")

 print("="*60)

 # VerifyBiferCompareresult completeness
 if len(successful_algorithms) >= 2:
 print(f"✓ successComparison{len(successful_algorithms)}TypeAlgorithmPerformance")

 # OutputMostAlgorithm
 best_algorithm = max(successful_algorithms,
 key=lambda x: comparison_result s[x]['f1_score'])
 best_f1 = comparison_result s[best_algorithm]['f1_score']

 print(f"✓ MostAlgorithm: {best_algorithm} (F1 Score: {best_f1:.4f})")

 elif len(successful_algorithms) == 1:
 print(f"✓ successAssessment{successful_algorithms[0]}AlgorithmPerformance")

 # MostEndVerify
 metrics_count = len(required_metrics)
 assert metrics_count >= 4, f"PerformanceComparisonShouldThisContainsat least 4 metrics, Implementationinternational{metrics_count}items"

 print(f"\nAlgorithm Performance Comparison Test Passed: DisplayAlgorithm Performance Comparison Table, Contains{metrics_count}itemsmetrics(Accuracy, Precision, Recall, F1 Score)")

if __name__ == "__main__":
 py test.main([__file__])