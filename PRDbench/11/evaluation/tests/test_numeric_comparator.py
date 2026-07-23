import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import compare_numbers


def test_numeric_comparator():
    """Test numeric comparator functionality"""
    # Arrange: Prepare three sets of input data: (a=5, b=10), (a=10, b=5), (a=5, b=5)
    test_cases = [
        (5, 10, -1),  # a < b should return -1
        (10, 5, 1),   # a > b should return 1
        (5, 5, 0)     # a == b should return 0
    ]

    # Act and Assert
    for a, b, expected in test_cases:
        result = compare_numbers(a, b)
        assert result == expected, f"compare_numbers({a}, {b}) should return {expected}, but got {result}"