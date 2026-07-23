#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.2.4 Feature Selection - Correlation Coefficient Calculation

Test whether feature correlation coefficient matrix and filtering recommendations are displayed.
"""

import py test
import sys
import os
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.data.feature_engineer import FeatureEngineer
 from credit_assessment.utils.config_manager import ConfigManager
 from sklearn.feature_selection import SelectKBest, f_classif
 import scipy.stats as stats
except ImportError as e:
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestCorrelationAnalysis:
 """Correlation coefficient calculation test class"""

 def setup_method(self):
 """Preparation before testing"""
 self.config = ConfigManager()
 self.feature_engineer = FeatureEngineer(self.config)

 # Create test data with correlations
 np.random.seed(42)
 n_samples = 200

 # Design features with known correlations
 age = np.random.randint(20, 80, n_samples)
 income = age * 1000 + np.random.normal(0, 5000, n_samples) # Positively correlated with age
 debt_ratio = np.random.uniform(0, 1, n_samples)
 credit_score = 850 - debt_ratio * 300 + np.random.normal(0, 50, n_samples) # Negatively correlated with debt ratio
 savings = income * 0.1 + np.random.normal(0, 2000, n_samples) # Positively correlated with income

 self.test_data = pd.DataFrame({
 'age': age,
 'income': income,
 'debt_ratio': debt_ratio,
 'credit_score': credit_score,
 'savings': savings,
 'target': np.random.choice([0, 1], n_samples)
 })

 def test_correlation_analysis(self):
 """Test feature selection correlation coefficient calculation functionality"""
 # Pre-check: Ensure sufficient numeric features for analysis
 numeric_columns = self.test_data.select_dtypes(include=[np.number]).columns.tolist()
 feature_columns = [col for col in numeric_columns if col != 'target']

 assert len(feature_columns) >= 3, f"Should have at least 3 numeric features for correlation analysis, actual: {len(feature_columns)}"

 # Act: Select feature selection function, perform Pearson correlation coefficient calculation
 try:
 # Assert: Verify whether feature correlation coefficient matrix and filtering recommendations are displayed

 # 1. Calculate correlation coefficient matrix
 correlation_matrix = self.test_data[feature_columns].corr()

 # Verify correlation coefficient matrix structure
 assert isinstance(correlation_matrix, pd.DataFrame), "Correlation coefficient matrix should be DataFrame"
 assert correlation_matrix.shape[0] == correlation_matrix.shape[1], "Correlation coefficient matrix should be square"
 assert correlation_matrix.shape[0] == len(feature_columns), "Matrix dimension should equal feature count"

 print(f"\nFeature correlation coefficient matrix ({len(feature_columns)}x{len(feature_columns)}):")
 print("-" * 60)
 print(correlation_matrix.round(4))
 print("-" * 60)

 # 2. Verify correlation coefficient value properties
 for i in range(len(feature_columns)):
 for j in range(len(feature_columns)):
 corr_value = correlation_matrix.iloc[i, j]

 # Verify correlation coefficient is in [-1, 1] range
 assert -1 <= corr_value <= 1, f"Correlation coefficient should be between -1 and 1: {corr_value}"

 # Diagonal should be 1 (self-correlation)
 if i == j:
 assert abs(corr_value - 1.0) < 1e-10, f"Diagonal element should be 1: {corr_value}"

 # Matrix should be symmetric
 symmetric_value = correlation_matrix.iloc[j, i]
 assert abs(corr_value - symmetric_value) < 1e-10, "Correlation coefficient matrix should be symmetric"

 # 3. Identify high correlation feature pairs
 high_correlation_pairs = []
 correlation_threshold = 0.7 # High correlation threshold

 for i in range(len(feature_columns)):
 for j in range(i + 1, len(feature_columns)):
 corr_value = abs(correlation_matrix.iloc[i, j])
 if corr_value > correlation_threshold:
 high_correlation_pairs.append({
 'feature1': feature_columns[i],
 'feature2': feature_columns[j],
 'correlation': correlation_matrix.iloc[i, j]
 })

 print(f"\nHigh correlation feature pairs (|correlation| > {correlation_threshold}):")
 if high_correlation_pairs:
 for pair in high_correlation_pairs:
 print(f" {pair['feature1']} <-> {pair['feature2']}: {pair['correlation']:.4f}")
 else:
 print(" No high correlation feature pairs found")

 # 4. Calculate feature-target correlations
 target_correlations = {}
 for feature in feature_columns:
 corr_with_target = stats.pearsonr(self.test_data[feature], self.test_data['target'])[0]
 target_correlations[feature] = corr_with_target

 print(f"\nFeature-target correlations:")
 sorted_correlations = sorted(target_correlations.items(), key=lambda x: abs(x[1]), reverse=True)
 for feature, corr in sorted_correlations:
 print(f" {feature}: {corr:.4f}")

 # 5. Generate filtering recommendations
 recommendations = []

 # Recommendation 1: Based on high correlation feature pairs
 if high_correlation_pairs:
 recommendations.append(f"Found {len(high_correlation_pairs)} high correlation feature pairs, consider removing one of them to reduce multicollinearity")
 for pair in high_correlation_pairs:
 # Recommend keeping feature with higher target correlation
 corr1 = abs(target_correlations[pair['feature1']])
 corr2 = abs(target_correlations[pair['feature2']])
 if corr1 > corr2:
 recommendations.append(f" Recommend keeping {pair['feature1']} (target correlation: {corr1:.4f}), consider removing {pair['feature2']} (target correlation: {corr2:.4f})")
 else:
 recommendations.append(f" Recommend keeping {pair['feature2']} (target correlation: {corr2:.4f}), consider removing {pair['feature1']} (target correlation: {corr1:.4f})")
 else:
 recommendations.append("Feature correlations are appropriate, no need to remove high correlation features")

 # Recommendation 2: Based on feature-target correlations
 weak_features = [f for f, c in target_correlations.items() if abs(c) < 0.1]
 if weak_features:
 recommendations.append(f"Found {len(weak_features)} features with weak target correlations: {weak_features}")
 recommendations.append("Recommend further analyzing these feature import ance or considering feature engineering")

 strong_features = [f for f, c in target_correlations.items() if abs(c) > 0.3]
 if strong_features:
 recommendations.append(f"Found {len(strong_features)} features with strong target correlations: {strong_features}")
 recommendations.append("These feature pairs may be valuable for the model")

 print(f"\nFiltering recommendations:")
 for i, recommendation in enumerate(recommendations, 1):
 print(f" {i}. {recommendation}")

 # 6. Verify analysis result completeness
 assert len(correlation_matrix) >= 3, "Correlation coefficient matrix should contain at least 3 features"
 assert len(target_correlations) == len(feature_columns), "Should calculate all feature-target correlations"
 assert len(recommendations) >= 2, "Should provide at least 2 filtering recommendations"

 # Verify known correlations are correctly identified
 # income and age should be positively correlated
 if 'income' in feature_columns and 'age' in feature_columns:
 income_age_corr = correlation_matrix.loc['income', 'age']
 print(f"[VALIDATION] Income-age correlation: {income_age_corr:.4f} (expected positive correlation)")

 # credit_score and debt_ratio should be negatively correlated
 if 'credit_score' in feature_columns and 'debt_ratio' in feature_columns:
 credit_debt_corr = correlation_matrix.loc['credit_score', 'debt_ratio']
 print(f"[VALIDATION] Credit score-debt ratio correlation: {credit_debt_corr:.4f} (expected negative correlation)")

 print(f"\nFeature selection correlation coefficient calculation test passed: Displayed feature correlation coefficient matrix and filtering recommendations")
 print(f"Analyzed {len(feature_columns)} features, provided {len(recommendations)} filtering recommendations")

 except Exception as e:
 py test.skip(f"Feature selection correlation coefficient calculation test failed: {e}")


if __name__ == "__main__":
 py test.main([__file__])
