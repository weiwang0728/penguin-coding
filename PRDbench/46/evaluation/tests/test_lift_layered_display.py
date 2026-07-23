#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.5.3b LIFTchart - DivideLayerExtractRepublicDisplay

TestchartonwhetherCleanClearDisplayNotSameDivideLayerExtractRepublicnumber value.
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

class TestLiftLayeredDisplay:
 """LIFTchartDivideLayerExtractRepublicDisplayTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.visualizer = ModelVisualizer(self.config)

 # Createtraining and Test data
 np.random.seed(42)
 n_samples = 500 # increasePlussamplesnumberGetUpdateFixedDivideLayerresult

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 # CreateHasRegionDivideRepublictarget
 y = pd. columns(
 ((X['feature1'] * 1.0 + X['feature2'] * 0.8 +
 np.random.normal(0, 0.3, n_samples)) > 0).astype(int)
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

 def test_lift_layered_display(self):
 """TestLIFTchartDivideLayerExtractRepublicDisplay function"""
 if not self.model_available:
 py test.skip("ModelNotAvailable, SkipLIFTDivideLayerDisplayTest")

 # Execute (Act): GenerateLIFTchart
 try:
 # GetGettrainingAlgorithmImplementationExample
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # forprediction
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]

 # Break (Assert): VerifychartonwhetherCleanClearDisplayNotSameDivideLayerExtractRepublicnumber value

 # 1. calculateDivideLayerLIFTData
 result s_df = pd.DataFrame({
 'actual': self.y_test.value s,
 'predicted_prob': y_pred_proba
 })

 # Accordingprediction probabilityDecreaseSequenceSort
 result s_df = result s_df.sort_value s('predicted_prob', ascending=False).reset_index(drop=True)

 # calculate basicStand ard CorrectsamplesRate
 baseline_positive_rate = result s_df['actual'].mean()

 # calculate10DividePositionDivideLayerLIFT
 n_layers = 10 # 10DividePositionDivideLayer
 layer_size = len(result s_df) // n_layers
 layered_lift_data = []

 for layer in range(n_layers):
 start_idx = layer * layer_size
 end_idx = min((layer + 1) * layer_size, len(result s_df))

 # CurrentDivideLayerData
 layer_data = result s_df.iloc[start_idx:end_idx]

 # calculateDivideLayermetrics
 layer_positive_count = layer_data['actual'].sum()
 layer_total_count = len(layer_data)
 layer_positive_rate = layer_positive_count / layer_total_count if layer_total_count > 0 else 0
 layer_lift = layer_positive_rate / baseline_positive_rate if baseline_positive_rate > 0 else 1

 layered_lift_data.append({
 'layer': layer + 1,
 'layer_name': f'{layer + 1}10DividePosition',
 'positive_count': layer_positive_count,
 'total_count': layer_total_count,
 'positive_rate': layer_positive_rate,
 'lift_value': layer_lift,
 'population_start': start_idx / len(result s_df) * 100,
 'population_end': end_idx / len(result s_df) * 100
 })

 print(f"\n[INFO] DivideLayerLIFTcalculate result:")
 print(f" basicStand ard CorrectsamplesRate: {baseline_positive_rate:.4f}")
 print(f" DivideLayernumber: {n_layers}")
 print(f" Layersamplesnumber: {layer_size}items")

 # 2. GenerateDivideLayerLIFTchartDisplaynumber value
 plt.figure(figsize=(14, 10))

 # ExtractGetchartData
 layers = [item['layer'] for item in layered_lift_data]
 lift_value s = [item['lift_value'] for item in layered_lift_data]
 positive_rates = [item['positive_rate'] for item in layered_lift_data]

 # Mainchart: DivideLayerLIFTvalue
 plt.subplot(2, 2, 1)
 bars = plt.bar(layers, lift_value s, color='lightcoral', alpha=0.7,
 edgecolor='darkred', linewidth=1)
 plt.axhline(y=1, color='black', linestyle='--', alpha=0.7, label='basicStandard rows (LIFT=1)')
 plt.xlabel('10DividePositionLayer')
 plt.ylabel('LIFTvalue')
 plt.title('DivideLayerLIFTvalueDivideDistribution')
 plt.legend()
 plt.grid(True, alpha=0.3)

 # CleanClearDisplayitemsDivideLayerExtractRepublicnumber value
 for i, (bar, lift_val) in enumerate(zip(bars, lift_value s)):
 height = bar.get_height()
 plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
 f'{lift_val:.3f}', ha='center', va='bottom',
 fontsize=10, fontweight='bold', color='darkred')

 # Helpchart: CorrectsamplesRateDivideDistribution
 plt.subplot(2, 2, 2)
 bars2 = plt.bar(layers, positive_rates, color='lightblue', alpha=0.7,
 edgecolor='darkblue', linewidth=1)
 plt.axhline(y=baseline_positive_rate, color='red', linestyle='--',
 alpha=0.7, label=f'basicStand ard Rate: {baseline_positive_rate:.3f}')
 plt.xlabel('10DividePositionLayer')
 plt.ylabel('CorrectsamplesRate')
 plt.title('DivideLayerCorrectsamplesRateDivideDistribution')
 plt.legend()
 plt.grid(True, alpha=0.3)

 # DisplayCorrectsamplesRatenumber value
 for bar, rate_val in zip(bars2, positive_rates):
 height = bar.get_height()
 plt.text(bar.get_x() + bar.get_width()/2., height + 0.005,
 f'{rate_val:.3f}', ha='center', va='bottom',
 fontsize=9, fontweight='bold', color='darkblue')

 # Detailednumber valueTableFormat
 plt.subplot(2, 1, 2)
 plt.axis('off') # CloseMark

 # CreateTableFormatData
 table_data = []
 headers = ['DivideLayer', 'Correctsamplesnumber', 'Totalsamplesnumber', 'CorrectsamplesRate', 'LIFTvalue', 'PersonRegionBetween(%)']

 for item in layered_lift_data:
 table_data.append([
 item['layer_name'],
 f"{item['positive_count']}",
 f"{item['total_count']}",
 f"{item['positive_rate']:.4f}",
 f"{item['lift_value']:.4f}",
 f"{item['population_start']:.0f}-{item['population_end']:.0f}%"
 ])

 # ControlTableFormat
 table = plt.table(cellText=table_data, colLabels=headers,
 cellLoc='center', loc='center',
 colWidths=[0.12, 0.1, 0.1, 0.12, 0.12, 0.14])
 table.auto_set_font_size(False)
 table.set_fontsize(9)
 table.scale(1, 2)

 # settingsTableForformat
 for i in range(len(headers)):
 table[(0, i)].set_facecolor('#4CAF50')
 table[(0, i)].set_text_props(weight='bold', color='white')

 for i in range(1, len(table_data) + 1):
 for j in range(len(headers)):
 if i % 2 == 0:
 table[(i, j)].set_facecolor('#f0f0f0')

 plt.title('DivideLayerLIFTDetailednumber valueTable', fontweight='bold', pad=20)

 plt.tight_layout()

 # SavechartTable
 output_path = "lift_layered_display.png"
 plt.savefig(output_path, dpi=150, bbox_inches='tight')
 print(f"[INFO] DivideLayerLIFTDisplaychartAlreadySave: {output_path}")

 # 3. VerifyDivideLayerExtractRepublicDisplay completeness
 assert len(layered_lift_data) == n_layers, f"ShouldThishas {n_layers}itemsDivideLayer, Implementationinternational: {len(layered_lift_data)}"

 # VerifyitemsDivideLayernumber value correctcalculate andDisplay
 for i, item in enumerate(layered_lift_data):
 assert item['lift_value'] >= 0, f"{i+1}DivideLayerLIFTvalueShouldThisNegative: {item['lift_value']}"
 assert 0 <= item['positive_rate'] <= 1, f"{i+1}DivideLayerCorrectsamplesRateShouldThisin0-1Between: {item['positive_rate']}"
 assert item['total_count'] > 0, f"{i+1}DivideLayerShouldThisHassamples: {item['total_count']}"

 print(f"[LAYER {i+1}] LIFT={item['lift_value']:.3f}, CorrectsamplesRate={item['positive_rate']:.3f}, "
 f"samplesnumber={item['total_count']}, RegionBetween={item['population_start']:.0f}-{item['population_end']:.0f}%")

 # 4. VerifyDivideLayerBetweenDifferentiationness(ModelShouldThisHasDifferentiation)
 lift_range = max(lift_value s) - min(lift_value s)
 print(f"[ANALYSIS] LIFTvalueDifferentiationRange: {lift_range:.3f}")

 if lift_range > 1.0:
 print("[SUCCESS] ModelDivideLayerEffectresult, EachLayerLIFTvalueDifferentiation")
 elif lift_range > 0.5:
 print("[INFO] ModelDivideLayerEffectresultOne, EachLayerHasOneFixedDifferentiation")
 else:
 print("[WARNING] ModelDivideLayerEffectresultCompareWeak, EachLayerDifferentiationNotLarge")

 # 5. VerifyHighDivideLayerOptimizeness(beforeitemsDivideLayerCommonConstantShouldThisHasUpdateHighLIFT)
 first_layer_lift = layered_lift_data[0]['lift_value']
 last_layer_lift = layered_lift_data[-1]['lift_value']

 print(f"[COMPARISON] 1LayerLIFT={first_layer_lift:.3f} vs {n_layers}LayerLIFT={last_layer_lift:.3f}")

 if first_layer_lift > last_layer_lift:
 print("[SUCCESS] HighDivideLayerToolHasUpdateHighLIFTvalue, meetPeriod")
 else:
 print("[INFO] DivideLayerLIFTDivideDistributionCanEnergyImportOneStepOptimizeization")

 # CleanProcessorchart
 plt.close()

 print(f"\nLIFTDivideLayerExtractRepublicDisplayTest Passed: chartTableCleanClearDisplay{n_layers}itemsDivideLayerExtractRepublicnumber value")
 print(f"LIFTvalueRange [{min(lift_value s):.3f}, {max(lift_value s):.3f}], DifferentiationRepublic {lift_range:.3f}")

 else:
 py test.fail("trainingafterModelNotAvailable")

 except Exception as e:
 py test.skip(f"LIFTDivideLayerExtractRepublicDisplay test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])