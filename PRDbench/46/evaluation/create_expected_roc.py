#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Expected ROC Curve PNG File
"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc

def create_expected_roc_curve():
 """Create expected ROC curve plot"""
 # Simulate prediction data
 np.random.seed(42)
 n_samples = 1000

 # Create simulated true labels and prediction probabilities
 y_true = np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
 y_proba = np.random.beta(2, 5, n_samples)

 # Increase probability for positive samples
 y_proba[y_true == 1] += 0.3
 y_proba = np.clip(y_proba, 0, 1)

 # Calculate ROC curve
 fpr, tpr, thresholds = roc_curve(y_true, y_proba)
 auc_score = auc(fpr, tpr)

 # Plot ROC curve
 plt.figure(figsize=(8, 6))
 plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc_score:.3f})')
 plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
 plt.xlim([0.0, 1.0])
 plt.ylim([0.0, 1.05])
 plt.xlabel('False Positive Rate')
 plt.ylabel('True Positive Rate')
 plt.title('ROC Curve')
 plt.legend(loc="lower right")
 plt.grid(True, alpha=0.3)

 # Save file
 output_path = "expected_roc_curve.png"
 plt.savefig(output_path, dpi=300, bbox_inches='tight')
 plt.close()

 print(f"Expected ROC curve saved: {output_path}")
 print(f"AUC Score: {auc_score:.3f}")

 return output_path

if __name__ == "__main__":
 create_expected_roc_curve()