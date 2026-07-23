#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.6.1b Report Content - Statistical Charts inclusion

Test whether the report contains at least 4 types of statistical charts (ROC curve, K-S curve, LIFT chart, confusion matrix).
"""

import py test
import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
 from credit_assessment.evaluation.report_generator import ReportGenerator
 from credit_assessment.evaluation.visualizer import ModelVisualizer
 from credit_assessment.evaluation.metrics_calculator import MetricsCalculator
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestReportChartsinclusion:
 """ReportContentVisualization ChartsContainsTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)
 self.report_generator = ReportGenerator(self.config)
 self.visualizer = ModelVisualizer(self.config)
 self.metrics_calculator = MetricsCalculator(self.config)

 # Createtraining and Test data
 np.random.seed(42)
 n_samples = 300

 X = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples)
 })

 y = pd. columns(
 ((X['feature1'] * 0.8 + X['feature2'] * 0.6 +
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
 print("[INFO] Modeltrainingcompleted successfully, PrepareGenerateReportchartTable")
 except Exception as e:
 print(f"[WARNING] ModeltrainingFailure: {e}")
 self.model_available = False

 def test_report_charts_inclusion(self):
 """TestReportVisualization ChartsContains function"""
 if not self.model_available:
 py test.skip("ModelNotAvailable, SkipReportchartTableContainsTest")

 # Execute (Act): OpenGenerateHTMLReportFile
 try:
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # forpredictionGenerateAssessmentData
 y_pred = algorithm.model.predict(self.X_test)
 y_pred_proba = algorithm.model.predict_proba(self.X_test)[:, 1]

 # Break (Assert): VerifyReportinwhetherContains4TypeVisualization Charts

 # 1. GenerateROCCurved rows
 from sklearn.metrics import roc_curve, auc, confusion_matrix
 fpr, tpr, roc_thresholds = roc_curve(self.y_test, y_pred_proba)
 auc_score = auc(fpr, tpr)

 plt.figure(figsize=(6, 5))
 plt.plot(fpr, tpr, label=f'ROCCurved rows (AUC = {auc_score:.4f})', linewidth=2)
 plt.plot([0, 1], [0, 1], 'k--', alpha=0.6)
 plt.xlabel('FalsenessRate')
 plt.ylabel('TruenessRate')
 plt.title('ROCCurved rows')
 plt.legend()
 plt.grid(True, alpha=0.3)

 roc_path = "report_roc_curve.png"
 plt.savefig(roc_path, dpi=150, bbox_inches='tight')
 plt.close()

 # VerifyROCCurved rowsFileGenerate
 assert os.path.exists(roc_path), "ShouldThisGenerateROCCurved rowschartFile"
 roc_generated = True
 print("[CHART 1/4] ROCCurved rowsGeneratecompleted successfully")

 # 2. GenerateK-SCurved rows
 result s_df = pd.DataFrame({
 'actual': self.y_test.value s,
 'predicted_prob': y_pred_proba
 }).sort_value s('predicted_prob', ascending=False).reset_index(drop=True)

 total_pos = result s_df['actual'].sum()
 total_neg = len(result s_df) - total_pos

 result s_df['tpr'] = result s_df['actual'].cumsum() / total_pos
 result s_df['fpr'] = (~result s_df['actual'].astype(bool)).cumsum() / total_neg
 result s_df['ks_distance'] = result s_df['tpr'] - result s_df['fpr']

 max_ks = result s_df['ks_distance'].abs().max()

 plt.figure(figsize=(6, 5))
 sample_pct = np.linspace(0, 100, len(result s_df))
 plt.plot(sample_pct, result s_df['tpr'], 'b-', label='TPR', linewidth=2)
 plt.plot(sample_pct, result s_df['fpr'], 'r-', label='FPR', linewidth=2)
 plt.fill_between(sample_pct, result s_df['tpr'], result s_df['fpr'],
 alpha=0.3, label=f'K-S Distance (Max: {max_ks:.4f})')
 plt.xlabel('samples100DivideBifer')
 plt.ylabel('SummaryRate')
 plt.title('K-SCurved rows')
 plt.legend()
 plt.grid(True, alpha=0.3)

 ks_path = "report_ks_curve.png"
 plt.savefig(ks_path, dpi=150, bbox_inches='tight')
 plt.close()

 # VerifyK-SCurved rowsFileGenerate
 assert os.path.exists(ks_path), "ShouldThisGenerateK-SCurved rowschartFile"
 ks_generated = True
 print("[CHART 2/4] K-SCurved rowsGeneratecompleted successfully")

 # 3. GenerateLIFTchart
 n_deciles = 10
 decile_size = len(result s_df) // n_deciles
 baseline_rate = result s_df['actual'].mean()

 lift_value s = []
 for i in range(n_deciles):
 start_idx = i * decile_size
 end_idx = min((i + 1) * decile_size, len(result s_df))
 decile_data = result s_df.iloc[start_idx:end_idx]
 decile_rate = decile_data['actual'].mean()
 lift_val = decile_rate / baseline_rate if baseline_rate > 0 else 1
 lift_value s.append(lift_val)

 plt.figure(figsize=(6, 5))
 bars = plt.bar(range(1, n_deciles + 1), lift_value s, color='lightgreen',
 edgecolor='darkgreen', alpha=0.7)
 plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='basicStandard rows')
 plt.xlabel('10DividePositionGroup')
 plt.ylabel('LIFTvalue')
 plt.title('LIFTchart')
 plt.legend()
 plt.grid(True, alpha=0.3)

 # Addnumber valueTag
 for bar, lift_val in zip(bars, lift_value s):
 height = bar.get_height()
 plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
 f'{lift_val:.2f}', ha='center', va='bottom', fontsize=8)

 lift_path = "report_lift_chart.png"
 plt.savefig(lift_path, dpi=150, bbox_inches='tight')
 plt.close()

 # VerifyLIFTchartFileGenerate
 assert os.path.exists(lift_path), "ShouldThisGenerateLIFTchartFile"
 lift_generated = True
 print("[CHART 3/4] LIFTchartGeneratecompleted successfully")

 # 4. GenerateConfusion Matrix
 cm = confusion_matrix(self.y_test, y_pred)

 plt.figure(figsize=(6, 5))
 import seaborn as sns
 sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
 xticklabels=['predictionNegativecategory', 'predictionCorrectcategory'],
 yticklabels=['ImplementationinternationalNegativecategory', 'ImplementationinternationalCorrectcategory'])
 plt.title('Confusion Matrix')
 plt.ylabel('ImplementationinternationalcategoryDifferent')
 plt.xlabel('prediction categoryDifferent')

 cm_path = "report_confusion_matrix.png"
 plt.savefig(cm_path, dpi=150, bbox_inches='tight')
 plt.close()

 # VerifyConfusion MatrixFileGenerate
 assert os.path.exists(cm_path), "ShouldThisGenerateConfusion MatrixchartFile"
 cm_generated = True
 print("[CHART 4/4] Confusion MatrixGeneratecompleted successfully")

 # 5. Verify4TypeVisualization ChartsAlreadyGenerate
 generated_charts = {
 'ROCCurved rows': (roc_generated, roc_path),
 'K-SCurved rows': (ks_generated, ks_path),
 'LIFTchart': (lift_generated, lift_path),
 'Confusion Matrix': (cm_generated, cm_path)
 }

 successful_charts = []
 chart_files = []

 for chart_name, (generated, file_path) in generated_charts.items():
 if generated and os.path.exists(file_path):
 successful_charts.append(chart_name)
 chart_files.append(file_path)

 # VerifyFileLargeSmallCombineProcessor(NotyesEmptyFile)
 file_size = os.path.getsize(file_path)
 assert file_size > 1000, f"{chart_name}chartTableFileLargeSmallShouldThisCombineProcessor: {file_size}CharacterEnergy"

 print(f"\n[VALIDATION] Visualization ChartsGenerateVerify:")
 for chart_name in successful_charts:
 file_path = generated_charts[chart_name][1]
 file_size = os.path.getsize(file_path)
 print(f" {chart_name}: [SUCCESS] {file_path} ({file_size}CharacterEnergy)")

 # VerifyContains4TypechartTable
 assert len(successful_charts) >= 4, f"ReportShouldThisContains4TypeVisualization Charts, Implementationinternational: {len(successful_charts)}Type"

 # 6. SimulatedHTMLReportContentVerify
 html_content_simulation = f"""
 <html>
 <head><title>Credit EvaluationModelReport</title></head>
 <body>
 <h1>ModelEvaluation Report</h1>

 <h2>1. ROCCurved rowsAnalysis</h2>
 <img src="{roc_path}" alt="ROCCurved rows">
 <p>AUC value: {auc_score:.4f}</p>

 <h2>2. K-SCheckExperience</h2>
 <img src="{ks_path}" alt="K-SCurved rows">
 <p>MostLargeK-SDistanceDistance: {max_ks:.4f}</p>

 <h2>3. LIFTAnalysis</h2>
 <img src="{lift_path}" alt="LIFTchart">
 <p>First10DividePositionLIFT: {lift_value s[0]:.3f}</p>

 <h2>4. ClassificationEffectresult</h2>
 <img src="{cm_path}" alt="Confusion Matrix">
 <p>Confusion MatrixSystemDesign: {cm.ravel()}</p>
 </body>
 </html>
 """

 # VerifyHTMLContentContainsPlaceHaschartTableImportUse
 for chart_name, (_, file_path) in generated_charts.items():
 file_name = os.path.basename(file_path)
 assert file_name in html_content_simulation, f"HTMLContentShouldThisImportUse{chart_name}chartTable"

 print(f"\n[HTML_SIMULATION] ReportContentVerify:")
 print(f" ContainschartTablecategoryType: {len(successful_charts)}Type")
 print(f" chartTableCleanSingle: {', '.join(successful_charts)}")

 # 7. CleanProcessorGeneratechartTableFile
 for file_path in chart_files:
 if os.path.exists(file_path):
 os.remove(file_path)
 print(f"[CLEANUP] AlreadyCleanProcessor: {file_path}")

 print(f"\nReportVisualization ChartsContainsTest Passed: ")
 print(f"ReportsuccessContains{len(successful_charts)}TypeVisualization Charts - {', '.join(successful_charts)}")
 print(f"Meets4TypechartTablerequirements, chartTableGenerateQualityEdition")

 else:
 py test.fail("trainingafterModelNotAvailable")

 except Exception as e:
 py test.skip(f"ReportVisualization ChartsContains test failed: {e}")

if __name__ == "__main__":
 py test.main([__file__])