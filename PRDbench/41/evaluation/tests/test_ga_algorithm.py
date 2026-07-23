import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from GA import GA

def test_ga_execution():
    """Test genetic algorithm execution"""
    # Prepare test data
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

def test_ga_with_different_sequences():
    """Test genetic algorithm with different sequences"""
    query = "ATCG"
    target = "GCTA"

    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)

    assert cost is not None
    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

def test_ga_parameters():
    """Test genetic algorithm parameter configuration"""
    query = "ATCG"
    target = "GCTA"

    # Test with different parameter configurations
    cost1, out_a1, out_b1 = GA(query, target, 1.2, 10, 5, 2)
    cost2, out_a2, out_b2 = GA(query, target, 1.5, 30, 15, 5)

    # Both runs should succeed
    assert cost1 >= 0
    assert cost2 >= 0
    assert out_a1 is not None
    assert out_a2 is not None
    assert out_b1 is not None
    assert out_b2 is not None

def test_ga_performance():
    """Test genetic algorithm performance"""
    import time

    query = "ATCGATCG"
    target = "GCTAGCTA"

    start_time = time.time()
    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)
    end_time = time.time()

    execution_time = end_time - start_time

    # Verify algorithm completes within reasonable time
    assert execution_time < 5.0  # Should complete within 5 seconds
    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

def test_ga_convergence():
    """Test genetic algorithm convergence"""
    query = "ATCG"
    target = "ATCG"

    # Identical sequences should converge to relatively low cost
    cost, out_a, out_b = GA(query, target, 1.2, 50, 20, 5)

    assert cost >= 0
    assert cost < 10  # Identical sequences should have relatively low cost
    assert out_a is not None
    assert out_b is not None

def test_ga_edge_cases():
    """Test genetic algorithm edge cases"""
    # Test short sequences
    query = "AT"
    target = "GC"

    cost, out_a, out_b = GA(query, target, 1.2, 10, 5, 2)

    assert cost >= 0
    assert out_a is not None
    assert out_b is not None

    # Test longer sequences
    query = "ATCGATCGATCGATCG"
    target = "GCTAGCTAGCTAGCTA"

    cost, out_a, out_b = GA(query, target, 1.2, 20, 10, 3)

    assert cost >= 0
    assert out_a is not None
    assert out_b is not None
