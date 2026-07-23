import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import filter_data


def test_conditional_filter():
    """Test conditional filter functionality"""
    # Arrange: Prepare a data list and a custom condition function
    data = [1, 2, 3, 4, 5, 6]

    def is_even(n):
        """Condition function to determine if a number is even"""
        return n % 2 == 0

    # Act: Call conditional_filter(data, is_even)
    result = filter_data(data, is_even)

    # Assert: Verify that the returned list is [2, 4, 6]
    expected = [2, 4, 6]
    assert result == expected, f"filter_data({data}, is_even) should return {expected}, but got {result}"