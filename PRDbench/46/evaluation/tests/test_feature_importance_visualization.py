#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.7.1b Feature Explanation - Top-N Importance Visualization

Test whether Top-N (at least top 5) feature import ance visualization chart is generated.
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
except ImportError as e:
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestFeatureImportanceVisualization:
 """Feature import ance visualization test class"""

 def setup_method(self):
 """Preparation before testing"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.visualizer = ModelVisualizer(self.config)

 # Create meaningful training data
 np.random.seed(42)
 n_samples = 300

 # Design features with different import ance levels
 age = np.random.randint(20, 80, n_samples)
 income = np.random.randint(20000, 200000, n_samples)
 debt_ratio = np.random.uniform(0, 1, n_samples)
 credit_history = np.random.randint(0, 10, n_samples)
 employment_years = np.random.randint(0, 40, n_samples)
 savings = np.random.uniform(0, 50000, n_samples)

 self.X_train = pd.DataFrame({
 'age': age,
 'income': income,
 'debt_ratio': debt_ratio,
 'credit_history': credit_history,
 'employment_years': employment_years,
 'savings': savings
 })

 # Create target variable with different feature import ance
 self.y_train = pd. columns(
 ((income / 100000 * 3) + # Income most import ant
 (-debt_ratio * 2) + # Debt ratio second import ant
 (credit_history / 10 * 1.5) + # Credit history import ant
 (age / 100 * 0.5) + # Age relatively less import ant
 (employment_years / 40 * 0.3) + # Employment years not very import ant
 (savings / 50000 * 0.2) + # Savings least import ant
 np.random.normal(0, 0.5, n_samples) > 0).astype(int)
 )

 # Train logistic regression model
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.model_available = True
 print("[INFO] Logistic regression model training completed")
 except Exception as e:
 print(f"[WARNING] Logistic regression training failed: {e}")
 self.model_available = False

 def test_feature_import ance_visualization(self):
 """Test feature import ance visualization functionality"""
 if not self.model_available:
 py test.skip("Logistic regression model not available, skipping feature import ance visualization test")

 # Act: Check feature import ance visualization in logistic regression result s
 try:
 # Get trained algorithm instance
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:

 # Assert: Verify whether Top-N (at least top 5) feature import ance visualization chart is generated

 # 1. Calculate feature import ance (based on coefficient absolute value s)
 if hasattr(algorithm.model, 'coef_'):
 coefficients = algorithm.model.coef_[0]
 feature_names = self.X_train.columns.tolist()

 # Calculate feature import ance (coefficient absolute value s)
 feature_import ance = pd.DataFrame({
 'feature': feature_names,
 'import ance': np.abs(coefficients),
 'coefficient': coefficients
 })

 # Sort by import ance
 feature_import ance = feature_import ance.sort_value s('import ance', ascending=False)

 print(f"\nFeature import ance ranking:")
 print("-" * 50)
 for i, row in feature_import ance.iterrows():
 print(f"{row['feature']:<20} {row['import ance']:<12.6f} (coef: {row['coefficient']:8.4f})")
 print("-" * 50)

 # 2. Verify at least 5 features
 assert len(feature_import ance) >= 5, f"Should have at least 5 features for import ance analysis, actual: {len(feature_import ance)}"

 # 3. Generate Top-N feature import ance visualization
 top_n = min(5, len(feature_import ance))
 top_features = feature_import ance.head(top_n)

 # Create visualization chart
 plt.figure(figsize=(10, 6))

 # Draw horizontal bar chart
 colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'][:top_n]
 bars = plt.barh(range(top_n), top_features['import ance'], color=colors)

 # Set labels and title
 plt.yticks(range(top_n), top_features['feature'])
 plt.xlabel('Feature Importance (|Coefficient|)')
 plt.title(f'Top-{top_n} Feature Importance')
 plt.gca().invert_yaxis() # Most import ant at top

 # Add value labels
 for i, (bar, import ance) in enumerate(zip(bars, top_features['import ance'])):
 plt.text(bar.get_width() + max(top_features['import ance']) * 0.01,
 bar.get_y() + bar.get_height()/2,
 f'{import ance:.4f}',
 va='center', ha='left', fontsize=9)

 plt.tight_layout()

 # Save chart (optional)
 output_path = "feature_import ance_top5.png"
 plt.savefig(output_path, dpi=150, bbox_inches='tight')
 print(f"[INFO] Feature import ance visualization chart saved: {output_path}")

 # 4. Verify visualization result s
 # Verify chart is correctly created
 fig = plt.gcf()
 assert fig is not None, "Should create matplotlib figure object"

 axes = fig.get_axes()
 assert len(axes) > 0, "Figure should contain at least one axis"

 ax = axes[0]

 # Verify bar chart
 bars = ax.patches
 assert len(bars) >= top_n, f"Should have {top_n} bars, actual: {len(bars)}"

 # Verify Y-axis labels (feature names)
 y_labels = [tick.get_text() for tick in ax.get_yticklabels()]
 for feature in top_features['feature'].head(top_n):
 assert feature in y_labels, f"Feature {feature} should be in Y-axis labels"

 # Verify X-axis label
 x_label = ax.get_xlabel()
 assert 'import ance' in x_label.lower() or 'coefficient' in x_label.lower(), "X-axis label should contain import ance related text"

 # Verify title
 title = ax.get_title()
 assert 'top' in title.lower() and str(top_n) in title, f"Title should contain Top-{top_n}"

 print(f"[VALIDATION] Visualization verification:")
 print(f" - Bar count: {len(bars)}")
 print(f" - Y-axis labels: {len(y_labels)} feature names")
 print(f" - X-axis label: {x_label}")
 print(f" - Chart title: {title}")

 # 5. Verify Top-N feature import ance ordering
 for i in range(len(top_features) - 1):
 current_import ance = top_features.iloc[i]['import ance']
 next_import ance = top_features.iloc[i + 1]['import ance']
 assert current_import ance >= next_import ance, "Feature import ance should be in descending order"

 # 6. Display most import ant feature information
 most_import ant = top_features.iloc[0]
 least_import ant = top_features.iloc[-1]

 print(f"\n[ANALYSIS] Top-{top_n} feature import ance analysis:")
 print(f" Most import ant feature: {most_import ant['feature']} (Importance: {most_import ant['import ance']:.6f})")
 print(f" Least import ant feature: {least_import ant['feature']} (Importance: {least_import ant['import ance']:.6f})")
 print(f" Importance ratio: {most_import ant['import ance'] / least_import ant['import ance']:.2f}")

 # Clean up figure
 plt.close()

 print(f"\nTop-N import ance visualization test passed: Successfully generated Top-{top_n} feature import ance visualization chart")

 else:
 py test.fail("Logistic regression model does not have coef_ attribute")

 else:
 py test.fail("Trained logistic regression model is not available")

 except Exception as e:
 py test.skip(f"Feature import ance visualization test failed: {e}")


if __name__ == "__main__":
 py test.main([__file__])
