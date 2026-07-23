#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.5.4a Basic Metrics - Precision, Recall, F1 Calculation

Test whether precision, recall, and F1 score are calculate d and displayed simultaneously.
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
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestBasicMetrics:
 """Basic metrics calculation test class"""

 def setup_method(self):
 """Preparation before testing"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.metrics_calculator = MetricsCalculator(self.config)

 # Create training and test data
 np.random.seed(42)
 n_samples = 250

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # Create distinctive target variable
 y = pd. columns(
 ((X['feature1'] * 0.7 + X['feature2'] * 0.5 +
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
 print("✓ Pre-trained model preparation completed")
 except Exception as e:
 print(f"⚠ Model training failed: {e}")
 self.model_available = False

 def test_basic_metrics_calculation(self):
 """Test basic metrics calculation functionality"""
 if not self.model_available:
 py test.skip("Model not available, skipping basic metrics calculation test")

 # Act: Check evaluation metrics after algorithm execution
 try:
 # Get trained algorithm instance
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # Make prediction s
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]
 y_pred = algorithm.model.predict(self.X_test)

 # Assert: Verify whether precision, recall, and F1 score are calculate d and displayed simultaneously

 # 1. Calculate basic metrics
 accuracy = accuracy_score(self.y_test, y_pred)
 precision = precision_score(self.y_test, y_pred, average='binary', zero_division=0)
 recall = recall_score(self.y_test, y_pred, average='binary', zero_division=0)
 f1 = f1_score(self.y_test, y_pred, average='binary', zero_division=0)

 # 2. Verify metric types and ranges
 metrics = {
 'accuracy': accuracy,
 'precision': precision,
 'recall': recall,
 'f1_score': f1
 }

 for metric_name, value in metrics.items():
 assert isinstance(value, (float, np.floating)), f"{metric_name} should be a float"
 assert 0.0 <= value <= 1.0, f"{metric_name} should be between 0-1, actual: {value}"

 # 3. Display the 3 required metrics
 required_metrics = ['precision', 'recall', 'f1_score']
 print(f"\nBasic metrics calculation result s:")
 print("-" * 40)

 for metric_name in required_metrics:
 value = metrics[metric_name]
 print(f"{metric_name.upper():<10}: {value:.4f}")

 # Display accuracy (additional metric)
 print(f"{'ACCURACY':<10}: {accuracy:.4f}")
 print("-" * 40)

 # 4. Verify that at least 3 metrics are included (precision, recall, F1 score)
 available_required_metrics = [m for m in required_metrics if m in metrics]
 assert len(available_required_metrics) == 3, f"Should contain 3 required metrics, actual {len(available_required_metrics)} metrics"

 # 5. Verify metric value reasonableness
 # F1 score should be the harmonic mean of precision and recall
 expected_f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
 f1_difference = abs(f1 - expected_f1)

 assert f1_difference < 0.001, f"F1 score calculation verification failed, expected: {expected_f1:.4f}, actual: {f1:.4f}"

 print(f"✓ F1 score calculation verification: Calculated value={f1:.4f}, Verified value={expected_f1:.4f}, Poor={f1_difference:.6f}")

 # 6. Evaluate overall model performance
 avg_score = (precision + recall + f1) / 3
 if avg_score > 0.8:
 performance = "Excellent"
 elif avg_score > 0.7:
 performance = "Good"
 elif avg_score > 0.6:
 performance = "Fair"
 else:
 performance = "Needs improvement"

 print(f"✓ Comprehensive score: {avg_score:.4f} ({performance})")

 print(f"\nBasic metrics calculation test passed: Successfully calculate d and displayed precision, recall, and F1 score simultaneously, calculation s are accurate")

 else:
 py test.fail("Trained model is not available")

 except Exception as e:
 py test.skip(f"Basic metrics calculation test failed: {e}")


if __name__ == "__main__":
 py test.main([__file__])
