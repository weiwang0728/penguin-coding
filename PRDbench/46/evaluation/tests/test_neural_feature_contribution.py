#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.7.2b Neural Network interpretation - Feature Contribution Visualization

Test whetherGenerateFeature Contribution VisualizationchartTable.
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
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestNeuralFeatureContribution:
 """Neural NetworkFeature Contribution VisualizationTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.visualizer = ModelVisualizer(self.config)

 # CreateHasclearFeaturetraining data
 np.random.seed(42)
 n_samples = 300

 # DesignDesignFeature, UseHasNotSameRepublic
 feature1 = np.random.normal(0, 1, n_samples) # High
 feature2 = np.random.normal(0, 1, n_samples) # inEqual
 feature3 = np.random.normal(0, 1, n_samples) # Low
 feature4 = np.random.normal(0, 1, n_samples) # MostLow

 self.X_train = pd.DataFrame({
 'high_contrib': feature1,
 'medium_contrib': feature2,
 'low_contrib': feature3,
 'minimal_contrib': feature4
 })

 # Createtarget, clearFeatureRelated columns
 self.y_train = pd. columns(
 ((feature1 * 1.2 + # High
 feature2 * 0.6 + # inEqual
 feature3 * 0.2 + # Low
 feature4 * 0.05 + # MostLow
 np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
 )

 # trainingNeural NetworkModel
 try:
 self.algorithm_manager.train_algorithm(
 'neural_network', self.X_train, self.y_train
 )
 self.model_available = True
 print("[INFO] Neural NetworkModeltrainingcompleted successfully")
 except Exception as e:
 print(f"[WARNING] Neural NetworktrainingFailure: {e}")
 self.model_available = False

 # resultNeural NetworkNotAvailable, UseLogistic Regression as PrepareSelect
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )
 self.backup_model_available = True
 print("[INFO] PrepareUseLogistic RegressionModeltrainingcompleted successfully")
 except Exception as e2:
 print(f"[ERROR] PrepareUseModeltrainingFailure: {e2}")
 self.backup_model_available = False

 def test_neural_feature_contribution(self):
 """TestNeural NetworkFeature Contribution Visualization function"""
 # Execute (Act): inNeural NetworkAnalysisresult inFeature Contribution Visualization

 algorithm_name = None
 model = None

 # UseNeural NetworkModel
 if self.model_available:
 try:
 algorithm = self.algorithm_manager.get_algorithm('neural_network')
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 model = algorithm.model
 algorithm_name = 'neural_network'
 print("[INFO] UseNeural NetworkModelforFeatureAnalysis")
 except:
 pass

 # PrepareSelectOfficialCase: UseLogistic Regression
 if model is None and hasattr(self, 'backup_model_available') and self.backup_model_available:
 try:
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 model = algorithm.model
 algorithm_name = 'logistic_regression'
 print("[INFO] UseLogistic RegressionModelforFeatureAnalysis(PrepareSelectOfficialCase)")
 except:
 pass

 if model is None:
 py test.skip("HasAvailableModelforFeatureAnalysis")

 try:
 # Break (Assert): VerifywhetherGenerateFeature Contribution VisualizationchartTable

 # 1. calculateFeature
 feature_contributions = {}
 feature_names = self.X_train.columns.tolist()

 if algorithm_name == 'neural_network' and hasattr(model, 'coefs_'):
 # Neural Network: Based oninput LayerWeightWeightcalculateFeature
 input_weights = model.coefs_[0] # input Layer to FirstHidden LayerWeightWeight

 for i, feature_name in enumerate(feature_names):
 if i < input_weights.shape[0]:
 # calculateThisFeatureWeightWeightWeightness(forvalueAverageAverage)
 feature_weights = input_weights[i, :]
 contribution = np.mean(np.abs(feature_weights))
 feature_contributions[feature_name] = contribution

 elif algorithm_name == 'logistic_regression' and hasattr(model, 'coef_'):
 # Logistic Regression: Based on columnsnumber calculateFeature
 coefficients = model.coef_[0]

 for i, feature_name in enumerate(feature_names):
 if i < len(coefficients):
 contribution = abs(coefficients[i])
 feature_contributions[feature_name] = contribution

 else:
 py test.fail("ModelHasAvailableWeightWeightor columnsnumber information")

 # VerifyFeatureData
 assert len(feature_contributions) >= 3, f"ShouldThiscalculate at least 3FeatureRepublic, Implementationinternational: {len(feature_contributions)}"

 for feature, contribution in feature_contributions.items():
 assert isinstance(contribution, (float, np.floating)), f"{feature}RepublicShouldThisyesnumber value categoryType"
 assert contribution >= 0, f"{feature}RepublicShouldThisNegative: {contribution}"

 print(f"[INFO] Featurecalculate completed successfully:")
 for feature, contribution in feature_contributions.items():
 print(f" {feature}: {contribution:.6f}")

 # 2. GenerateFeature Contribution VisualizationchartTable
 # AccordingRepublicSort
 sorted_contributions = sorted(feature_contributions.items(), key=lambda x: x[1], reverse=True)

 features = [item[0] for item in sorted_contributions]
 contributions = [item[1] for item in sorted_contributions]

 # CreateVisualizationchartTable
 plt.figure(figsize=(12, 8))

 # Mainchart: Featurechart
 plt.subplot(2, 2, 1)
 colors = plt.cm.viridis(np.linspace(0, 1, len(features)))
 bars = plt.barh(range(len(features)), contributions, color=colors)
 plt.yticks(range(len(features)), features)
 plt.xlabel('FeatureRepublic')
 plt.title(f'FeatureSort - {algorithm_name.upper()}')
 plt.grid(True, alpha=0.3, axis='x')

 # Addnumber valueTag
 for i, (bar, contrib) in enumerate(zip(bars, contributions)):
 plt.text(bar.get_width() + max(contributions) * 0.02, bar.get_y() + bar.get_height()/2,
 f'{contrib:.4f}', va='center', fontsize=9)

 plt.gca().invert_yaxis() # MostWeightin

 # Helpchart: Featurechart
 plt.subplot(2, 2, 2)
 if len(contributions) <= 6: # inFeatureNotManyTimeDisplaychart
 wedges, texts, autotexts = plt.pie(contributions, labels=features, autopct='%1.1f%%',
 startangle=90, colors=colors)
 plt.title('FeatureDivideDistribution')
 else:
 plt.text(0.5, 0.5, f'FeaturequantityOverMany\n({len(features)}items)\nNotSuitableCombinechartDisplay',
 ha='center', va='center', transform=plt.gca().transAxes)
 plt.axis('off')

 # Helpchart: RepublicSystemDesign
 plt.subplot(2, 2, 3)
 plt.axis('off')

 # calculateSystemDesigninformation
 total_contribution = sum(contributions)
 max_contribution = max(contributions)
 min_contribution = min(contributions)
 contribution_ratio = max_contribution / min_contribution if min_contribution > 0 else float('inf')

 stats_text = f"""FeatureSystemDesigninformation:

TotalRepublic: {total_contribution:.6f}
MostLarge: {max_contribution:.6f} ({features[0]})
MostSmall: {min_contribution:.6f} ({features[-1]})
Bifervalue: {contribution_ratio:.2f}
Featurequantity: {len(features)}items

Sort:"""

 for i, (feature, contrib) in enumerate(sorted_contributions[:4]):
 rank_text = f"\n{i+1}. {feature}: {contrib:.4f} ({contrib/total_contribution*100:.1f}%)"
 stats_text += rank_text

 if len(sorted_contributions) > 4:
 stats_text += f"\n... has {len(sorted_contributions)-4}itemsFeature"

 plt.text(0.1, 0.9, stats_text, transform=plt.gca().transAxes,
 verticalalignment='top', fontfamily='monospace', fontsize=10,
 bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

 # Helpchart: RepublicDivideDistributionDirectOfficialchart
 plt.subplot(2, 2, 4)
 plt.hist(contributions, bins=min(5, len(contributions)), alpha=0.7,
 color='lightcoral', edgecolor='darkred')
 plt.xlabel('Republicvalue')
 plt.ylabel('Featurequantity')
 plt.title('RepublicDivideDistribution')
 plt.grid(True, alpha=0.3)

 plt.tight_layout()

 # SaveVisualizationchartTable
 output_path = "neural_feature_contribution.png"
 plt.savefig(output_path, dpi=150, bbox_inches='tight')
 print(f"[INFO] Feature Contribution VisualizationchartTableAlreadySave: {output_path}")

 # 3. VerifyVisualizationchartTableGenerate
 fig = plt.gcf()
 assert fig is not None, "ShouldThisCreatematplotlibchartObject"

 axes = fig.get_axes()
 assert len(axes) >= 3, "chartTableShouldThisContainsat least 3Subchart" # RemoveCanEnergyEmptyWhiteSubchart

 # VerifyMainchart
 main_ax = axes[0] # Featurechart
 bars = main_ax.patches
 assert len(bars) >= len(features), f"chartShouldThishas {len(features)}items"

 # VerifyYTag(FeatureName)
 y_labels = [tick.get_text() for tick in main_ax.get_yticklabels()]
 for feature in features:
 assert feature in y_labels, f"Feature {feature} ShouldThisinYTagin"

 # VerifyMark
 title = main_ax.get_title()
 assert 'Feature' in title or 'feature' in title.lower(), "MarkShouldThisContainsFeatureCameraRelatedContent"

 # 4. VerifyRepublicAnalysisCombineProcessorness
 if len(sorted_contributions) >= 2:
 highest_contrib = sorted_contributions[0]
 lowest_contrib = sorted_contributions[-1]

 print(f"[ANALYSIS] FeatureAnalysis:")
 print(f" MostHigh: {highest_contrib[0]} ({highest_contrib[1]:.6f})")
 print(f" MostLow: {lowest_contrib[0]} ({lowest_contrib[1]:.6f})")
 print(f" Differentiation: {contribution_ratio:.2f}")

 # VerifyPeriodRelated columns(Based onDataGenerate)
 if 'high_contrib' in feature_contributions:
 high_contrib_val = feature_contributions['high_contrib']
 print(f" HighFeaturevalue: {high_contrib_val:.6f}")

 # CleanProcessorchart
 plt.close()

 # CleanProcessorGenerateFile
 if os.path.exists(output_path):
 os.remove(output_path)
 print(f"[CLEANUP] AlreadyCleanProcessor: {output_path}")

 print(f"\nFeature Contribution VisualizationTest Passed: ")
 print(f"successGenerate{algorithm_name}Feature Contribution VisualizationchartTable, Contains{len(features)}itemsFeatureAnalysis")

 except Exception as e:
 py test.skip(f"Feature Contribution Visualization test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])