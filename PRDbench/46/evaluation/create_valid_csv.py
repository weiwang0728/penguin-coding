#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create CSV Test data Meeting System Validation Requirements
"""

import pandas as pd
import numpy as np

# Set random seed to ensure reproducible result s
np.random.seed(42)

# Generate data meeting validation requirements
data = []
for i in range(150): # Generate 150 rows of data (exceeds 100 row minimum requirement)
 record = {
 'age': np.random.randint(18, 70),
 'income': np.random.randint(20000, 150000),
 'employment_years': np.random.randint(0, 30),
 'debt_ratio': max(0.05, np.random.random() * 0.8), # Ensure greater than 0.01
 'credit_history': np.random.choice(['excellent', 'good', 'fair', 'poor']),
 'target': np.random.choice([0, 1]) # Add target column
 }
 data.append(record)

# Create DataFrame and save
df = pd.DataFrame(data)
df.to_csv('evaluation/test_data_csv.csv', index=False)

print(f"Generated CSV data meeting validation requirements: {len(df)} rows")
print(f"Column names: {list(df.columns)}")
print(f"debt_ratio range: {df['debt_ratio'].min():.4f} - {df['debt_ratio'].max():.4f}")