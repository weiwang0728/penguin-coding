#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix CSV Target Column Name
"""

import pandas as pd

# Read previous CSV file
df = pd.read_csv('evaluation/test_data_csv.csv')

# Rename target column to "target"
if 'target' in df.columns:
 df = df.rename(columns={'target': 'target'})
 print("Column 'target' renamed to 'target'")

# Save modified file
df.to_csv('evaluation/test_data_csv.csv', index=False)

print(f"Modification completed successfully: {len(df)} rows of data")
print(f"Column names: {list(df.columns)}")