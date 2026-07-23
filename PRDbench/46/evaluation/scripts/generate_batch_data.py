#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Large Batch Test data Generation Script

Generate standard datasets for batch scoring and performance testing
"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse

def generate_credit_data(num_records, seed=42, include_target=True):
 """
 Generate credit evaluation test data

 Args:
 num_records: Number of records to generate
 seed: Random seed
 include_target: Whether to include target column

 Returns:
 pandas.DataFrame: Generated dataset
 """
 np.random.seed(seed)

 # Generate basic customer information
 data = {
 'customer_id': [f'CUST_{str(i).zfill(6)}' for i in range(1, num_records + 1)],
 'age': np.random.normal(35, 10, num_records).astype(int).clip(18, 70),
 'income': np.random.lognormal(10.5, 0.5, num_records).astype(int),
 'employment_years': np.random.exponential(5, num_records).astype(int).clip(0, 30),
 'debt_ratio': np.random.beta(2, 5, num_records).clip(0, 1),
 'credit_history': np.random.choice(
 ['excellent', 'good', 'fair', 'poor'],
 num_records,
 p=[0.2, 0.4, 0.3, 0.1]
 )
 }

 # If target is needed, generate target based on feature combination
 if include_target:
 # Calculate credit risk probability based on features
 risk_score = (
 (data['age'] / 70) * 0.2 +
 (np.log(data['income']) / 12) * 0.3 +
 (data['employment_years'] / 30) * 0.2 +
 (1 - data['debt_ratio']) * 0.3
 )

 # Adjust based on credit history
 history_multiplier = {
 'excellent': 1.2, 'good': 1.0, 'fair': 0.8, 'poor': 0.5
 }
 risk_score *= [history_multiplier[h] for h in data['credit_history']]

 # Convert to binary target (0=high risk, 1=low risk)
 data['target'] = (risk_score > np.median(risk_score)).astype(int)

 return pd.DataFrame(data)

def generate_batch_test_data():
 """Generate batch scoring test data (20 records)"""
 print("Generating batch scoring test data...")
 batch_data = generate_credit_data(20, seed=123, include_target=False)

 output_path = Path(__file__).parent.parent / "test_data_batch.csv"
 batch_data.to_csv(output_path, index=False)

 print(f"[SUCCESS] Batch test data generated: {output_path}")
 print(f" - Record count: {len(batch_data)}")
 print(f" - Fields: {list(batch_data.columns)}")
 return output_path

def generate_performance_test_data():
 """Generate performance test data (1000 records)"""
 print("Generating performance test data...")
 performance_data = generate_credit_data(1000, seed=456, include_target=True)

 output_path = Path(__file__).parent.parent / "test_data_performance.csv"
 performance_data.to_csv(output_path, index=False)

 print(f"[SUCCESS] Performance test data generated: {output_path}")
 print(f" - Record count: {len(performance_data)}")
 print(f" - Fields: {list(performance_data.columns)}")
 return output_path

def generate_anomaly_test_data():
 """Generate test set containing anomalous data"""
 print("Generating anomalous data test set...")
 # First generate normal data
 normal_data = generate_credit_data(8, seed=789, include_target=True)

 # Add anomalous data
 anomaly_records = {
 'customer_id': ['CUST_999991', 'CUST_999992'],
 'age': [-5, 200], # Anomalous ages
 'income': [50000, 80000],
 'employment_years': [5, 3],
 'debt_ratio': [0.3, 0.4],
 'credit_history': ['good', 'fair'],
 'target': [0, 1]
 }

 anomaly_df = pd.DataFrame(anomaly_records)
 combined_data = pd.concat([normal_data, anomaly_df], ignore_index=True)

 output_path = Path(__file__).parent.parent / "test_data_anomaly.csv"
 combined_data.to_csv(output_path, index=False)

 print(f"[SUCCESS] Anomalous data test set generated: {output_path}")
 print(f" - normal records: {len(normal_data)}")
 print(f" - Anomalous records: {len(anomaly_df)}")
 return output_path

def generate_type_error_test_data():
 """Generate test set containing type errors"""
 print("Generating type error test set...")
 # Create data containing type errors
 type_error_data = {
 'customer_id': ['CUST_000001', 'CUST_000002', 'CUST_000003'],
 'age': [25, 'invalid_age', 35], # Age field contains text
 'income': ['not_number', 55000, 75000], # Income field contains text
 'employment_years': [3, 5, 'unknown'], # Employment years contains text
 'debt_ratio': [0.3, 0.2, 0.4],
 'credit_history': ['good', 'excellent', 'fair'],
 'target': [1, 0, 1]
 }

 type_error_df = pd.DataFrame(type_error_data)

 output_path = Path(__file__).parent.parent / "test_data_type_error.csv"
 type_error_df.to_csv(output_path, index=False)

 print(f"[SUCCESS] Type error test set generated: {output_path}")
 print(f" - Record count: {len(type_error_df)}")
 return output_path

def main():
 """Main function"""
 parser = argparse.ArgumentParser(description='Generate test data')
 parser.add_argument('--type', choices=['batch', 'performance', 'anomaly', 'type_error', 'all'],
 default='all', help='Type of data to generate')

 args = parser.parse_args()

 print("=== Large Batch Test data Generator ===")

 if args.type in ['batch', 'all']:
 generate_batch_test_data()

 if args.type in ['performance', 'all']:
 generate_performance_test_data()

 if args.type in ['anomaly', 'all']:
 generate_anomaly_test_data()

 if args.type in ['type_error', 'all']:
 generate_type_error_test_data()

 print("\nData generation completed successfully!")

if __name__ == "__main__":
 main()