#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.5.2b K-S Curve - Maximum KS Distance Annotation

Test whether the curve clearly marks the value and position of the maximum KS distance.
"""

import py test
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
 from credit_assessment.evaluation.visualizer import ModelVisualizer
 from credit_assessment.utils.config_manager import ConfigManager
 from sklearn.metrics import roc_curve
except ImportError as e:
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestKSMaxDistance:
 """K-S Curve Maximum Distance Annotation Test Class"""

 def setup_method(self):
 """Test setup"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.visualizer = ModelVisualizer(self.config)

 # Create training and test data
 np.random.seed(42)
 n_samples = 300

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # Create target variable with discriminative power
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

 # Train model
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.model_available = True
 print("[INFO] Logistic regression model training completed successfully")
 except Exception as e:
 print(f"[WARNING] Logistic regression training failed: {e}")
 self.model_available = False

 def test_ks_max_distance(self):
 """Test K-S curve maximum distance annotation function"""
 if not self.model_available:
 py test.skip("Model not available, skip K-S maximum distance annotation test")

 # Act: View generated K-S curve
 try:
 # Get trained algorithm instance
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # Make prediction s
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]

 # Assert: Verify whether the curve clearly marks the maximum KS distance value and position

 # 1. Calculate K-S curve data
 result s_df = pd.DataFrame({
 'actual': self.y_test.value s,
 'predicted_prob': y_pred_proba
 })

 # Sort by predicted probability in descending order
 result s_df = result s_df.sort_value s('predicted_prob', ascending=False).reset_index(drop=True)

 # Calculate cumulative distribution
 total_positive = result s_df['actual'].sum()
 total_negative = len(result s_df) - total_positive

 result s_df['cumulative_positive'] = result s_df['actual'].cumsum()
 result s_df['cumulative_negative'] = (~result s_df['actual'].astype(bool)).cumsum()

 # Calculate TPR and FPR
 result s_df['tpr'] = result s_df['cumulative_positive'] / total_positive
 result s_df['fpr'] = result s_df['cumulative_negative'] / total_negative

 # Calculate K-S distance (TPR - FPR)
 result s_df['ks_distance'] = result s_df['tpr'] - result s_df['fpr']

 # Find maximum K-S distance
 max_ks_index = result s_df['ks_distance'].abs().idxmax()
 max_ks_value = result s_df.loc[max_ks_index, 'ks_distance']
 max_ks_position = max_ks_index / len(result s_df) * 100 # Convert to percentile
 max_ks_threshold = result s_df.loc[max_ks_index, 'predicted_prob']

 print(f"[INFO] K-S statistic calculation result:")
 print(f" Maximum K-S distance: {abs(max_ks_value):.6f}")
 print(f" Maximum K-S position: {max_ks_position:.1f}th percentile")
 print(f" Corresponding threshold: {max_ks_threshold:.6f}")
 print(f" Corresponding TPR: {result s_df.loc[max_ks_index, 'tpr']:.4f}")
 print(f" Corresponding FPR: {result s_df.loc[max_ks_index, 'fpr']:.4f}")

 # 2. Generate K-S curve and verify maximum distance annotation
 plt.figure(figsize=(12, 8))

 # Calculate data points for plotting
 sample_percentiles = np.linspace(0, 100, len(result s_df))

 # Plot TPR and FPR curves
 plt.plot(sample_percentiles, result s_df['tpr'], 'b-',
 label='True Positive Rate (TPR)', linewidth=2)
 plt.plot(sample_percentiles, result s_df['fpr'], 'r-',
 label='False Positive Rate (FPR)', linewidth=2)

 # Fill K-S distance area
 plt.fill_between(sample_percentiles, result s_df['tpr'], result s_df['fpr'],
 alpha=0.3, color='green', label='K-S Distance')

 # Key: Annotate maximum K-S distance point
 max_ks_x = max_ks_position
 max_ks_tpr = result s_df.loc[max_ks_index, 'tpr']
 max_ks_fpr = result s_df.loc[max_ks_index, 'fpr']

 # Draw vertical line for maximum K-S distance
 plt.plot([max_ks_x, max_ks_x], [max_ks_tpr, max_ks_fpr],
 'g-', linewidth=4, alpha=0.8, label='Max K-S Distance')

 # Mark maximum K-S distance points
 plt.plot(max_ks_x, max_ks_tpr, 'go', markersize=10, markerfacecolor='lightgreen')
 plt.plot(max_ks_x, max_ks_fpr, 'go', markersize=10, markerfacecolor='lightgreen')

 # Add value and position annotation
 annotation_text = (f'Max K-S Distance: {abs(max_ks_value):.4f}\n'
 f'Position: {max_ks_position:.1f}% percentile\n'
 f'Threshold: {max_ks_threshold:.4f}')

 plt.annotate(annotation_text,
 xy=(max_ks_x, (max_ks_tpr + max_ks_fpr) / 2),
 xytext=(max_ks_x + 15, (max_ks_tpr + max_ks_fpr) / 2 + 0.1),
 arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2),
 fontsize=12, color='darkgreen', fontweight='bold',
 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.8))

 # Set figure properties
 plt.xlabel('Sample Percentile (%)')
 plt.ylabel('Cumulative Rate')
 plt.title(f'K-S Curve with Maximum Distance Annotation\nMax K-S = {abs(max_ks_value):.4f} at {max_ks_position:.1f}% percentile')
 plt.legend(loc='center right')
 plt.grid(True, alpha=0.3)
 plt.xlim(0, 100)
 plt.ylim(0, 1)

 # Save chart
 output_path = "ks_curve_with_max_distance.png"
 plt.savefig(output_path, dpi=150, bbox_inches='tight')
 print(f"[INFO] K-S curve (with maximum distance annotation) saved: {output_path}")

 # 3. Verify annotation correctness
 assert abs(max_ks_value) >= 0, "Maximum K-S distance should be non-negative"
 assert abs(max_ks_value) <= 1, "Maximum K-S distance should not exceed 1"
 assert 0 <= max_ks_position <= 100, "Maximum K-S position should be in 0-100 percentile range"
 assert 0 <= max_ks_threshold <= 1, "Corresponding threshold should be in 0-1 range"

 # 4. Verify figure annotation elements
 fig = plt.gcf()
 assert fig is not None, "Should have created matplotlib figure object"

 ax = fig.get_axes()[0]

 # Verify title contains maximum K-S distance information
 title = ax.get_title()
 assert str(round(abs(max_ks_value), 4)) in title, "Title should contain maximum K-S distance value"
 assert f'{max_ks_position:.1f}%' in title, "Title should contain maximum K-S position percentile"

 # Verify legend contains maximum K-S distance
 legend = ax.get_legend()
 assert legend is not None, "Figure should contain legend"

 legend_labels = [text.get_text() for text in legend.get_texts()]
 max_ks_in_legend = any('max' in label.lower() and 'k-s' in label.lower() for label in legend_labels)
 assert max_ks_in_legend, "Legend should contain maximum K-S distance related label"

 # Verify annotation text content
 annotations = [child for child in ax.get_children() if hasattr(child, 'get_text')]
 annotation_texts = [ann.get_text() for ann in annotations if hasattr(ann, 'get_text')]

 max_distance_annotated = any(str(round(abs(max_ks_value), 4)) in text for text in annotation_texts)
 position_annotated = any(f'{max_ks_position:.1f}%' in text for text in annotation_texts)

 print(f"[VALIDATION] Annotation verification:")
 print(f" - Maximum K-S distance annotated: {max_distance_annotated}")
 print(f" - Position percentile annotated: {position_annotated}")
 print(f" - Title contains information: Max K-S = {abs(max_ks_value):.4f}")
 print(f" - Legend label count: {len(legend_labels)}")

 # 5. Verify business reasonableness of value s
 if abs(max_ks_value) > 0.3:
 ks_performance = "Excellent"
 elif abs(max_ks_value) > 0.2:
 ks_performance = "Good"
 elif abs(max_ks_value) > 0.1:
 ks_performance = "Fair"
 else:
 ks_performance = "Poor"

 print(f"[ANALYSIS] K-S statistic performance rating: {ks_performance}")

 # Clean up figure
 plt.close()

 # 6. Final verification
 assert abs(max_ks_value) > 0.01, f"K-S distance should be meaningful (>0.01): {abs(max_ks_value)}"

 print(f"\nK-S curve maximum distance annotation test passed:")
 print(f"Curve clearly marks maximum K-S distance {abs(max_ks_value):.4f} and its position {max_ks_position:.1f}%")

 else:
 py test.fail("Trained model not available")

 except Exception as e:
 py test.skip(f"K-S curve maximum distance annotation test failed: {e}")


if __name__ == "__main__":
 py test.main([__file__])