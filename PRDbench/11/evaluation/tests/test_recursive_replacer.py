import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import recursive_replace


def test_recursive_replacer():
    """Test recursive replacer functionality"""
    # Arrange: Prepare a nested list, replacement target and replacement value
    data = [1, [2, 1, [3, 1]]]
    target = 1
    replacement = 'X'

    # Act: Call recursive_replacer(data, target, replacement)
    result = recursive_replace(data, target, replacement)

    # Assert: Verify that the returned list is ['X', [2, 'X', [3, 'X']]]
    expected = ['X', [2, 'X', [3, 'X']]]
    assert result == expected, f"recursive_replace({data}, {target}, {replacement}) should return {expected}, but got {result}"

    # Additional test: Test dict structure
    dict_data = {'a': 1, 'b': {'c': 1, 'd': 2}}
    dict_result = recursive_replace(dict_data, 1, 'X')
    dict_expected = {'a': 'X', 'b': {'c': 'X', 'd': 2}}
    assert dict_result == dict_expected, f"Dict recursive replacement failed"

    # Additional test: Test single value
    single_result = recursive_replace(1, 1, 'X')
    assert single_result == 'X', "Single value replacement failed"