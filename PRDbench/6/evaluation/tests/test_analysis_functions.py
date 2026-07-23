
import pandas as pd
import numpy as np
import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from data_processor import handle_missing_values_fill
from analysis import get_descriptive_stats, detect_outliers_iqr

# Test for 3.2a - Mean Fill
def test_fill_missing_with_mean():
    df = pd.DataFrame({'Value': [1, 2, np.nan, 5]})
    # mean is (1+2+5)/3 = 2.666...
    result_df = handle_missing_values_fill(df, 'Value', 'mean')
    assert result_df['Value'].isnull().sum() == 0
    assert np.isclose(result_df.loc[2, 'Value'], 2.666667, atol=1e-5)

# Test for 3.2b - Median Fill
def test_fill_missing_with_median():
    df = pd.DataFrame({'Value': [1, 2, np.nan, 5, 10]})
    # median is (2+5)/2 = 3.5
    result_df = handle_missing_values_fill(df, 'Value', 'median')
    assert result_df['Value'].isnull().sum() == 0
    assert result_df.loc[2, 'Value'] == 3.5

# Test for 3.2c - Mode Fill
def test_fill_missing_with_mode():
    df = pd.DataFrame({'Category': ['A', 'B', np.nan, 'B', 'C']})
    result_df = handle_missing_values_fill(df, 'Category', 'mode')
    assert result_df['Category'].isnull().sum() == 0
    assert result_df.loc[2, 'Category'] == 'B'

# Test for 3.3 - IQR Outlier Detection
def test_detect_outliers_iqr():
    df = pd.DataFrame({'Value': [1, 10, 12, 11, 13, 9, 100]})
    outliers = detect_outliers_iqr(df, 'Value')
    assert 100 in outliers['Value'].values
    assert len(outliers) == 1

# Test for 4.1a - Descriptive Stats (Numeric - Central Tendency)
def test_descriptive_stats_numeric_central():
    df = pd.DataFrame({'Value': [1, 2, 3, 4, 5]})
    stats = get_descriptive_stats(df, 'Value')
    assert stats['mean'] == 3.0
    assert stats['median'] == 3.0

# Test for 4.1b - Descriptive Stats (Numeric - Dispersion)
def test_descriptive_stats_numeric_dispersion():
    df = pd.DataFrame({'Value': [1, 2, 3, 4, 5]})
    stats = get_descriptive_stats(df, 'Value')
    assert np.isclose(stats['std'], 1.581138, atol=1e-5)
    assert stats['range'] == 4
    assert stats['quartiles']['25%'] == 2.0
    assert stats['quartiles']['75%'] == 4.0

# Test for 4.2a - Descriptive Stats (Categorical - Frequency)
def test_descriptive_stats_categorical_freq():
    df = pd.DataFrame({'Category': ['A', 'B', 'A', 'A', 'C']})
    stats = get_descriptive_stats(df, 'Category')
    assert stats['counts'] == {'A': 3, 'B': 1, 'C': 1}
    assert stats['frequencies'] == {'A': 0.6, 'B': 0.2, 'C': 0.2}

# Test for 4.2b - Descriptive Stats (Categorical - Mode/Unique)
def test_descriptive_stats_categorical_mode_unique():
    df = pd.DataFrame({'Category': ['A', 'B', 'A', 'A', 'C']})
    stats = get_descriptive_stats(df, 'Category')
    assert stats['mode'] == 'A'
    assert stats['unique_count'] == 3
