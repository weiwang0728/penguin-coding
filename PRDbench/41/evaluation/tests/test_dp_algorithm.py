import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from DP import DP

def test_dp_execution():
    """Test dynamic programming algorithm execution"""
    # Prepare test data
    query = "ATCG"
    target = "ATCG"

    # Execute algorithm
    aligned_query, aligned_target, cost_matrix = DP(query, target)

    # Verify results
    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix is not None
    assert len(aligned_query) > 0
    assert len(aligned_target) > 0
    assert cost_matrix[0][0] >= 0  # Cost should be non-negative

def test_dp_with_different_sequences():
    """Test dynamic programming algorithm with different sequences"""
    query = "ATCG"
    target = "GCTA"

    aligned_query, aligned_target, cost_matrix = DP(query, target)

    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix[0][0] > 0  # Different sequences should have positive cost

def test_dp_empty_sequences():
    """Test empty sequence processing"""
    query = ""
    target = "ATCG"

    aligned_query, aligned_target, cost_matrix = DP(query, target)

    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix is not None

def test_dp_identical_sequences():
    """Test identical sequence processing"""
    query = "ATCGATCG"
    target = "ATCGATCG"

    aligned_query, aligned_target, cost_matrix = DP(query, target)

    assert aligned_query == target
    assert aligned_target == query
    assert cost_matrix[0][0] == 0  # Identical sequences should have zero cost

def test_dp_performance():
    """Test dynamic programming algorithm performance"""
    import time

    query = "ATCGATCGATCGATCG"
    target = "GCTAGCTAGCTAGCTA"

    start_time = time.time()
    aligned_query, aligned_target, cost_matrix = DP(query, target)
    end_time = time.time()

    execution_time = end_time - start_time

    # Verify algorithm completes within reasonable time
    assert execution_time < 1.0  # Should complete within 1 second
    assert aligned_query is not None
    assert aligned_target is not None
    assert cost_matrix[0][0] >= 0
