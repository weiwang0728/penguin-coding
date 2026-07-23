#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.5.1a ROCCurved rows - chartPortraitGenerate (SimpleizationEdition)
"""

import os
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc

def test_roc_curve_generation_simple():
 """SimpleizationROCCurved rowsGenerateTest, NotDependDependitemsModule"""
 print("StartingTest2.5.1a ROCCurved rowsGenerate(SimpleizationEdition)...")

 # Create simulated prediction data
 np.random.seed(42)
 n_samples = 200

 # Simulated true labelsandprediction probability
 y_true = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
 y_proba = np.random.beta(2, 5, n_samples)

 # asCorrectsamplesincreasePlusprediction probability
 y_proba[y_true == 1] += 0.3
 y_proba = np.clip(y_proba, 0, 1)

 # CreateTimeOutputpath
 with tempfile.TemporaryDirectory() as temp_dir:
 output_path = os.path.join(temp_dir, "test_roc_curve.png")

 try:
 # calculateROCCurved rows
 fpr, tpr, thresholds = roc_curve(y_true, y_proba)
 auc_score = auc(fpr, tpr)

 # ControlROCCurved rows
 plt.figure(figsize=(8, 6))
 plt.plot(fpr, tpr, color='darkorange', lw=2,
 label=f'ROC curve (AUC = {auc_score:.3f})')
 plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
 label='Random')
 plt.xlim([0.0, 1.0])
 plt.ylim([0.0, 1.05])
 plt.xlabel('False Positive Rate')
 plt.ylabel('True Positive Rate')
 plt.title('ROC Curve')
 plt.legend(loc="lower right")
 plt.grid(True, alpha=0.3)

 # SavePNGFile
 plt.savefig(output_path, dpi=300, bbox_inches='tight')
 plt.close()

 # VerifyPNGFilewhetherGenerate
 assert os.path.exists(output_path), f"ROCCurved rowsPNGFileNotGenerate: {output_path}"

 # VerifyFileLargeSmall
 file_size = os.path.getsize(output_path)
 assert file_size > 10000, f"ROCCurved rowsPNGFileSmall: {file_size}CharacterEnergy"

 # Verify AUC valueCombineProcessorness
 assert 0.5 <= auc_score <= 1.0, f"AUC valueNotCombineProcessor: {auc_score}"
 assert auc_score > 0.7, f"AUC valueOverLow: {auc_score}"

 # VerifychartPortraitinch
 from PIL import Image
 with Image.open(output_path) as img:
 width, height = img.size
 assert width > 500 and height > 400, f"chartPortraitinchNotCombineProcessor: {width}x{height}"

 print(f"SUCCESS: ROCCurved rowsPNGGeneratesuccess: {output_path}")
 print(f"SUCCESS: FileLargeSmall: {file_size}CharacterEnergy")
 print(f"SUCCESS: AUC value: {auc_score:.3f}")
 print(f"SUCCESS: chartPortraitinch: {width}x{height}")
 print("SUCCESS: ROCCurved rowschartPortraitVerifyPass")

 return True

 except Exception as e:
 print(f"FAIL: ROCCurved rowsGenerateFailure: {e}")
 return False

if __name__ == "__main__":
 success = test_roc_curve_generation_simple()
 if success:
 print("2.5.1a ROCCurved rowsGenerateTest Passed")
 else:
 print("2.5.1a ROCCurved rowsGenerate test failed")