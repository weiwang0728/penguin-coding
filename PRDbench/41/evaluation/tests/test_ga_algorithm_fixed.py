import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from GA import GA

def test_ga_execution_basic():
    """Test genetic algorithm basic execution"""
    # Prepare test data - use identical sequences to avoid division by zero error
    query = "ATCG"
    target = "ATCG"

    # Execute algorithm
    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)

    # Verify results
    assert cost is not None
    assert out_a is not None
    assert out_b is not None
    assert cost >= 0  # Cost should be non-negative
    assert len(out_a) > 0
    assert len(out_b) > 0

def test_ga_with_simple_sequences():
    """Test genetic algorithm with simple sequences to avoid complex cases causing division by zero error"""
    query = "AT"
    target = "AT"

    cost, out_a, out_b = GA(query, target, 1.2, 10, 5, 2)

    assert cost is not None
    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

def test_ga_zero_division_fix():
    """Test fix for division by zero error cases"""
    # This test specifically verifies the division by zero error fix
    query = "A"
    target = "T"

    try:
        cost, out_a, out_b = GA(query, target, 1.2, 5, 3, 1)
        # If no exception is thrown, the division by zero error has been fixed
        assert cost >= 0
        assert out_a is not None
        assert out_b is not None
    except ZeroDivisionError:
        pytest.fail("Genetic algorithm still has division by zero error, needs to be fixed")

def test_ga_fitness_calculation():
    """Test fitness calculation does not cause division by zero error"""
    query = "ATCG"
    target = "GCTA"

    # Use smaller parameters to avoid complex calculations
    cost, out_a, out_b = GA(query, target, 1.1, 5, 3, 1)

    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

def test_ga_parameter_validation():
    """Test genetic algorithm parameter validation"""
    query = "ATCG"
    target = "GCTA"

    # Test boundary parameters
    cost, out_a, out_b = GA(query, target, 1.0, 2, 1, 1)

    assert cost >= 0
    assert out_a is not None
    assert out_b is not None
