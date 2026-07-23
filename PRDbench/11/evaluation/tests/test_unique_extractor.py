import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import extract_unique


def test_unique_list_extractor():
    """Test unique list extractor functionality"""
    # Arrange: Prepare a list with duplicate elements
    data = ['a', 'b', 'a', 'c', 'b']

    # Act: Call unique_list_extractor(data)
    result = extract_unique(data)

    # Assert: Verify that the returned list is ['a', 'b', 'c'], and strictly maintains the original order of first occurrence for each element
    expected = ['a', 'b', 'c']
    assert result == expected, f"extract_unique({data}) should return {expected}, but got {result}"

    # Additional test: Test empty list
    assert extract_unique([]) == [], "Empty list should return empty list"

    # Additional test: Test list with no duplicates
    unique_data = [1, 2, 3]
    assert extract_unique(unique_data) == unique_data, "List with no duplicates should remain unchanged"