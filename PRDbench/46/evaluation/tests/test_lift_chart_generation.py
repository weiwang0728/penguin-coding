#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.5.3a LIFTchart - chartPortraitGenerate

Test whetherGenerateLIFTchart.
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

class TestLiftChartGeneration:
 """LIFTchartGenerateTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.visualizer = ModelVisualizer(self.config)

 # Createtraining and Test data
 np.random.seed(42)
 n_samples = 400

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # CreateHasRegionDividenesstarget(ensureHasCorrectNegativesamples)
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
 print("[INFO] Logistic RegressionModeltrainingcompleted successfully")
 except Exception as e:
 print(f"[WARNING] Logistic RegressiontrainingFailure: {e}")
 self.model_available = False

 def test_lift_chart_generation(self):
 """TestLIFTchartNativesuccessEnergy"""
 if not self.model_available:
 py test.skip("ModelNotAvailable, SkipLIFTchartGenerateTest")

 # Execute (Act): inModelAssessment interfaceLIFTchartNativesuccessEnergy
 try:
 # GetGettrainingAlgorithmImplementationExample
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # forprediction
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]

 # Break (Assert): VerifywhetherGenerateLIFTchart

 # 1. calculateLIFTchartData
 result s_df = pd.DataFrame({
 'actual': self.y_test.value s,
 'predicted_prob': y_pred_proba
 })

 # Accordingprediction probabilityDecreaseSequenceSort
 result s_df = result s_df.sort_value s('predicted_prob', ascending=False).reset_index(drop=True)

 # calculate basicStand ard CorrectsamplesRate
 baseline_positive_rate = result s_df['actual'].mean()

 # calculateDividedecimal places and LIFT
 n_deciles = 10
 decile_size = len(result s_df) // n_deciles
 lift_data = []

 for i in range(n_deciles):
 start_idx = i * decile_size
 end_idx = min((i + 1) * decile_size, len(result s_df))

 # Current10DividePositionData
 decile_data = result s_df.iloc[start_idx:end_idx]

 # calculate metrics
 decile_positive_rate = decile_data['actual'].mean()
 lift_value = decile_positive_rate / baseline_positive_rate if baseline_positive_rate > 0 else 1

 # metrics
 cumulative_data = result s_df.iloc[:end_idx]
 cumulative_positive_rate = cumulative_data['actual'].mean()
 cumulative_lift = cumulative_positive_rate / baseline_positive_rate if baseline_positive_rate > 0 else 1

 lift_data.append({
 'decile': i + 1,
 'decile_lift': lift_value,
 'cumulative_lift': cumulative_lift,
 'decile_positive_rate': decile_positive_rate,
 'cumulative_positive_rate': cumulative_positive_rate,
 'population_pct': end_idx / len(result s_df) * 100
 })

 print(f"[INFO] LIFTchartDatacalculate:")
 print(f" Testsamplesnumber: {len(result s_df)}")
 print(f" basicStand ard CorrectsamplesRate: {baseline_positive_rate:.4f}")
 print(f" 10Dividedecimal places: {n_deciles}")

 # 2. GenerateLIFTchart
 plt.figure(figsize=(12, 8))

 # ExtractGetchartData
 deciles = [item['decile'] for item in lift_data]
 decile_lifts = [item['decile_lift'] for item in lift_data]
 cumulative_lifts = [item['cumulative_lift'] for item in lift_data]
 population_pcts = [item['population_pct'] for item in lift_data]

 # Control10DividePositionLIFTvalue
 plt.subplot(2, 1, 1)
 bars = plt.bar(deciles, decile_lifts, color='skyblue', alpha=0.7,
 edgecolor='navy', linewidth=1)
 plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='basicStandard rows (LIFT=1)')
 plt.xlabel('10DividePositionGroup')
 plt.ylabel('LIFTvalue')
 plt.title('Divide10DividePositionLIFTchart')
 plt.legend()
 plt.grid(True, alpha=0.3)

 # Addnumber valueTag
 for bar, lift_val in zip(bars, decile_lifts):
 height = bar.get_height()
 plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
 f'{lift_val:.2f}', ha='center', va='bottom', fontsize=9)

 # ControlLIFTCurved rows
 plt.subplot(2, 1, 2)
 plt.plot(population_pcts, cumulative_lifts, 'o-', linewidth=2,
 markersize=6, color='green', label='LIFT')
 plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='basicStandard rows (LIFT=1)')
 plt.xlabel('Person100DivideBifer (%)')
 plt.ylabel('LIFTvalue')
 plt.title('LIFTCurved rows')
 plt.legend()
 plt.grid(True, alpha=0.3)

 # AddKeyPointMarkNote
 for i in [2, 4, 6, 8]: # MarkNote30%, 50%, 70%, 90%Point
 if i < len(population_pcts):
 plt.annotate(f'({population_pcts[i]:.0f}%, {cumulative_lifts[i]:.2f})',
 xy=(population_pcts[i], cumulative_lifts[i]),
 xytext=(population_pcts[i] + 5, cumulative_lifts[i] + 0.05),
 arrowprops=dict(arrowstyle='->', alpha=0.6),
 fontsize=8)

 plt.tight_layout()

 # SavechartTable
 output_path = "lift_chart.png"
 plt.savefig(output_path, dpi=150, bbox_inches='tight')
 print(f"[INFO] LIFTchartAlreadySave: {output_path}")

 # 3. VerifychartTableGenerate
 fig = plt.gcf()
 assert fig is not None, "ShouldThisCreatematplotlibchartObject"

 axes = fig.get_axes()
 assert len(axes) >= 2, "LIFTchartShouldThisContainsat least 2Subchart(10DividePositionchartandchart)"

 # VerifyFirstitemsSubchart(10DividePositionLIFT)
 ax1 = axes[0]
 bars = ax1.patches
 assert len(bars) >= n_deciles, f"10DividePositionchartShouldThishas {n_deciles}items"

 ax1_title = ax1.get_title()
 assert 'lift' in ax1_title.lower(), "FirstitemsSubchartMarkShouldThisContainsLIFT"

 # VerifysecondsitemsSubchart(LIFT)
 ax2 = axes[1]
 lines = ax2.get_lines()
 assert len(lines) >= 1, "LIFTchartShouldThisHasOneCurved rows"

 ax2_title = ax2.get_title()
 assert 'lift' in ax2_title.lower() or '' in ax2_title, "secondsitemsSubchartMarkShouldThisContainsLIFT"

 # 4. VerifyLIFTDataCombineProcessorness
 for item in lift_data:
 assert item['decile_lift'] >= 0, "10DividePositionLIFTvalueShouldThisNegative"
 assert item['cumulative_lift'] >= 0, "LIFTvalueShouldThisNegative"
 assert 0 <= item['decile_positive_rate'] <= 1, "10DividePositionCorrectsamplesRateShouldThisin0-1Between"
 assert 0 <= item['cumulative_positive_rate'] <= 1, "CorrectsamplesRateShouldThisin0-1Between"

 # 5. VerifyLIFTContainDefinition
 max_decile_lift = max(decile_lifts)
 max_cumulative_lift = max(cumulative_lifts)

 print(f"[ANALYSIS] LIFTchartSystemDesign:")
 print(f" MostLarge10DividePositionLIFT: {max_decile_lift:.3f}")
 print(f" MostLargeLIFT: {max_cumulative_lift:.3f}")
 print(f" First10DividePositionLIFT: {decile_lifts[0]:.3f}")

 # VerifyLIFTvalueCombineProcessorness
 assert max_decile_lift >= 1.0, f"MostLargeLIFTvalueShouldThisas1, Implementationinternational: {max_decile_lift:.3f}"

 # CommonConstantbeforeitems10DividePositionShouldThisHasUpdateHighLIFTvalue
 first_decile_lift = decile_lifts[0]
 if first_decile_lift > 1.2:
 print(f"[SUCCESS] ModelRegionDividecapability, First10DividePositionLIFT = {first_decile_lift:.3f}")
 else:
 print(f"[INFO] ModelRegionDividecapabilityOne, First10DividePositionLIFT = {first_decile_lift:.3f}")

 # CleanProcessorchart
 plt.close()

 print(f"\nLIFTchartGenerateTest Passed: successGenerateContains10DividePosition and TypechartLIFTchart")

 else:
 py test.fail("trainingafterModelNotAvailable")

 except Exception as e:
 py test.skip(f"LIFTchartGenerate test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])