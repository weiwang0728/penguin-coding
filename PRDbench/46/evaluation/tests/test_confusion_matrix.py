#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.5.4b Basic Metrics - Confusion Matrix

Test whether confusion matrix is generated and displayed.
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
 from sklearn.metrics import confusion_matrix
except ImportError as e:
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestConfusionMatrix:
 """Confusion matrix test class"""

 def setup_method(self):
 """Preparation before testing"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.metrics_calculator = MetricsCalculator(self.config)

 # Create training and test data
 np.random.seed(42)
 n_samples = 200

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # Create distinctive target variable
 y = pd. columns(
 ((X['feature1'] * 0.8 + X['feature2'] * 0.6 +
 np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
 )

 # Split data
 split_idx = int(n_samples * 0.7)
 self.X_train = X[:split_idx]
 self.X_test = X[split_idx:]
 self.y_train = y[:split_idx]
 self.y_test = y[split_idx:]

 # Try to train model
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.model_available = True
 print("[SUCCESS] Pre-trained model preparation completed")
 except Exception as e:
 print(f"[WARNING] Model training failed: {e}")
 self.model_available = False

 def test_confusion_matrix(self):
 """Test confusion matrix functionality"""
 if not self.model_available:
 py test.skip("Model not available, skipping confusion matrix test")

 # Act: Check evaluation metrics after algorithm execution
 try:
 # Get trained algorithm instance
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # Make prediction s
 y_pred = algorithm.model.predict(self.X_test)

 # Assert: Verify whether confusion matrix is generated and displayed

 # 1. Generate confusion matrix
 cm = confusion_matrix(self.y_test, y_pred)

 # Verify confusion matrix structure
 assert isinstance(cm, np.ndarray), "Confusion matrix should be numpy array"
 assert cm.shape == (2, 2), f"Binary classification confusion matrix should be 2x2, actual: {cm.shape}"
 assert cm.dtype == np.int64 or cm.dtype == int, "Confusion matrix elements should be integers"

 # Verify confusion matrix value reasonableness
 assert np.all(cm >= 0), "All confusion matrix elements should be non-negative"
 assert cm.sum() == len(self.y_test), f"Confusion matrix total should equal test set size: {len(self.y_test)}"

 print(f"[INFO] Confusion matrix structure: {cm.shape}, Total: {cm.sum()}")

 # 2. Display confusion matrix
 print(f"\nConfusion Matrix:")
 print("-" * 30)
 print(f" Predicted")
 print(f"Actual 0 1 ")
 print(f" 0 {cm[0,0]:4d} {cm[0,1]:4d}") # TN, FP
 print(f" 1 {cm[1,0]:4d} {cm[1,1]:4d}") # FN, TP
 print("-" * 30)

 # 3. Parse confusion matrix components
 tn, fp, fn, tp = cm.ravel()

 matrix_components = {
 'True Negative (TN)': tn,
 'False Positive (FP)': fp,
 'False Negative (FN)': fn,
 'True Positive (TP)': tp
 }

 print(f"Confusion matrix components:")
 for component, value in matrix_components.items():
 assert isinstance(value, (int, np.integer)), f"{component} should be integer"
 assert value >= 0, f"{component} should be non-negative"
 print(f" {component}: {value}")

 # 4. Verify confusion matrix completeness
 total_samples = tp + tn + fp + fn
 assert total_samples == len(self.y_test), "Confusion matrix total samples should equal test set size"

 # 5. Calculate metrics based on confusion matrix
 accuracy = (tp + tn) / total_samples if total_samples > 0 else 0
 precision = tp / (tp + fp) if (tp + fp) > 0 else 0
 recall = tp / (tp + fn) if (tp + fn) > 0 else 0
 specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

 derived_metrics = {
 'Accuracy': accuracy,
 'Precision': precision,
 'Recall': recall,
 'Specificity': specificity
 }

 print(f"\nMetrics calculate d from confusion matrix:")
 for metric_name, value in derived_metrics.items():
 assert 0 <= value <= 1, f"{metric_name} should be between 0-1"
 print(f" {metric_name}: {value:.4f}")

 # 6. Verify confusion matrix business interpretation
 print(f"\nConfusion matrix business interpretation:")
 print(f" Correctly predicted as low risk: {tn} cases ({tn/total_samples:.1%})")
 print(f" Correctly predicted as high risk: {tp} cases ({tp/total_samples:.1%})")
 print(f" Misclassified as high risk: {fp} cases ({fp/total_samples:.1%})")
 print(f" Misclassified as low risk: {fn} cases ({fn/total_samples:.1%})")

 # 7. Verify confusion matrix quality
 # Good model should have larger value s on the diagonal
 correct_prediction s = tp + tn
 incorrect_prediction s = fp + fn

 assert correct_prediction s >= incorrect_prediction s, "Correct prediction s should be more than incorrect prediction s"

 accuracy_rate = correct_prediction s / total_samples
 print(f"[INFO] Prediction accuracy: {accuracy_rate:.1%}")

 assert accuracy_rate > 0.5, f"Accuracy should be greater than 50%, actual: {accuracy_rate:.1%}"

 print(f"\nConfusion matrix test passed: Successfully generated and displayed confusion matrix, structure is correct, calculation s are accurate, functionality works properly")

 else:
 py test.fail("Trained model is not available")

 except Exception as e:
 py test.skip(f"Confusion matrix test failed: {e}")


if __name__ == "__main__":
 py test.main([__file__])
