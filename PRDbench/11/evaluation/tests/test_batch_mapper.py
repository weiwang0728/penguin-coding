import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import batch_map_replace


def test_batch_mapper_replacer():
    """Test batch mapper & replacer functionality"""
    # Arrange: Prepare a data list and a mapping dictionary
    data = ['A', 'B', 'C']
    mapping = {'A': 'Apple', 'B': 'Banana'}

    # Act: Call batch_mapper(data, mapping)
    result = batch_map_replace(data, mapping)

    # Assert: Verify that the returned list is ['Apple', 'Banana', 'C']
    expected = ['Apple', 'Banana', 'C']
    assert result == expected, f"batch_map_replace({data}, {mapping}) should return {expected}, but got {result}"

    # Additional test: Test dict data
    dict_data = {'x': 'A', 'y': 'B', 'z': 'D'}
    dict_result = batch_map_replace(dict_data, mapping)
    dict_expected = {'x': 'Apple', 'y': 'Banana', 'z': 'D'}
    assert dict_result == dict_expected, f"Dict batch mapping failed"

    # Additional test: Test single value
    single_result = batch_map_replace('A', mapping)
    assert single_result == 'Apple', "Single value mapping failed"

    # Test non-existent mapping
    single_result2 = batch_map_replace('D', mapping)
    assert single_result2 == 'D', "Non-existent mapping should keep original value"