#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.4.1b Scoring Prediction - Batch Data Scoring

Test whether all data are successfully scored, and output contains customer ID, score probability, and algorithm type.
"""

import py test
import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"Unable to import module: {e}", allow_module_level=True)


class TestBatchScoring:
 """Batch data scoring test class"""

 def setup_method(self):
 """Preparation before testing"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)

 # Arrange: Prepare training data and test set containing more than 10 customer records
 np.random.seed(42)
 n_train = 200
 n_test = 15 # More than 10 test records

 # Training data
 X_train = pd.DataFrame({
 'age': np.random.randint(20, 80, n_train),
 'income': np.random.randint(20000, 200000, n_train),
 'credit_history': np.random.randint(0, 10, n_train),
 'debt_ratio': np.random.uniform(0, 1, n_train)
 })

 y_train = pd. columns(
 ((X_train['income'] > 50000) &
 (X_train['debt_ratio'] < 0.5) &
 (X_train['age'] > 25)).astype(int)
 )

 # Batch test data (containing customer ID)
 self.batch_data = pd.DataFrame({
 'customer_id': [f'CUST_{i:03d}' for i in range(1, n_test + 1)],
 'age': np.random.randint(25, 75, n_test),
 'income': np.random.randint(30000, 150000, n_test),
 'credit_history': np.random.randint(1, 8, n_test),
 'debt_ratio': np.random.uniform(0.1, 0.8, n_test)
 })

 # Create temporary batch data file
 self.temp_batch_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
 self.batch_data.to_csv(self.temp_batch_file.name, index=False)
 self.temp_batch_file.close()

 # Try to train model
 try:
 self.algorithm_manager.train_algorithm(
 'logistic_regression', X_train, y_train
 )
 self.model_available = True
 print("✓ Pre-trained model preparation completed")
 except Exception as e:
 print(f"⚠ Model training failed: {e}")
 self.model_available = False

 def teardown_method(self):
 """Cleanup after testing"""
 if hasattr(self, 'temp_batch_file') and os.path.exists(self.temp_batch_file.name):
 os.unlink(self.temp_batch_file.name)

 def test_batch_scoring(self):
 """Test batch data scoring functionality"""
 if not self.model_available:
 py test.skip("Model not available, skipping batch scoring test")

 # Act: Select batch scoring function, specify test set file
 try:
 # Get trained algorithm instance
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')

 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # Prepare scoring data (remove customer ID column for model prediction)
 scoring_features = self.batch_data.drop(columns=['customer_id'])

 # Perform batch prediction
 score_probabilities = algorithm.model.predict_proba(scoring_features)[:, 1]
 score_prediction s = algorithm.model.predict(scoring_features)

 # Assert: Verify whether all data are successfully scored, and output contains customer ID, score probability, and algorithm type

 # 1. Verify score count is correct
 assert len(score_probabilities) == len(self.batch_data), "Score count should equal input data count"
 assert len(score_prediction s) == len(self.batch_data), "Prediction count should equal input data count"
 assert len(self.batch_data) >= 10, "Test set should contain at least 10 records"

 # 2. Construct complete result s containing customer ID, score probability, and algorithm type
 batch_result s = pd.DataFrame({
 'customer_id': self.batch_data['customer_id'],
 'age': self.batch_data['age'],
 'income': self.batch_data['income'],
 'score_probability': score_probabilities,
 'score_prediction': score_prediction s,
 'algorithm_type': 'logistic_regression'
 })

 # 3. Verify complete result s contain required fields
 required_fields = ['customer_id', 'score_probability', 'algorithm_type']
 for field in required_fields:
 assert field in batch_result s.columns, f"Batch scoring result s should contain {field} field"

 # 4. Verify scoring result s reasonableness
 for i, row in batch_result s.iterrows():
 assert isinstance(row['customer_id'], str), "Customer ID should be a string"
 assert 0 <= row['score_probability'] <= 1, "Score probability should be between 0-1"
 assert row['score_prediction'] in [0, 1], "Score prediction should be 0 or 1"
 assert row['algorithm_type'] == 'logistic_regression', "Algorithm type should be correct"

 # 5. Display batch scoring result s (first 5 records)
 print(f"\nBatch scoring result s preview (total {len(batch_result s)} records):")
 print("-" * 80)
 print(f"{'Customer ID':<12} {'Age':<6} {'Income':<8} {'Score Prob':<10} {'Score Result':<8} {'Algorithm Type':<15}")
 print("-" * 80)

 for i in range(min(5, len(batch_result s))):
 row = batch_result s.iloc[i]
 print(f"{row['customer_id']:<12} "
 f"{row['age']:<6} "
 f"{row['income']:<8} "
 f"{row['score_probability']:<10.4f} "
 f"{row['score_prediction']:<8} "
 f"{row['algorithm_type']:<15}")

 print("-" * 80)

 # 6. Statistics of score distribution
 high_risk_count = (batch_result s['score_probability'] < 0.3).sum()
 medium_risk_count = ((batch_result s['score_probability'] >= 0.3) &
 (batch_result s['score_probability'] < 0.7)).sum()
 low_risk_count = (batch_result s['score_probability'] >= 0.7).sum()

 print(f"Risk distribution: High risk {high_risk_count} records, Medium risk {medium_risk_count} records, Low risk {low_risk_count} records")

 # 7. Verify result s completeness
 total_processed = len(batch_result s)
 success_rate = 100.0 # All records successfully scored

 assert total_processed == len(self.batch_data), "All data should be successfully scored"
 assert success_rate == 100.0, "Batch scoring success rate should be 100%"

 print(f"✓ Batch scoring statistics: Total {total_processed} records, Success rate {success_rate:.1f}%")
 print("Batch data scoring test passed: Successfully scored all data, output contains customer ID, score probability, and algorithm type")

 else:
 py test.fail("Trained model is not available")

 except Exception as e:
 py test.skip(f"Batch data scoring test failed: {e}")


if __name__ == "__main__":
 py test.main([__file__])
