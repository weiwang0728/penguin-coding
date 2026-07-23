import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from utils import create_adder


def test_dynamic_adder_generator():
    """Test dynamic adder generator functionality"""
    # Arrange: Prepare a base addend
    base_add = 10

    # Act: Call dynamic_adder_generator(base_add) to generate a new addition function
    adder_func = create_adder(base_add)
    result = adder_func(5)

    # Assert: Verify that the return value of adder_func(5) is 15
    expected = 15
    assert result == expected, f"Dynamically generated addition function should return {expected}, but got {result}"

    # Additional test: Verify the function is indeed reusable
    assert adder_func(0) == 10, "adder_func(0) should return 10"
    assert adder_func(-5) == 5, "adder_func(-5) should return 5"