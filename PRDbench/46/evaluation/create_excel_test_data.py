#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Excel Format Test data File
"""

import pandas as pd
import numpy as np

# Create Excel test data
np.random.seed(42)
data = []
for i in range(120): # Exceeds 100 row requirement
 record = {
 'age': np.random.randint(18, 70),
 'income': np.random.randint(20000, 150000),
 'employment_years': np.random.randint(0, 30),
 'debt_ratio': max(0.05, np.random.random() * 0.8),
 'credit_history': np.random.choice(['excellent', 'good', 'fair', 'poor']),
 'target': np.random.choice([0, 1])
 }
 data.append(record)

df = pd.DataFrame(data)

# Save as Excel file
df.to_excel('evaluation/test_data_excel.xlsx', index=False)

print(f"Created Excel test data: {len(df)} rows")
print(f"File: evaluation/test_data_excel.xlsx")
print(f"Column names: {list(df.columns)}")