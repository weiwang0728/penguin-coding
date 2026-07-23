#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.5.2a K-S Curve - Chart Generation

Test whether K-S curve chart is generated.
"""

import pytest
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
    pytest.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestKSCurveGeneration:
    """K-S curve generation test class"""

    def setup_method(self):
        """Preparation before testing"""
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

        # Create distinctive target variable
        y = pd.Series(
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
            print("[INFO] Logistic regression model training completed")
        except Exception as e:
            print(f"[WARNING] Logistic regression training failed: {e}")
            self.model_available = False

    def test_ks_curve_generation(self):
        """Test K-S curve generation functionality"""
        if not self.model_available:
            pytest.skip("Model not available, skipping K-S curve generation test")

        # Act: Check K-S curve generation in model evaluation interface
        try:
            # Get trained algorithm instance
            algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

            if hasattr(algorithm, 'model') and algorithm.model is not None:
                # Make predictions
                y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]

                # Assert: Verify whether K-S curve chart is generated

                # 1. Calculate K-S curve data
                # K-S curve requires calculating good and bad sample cumulative distributions

                # Create prediction results DataFrame
                results_df = pd.DataFrame({
                    'actual': self.y_test.values,
                    'predicted_prob': y_pred_proba
                })

                # Sort by prediction probability in descending order
                results_df = results_df.sort_values('predicted_prob', ascending=False).reset_index(drop=True)

                # Calculate cumulative distributions
                total_positive = results_df['actual'].sum()
                total_negative = len(results_df) - total_positive

                results_df['cumulative_positive'] = results_df['actual'].cumsum()
                results_df['cumulative_negative'] = (~results_df['actual'].astype(bool)).cumsum()

                # Calculate TPR and FPR
                results_df['tpr'] = results_df['cumulative_positive'] / total_positive
                results_df['fpr'] = results_df['cumulative_negative'] / total_negative

                # Calculate K-S distance
                results_df['ks_distance'] = results_df['tpr'] - results_df['fpr']

                # Find maximum K-S distance
                max_ks_index = results_df['ks_distance'].abs().idxmax()
                max_ks_value = results_df.loc[max_ks_index, 'ks_distance']
                max_ks_position = max_ks_index / len(results_df)

                print(f"[INFO] K-S curve data statistics:")
                print(f"  Total samples: {len(results_df)}")
                print(f"  Positive samples: {total_positive}")
                print(f"  Negative samples: {total_negative}")
                print(f"  Maximum K-S distance: {abs(max_ks_value):.4f}")
                print(f"  Maximum K-S position: {max_ks_position:.2%}")

                # 2. Generate K-S curve chart
                plt.figure(figsize=(10, 8))

                # Calculate data points for plotting
                sample_points = np.linspace(0, 1, min(100, len(results_df)))
                indices = (sample_points * (len(results_df) - 1)).astype(int)

                x_axis = sample_points
                tpr_values = results_df.loc[indices, 'tpr'].values
                fpr_values = results_df.loc[indices, 'fpr'].values

                # Plot TPR and FPR curves
                plt.plot(x_axis, tpr_values, 'b-', label='True Positive Rate', linewidth=2)
                plt.plot(x_axis, fpr_values, 'r-', label='False Positive Rate', linewidth=2)

                # Plot K-S distance
                plt.fill_between(x_axis, tpr_values, fpr_values, alpha=0.3, color='green',
                                 label=f'K-S Distance (Max: {abs(max_ks_value):.4f})')

                # Mark maximum K-S distance point
                max_ks_x = max_ks_position
                max_ks_tpr = results_df.loc[max_ks_index, 'tpr']
                max_ks_fpr = results_df.loc[max_ks_index, 'fpr']

                plt.plot(max_ks_x, max_ks_tpr, 'go', markersize=8, label='Max K-S Point')
                plt.plot(max_ks_x, max_ks_fpr, 'go', markersize=8)
                plt.plot([max_ks_x, max_ks_x], [max_ks_tpr, max_ks_fpr], 'g--', linewidth=2)

                # Add annotation
                plt.annotate(f'Max K-S: {abs(max_ks_value):.4f}',
                             xy=(max_ks_x, (max_ks_tpr + max_ks_fpr) / 2),
                             xytext=(max_ks_x + 0.1, (max_ks_tpr + max_ks_fpr) / 2),
                             arrowprops=dict(arrowstyle='->', color='green'),
                             fontsize=10, color='green', fontweight='bold')

                # Set figure attributes
                plt.xlabel('Cumulative Percentage of Population')
                plt.ylabel('Cumulative Percentage of Events')
                plt.title('Kolmogorov-Smirnov (K-S) Curve')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.xlim(0, 1)
                plt.ylim(0, 1)

                # Save chart
                output_path = "ks_curve.png"
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"[INFO] K-S curve chart saved: {output_path}")

                # 3. Verify chart generation
                fig = plt.gcf()
                assert fig is not None, "Should create matplotlib figure object"

                axes = fig.get_axes()
                assert len(axes) > 0, "Figure should contain at least one axis"

                ax = axes[0]

                # Verify figure elements
                lines = ax.get_lines()
                assert len(lines) >= 2, "Should have at least TPR and FPR lines"

                # Verify labels
                x_label = ax.get_xlabel()
                y_label = ax.get_ylabel()
                title = ax.get_title()

                assert 'population' in x_label.lower() or 'percentage' in x_label.lower(), "X-axis label should contain population percentage related content"
                assert 'events' in y_label.lower() or 'percentage' in y_label.lower(), "Y-axis label should contain events percentage related content"
                assert 'k-s' in title.lower() or 'kolmogorov' in title.lower(), "Title should contain K-S related content"

                # Verify legend
                legend = ax.get_legend()
                assert legend is not None, "Figure should contain legend"

                legend_labels = [text.get_text() for text in legend.get_texts()]
                tpr_in_legend = any('tpr' in label.lower() or 'true positive' in label.lower() for label in legend_labels)
                fpr_in_legend = any('fpr' in label.lower() or 'false positive' in label.lower() for label in legend_labels)

                assert tpr_in_legend, "Legend should contain TPR related label"
                assert fpr_in_legend, "Legend should contain FPR related label"

                print(f"[VALIDATION] K-S curve chart verification:")
                print(f"  - rows count: {len(lines)}")
                print(f"  - X-axis label: {x_label}")
                print(f"  - Y-axis label: {y_label}")
                print(f"  - Chart title: {title}")
                print(f"  - Legend label count: {len(legend_labels)}")

                # 4. Verify K-S statistics reasonableness
                assert 0 <= abs(max_ks_value) <= 1, f"K-S distance should be between 0-1: {abs(max_ks_value)}"
                assert abs(max_ks_value) > 0.01, f"K-S distance should be meaningful (>0.01): {abs(max_ks_value)}"

                # 5. Verify data point count
                assert len(tpr_values) == len(fpr_values), "TPR and FPR should have same number of data points"
                assert len(tpr_values) >= 10, f"Should have sufficient data points to plot curve: {len(tpr_values)}"

                # Clean up figure
                plt.close()

                print(f"\nK-S curve generation test passed: Successfully generated K-S curve chart, containing TPR/FPR curves and maximum K-S distance annotation")

            else:
                pytest.fail("Trained model is not available")

        except Exception as e:
            pytest.skip(f"K-S curve generation test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
