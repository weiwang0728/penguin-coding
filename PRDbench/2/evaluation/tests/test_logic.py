import pandas as pd
import pytest
from src.analysis import filter_by_market_cap, variance_decomposition, analyze_dimension

@pytest.fixture
def sample_df():
    """Provides a sample DataFrame for testing."""
    data = {
        'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JPM', 'V', 'JNJ', 'PFE', 'MRNA'],
        'CompanyName': ['Apple', 'Microsoft', 'Alphabet', 'Amazon', 'Tesla', 'JPMorgan', 'Visa', 'Johnson & Johnson', 'Pfizer', 'Moderna'],
        'Industry': ['Technology', 'Technology', 'Technology', 'Technology', 'Technology', 'Financials', 'Financials', 'Healthcare', 'Healthcare', 'Healthcare'],
        'Sector': ['Technology', 'Technology', 'Technology', 'Technology', 'Technology', 'Financials', 'Financials', 'Healthcare', 'Healthcare', 'Healthcare'],
        'PE': [28.5, 35.2, 30.1, 60.3, 150.1, 12.5, 40.1, 25.5, 15.8, 80.2],
        'Market Value': [2.8e12, 2.5e12, 1.8e12, 1.6e12, 1.1e12, 4.5e11, 5.0e11, 4.8e11, 2.5e11, 1.5e11]
    }
    return pd.DataFrame(data)

def test_market_cap_preset_filter(sample_df):
    """
    Tests the preset market cap filter for 'Large-cap'.
    PRD Definition: MarketCap >= 10 billion (1e10)
    """
    # In our sample_df, all stocks are 'Large-cap'
    filtered_df, error = filter_by_market_cap(sample_df, category='Large-cap')
    assert error is None
    assert not filtered_df.empty
    assert all(filtered_df['Market Value'] >= 1e10)
    # Test a category that should yield no results
    filtered_df_small, error = filter_by_market_cap(sample_df, category='Small-cap')
    assert error is None
    assert filtered_df_small.empty

def test_variance_decomposition(sample_df):
    """
    Tests the variance decomposition calculation.
    We don't check the exact values, but ensure the process runs and returns a correctly structured result.
    """
    target_metric = 'PE'
    dimensions = ['Industry', 'Sector']
    anova_table, error = variance_decomposition(sample_df, target_metric, dimensions)
    
    assert error is None
    assert isinstance(anova_table, pd.DataFrame)
    assert 'contribution_%' in anova_table.columns
    assert 'sum_sq' in anova_table.columns
    # The sum of contributions should be close to 100
    assert abs(anova_table['contribution_%'].sum() - 100.0) < 1e-9

def test_deep_dive_analysis(sample_df):
    """
    Tests the deep-dive analysis on the highest contributing dimension.
    """
    target_metric = 'PE'
    dimension = 'Industry'
    analysis_df, error = analyze_dimension(sample_df, target_metric, dimension)
    
    assert error is None
    assert isinstance(analysis_df, pd.DataFrame)
    assert f'{target_metric}_mean' in analysis_df.columns
    assert f'{target_metric}_std' in analysis_df.columns
    assert not analysis_df.empty
    # Check if the calculation for 'Technology' is correct
    tech_pe = sample_df[sample_df['Industry'] == 'Technology']['PE']
    expected_mean = tech_pe.mean()
    calculated_mean = analysis_df[analysis_df['Industry'] == 'Technology'][f'{target_metric}_mean'].iloc[0]
    assert abs(expected_mean - calculated_mean) < 1e-9
