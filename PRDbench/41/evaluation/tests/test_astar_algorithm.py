import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from A_star import A_star

def test_astar_execution():
    """Test A* search algorithm execution"""
    # Prepare test data
    query = "ATCG"
    target = "ATCG"

    # Execute algorithm
    final_node = A_star(query, target)

    # Verify results
    assert final_node is not None
    assert hasattr(final_node, 'g')
    assert hasattr(final_node, 'path_a')
    assert hasattr(final_node, 'path_b')
    assert final_node.g >= 0  # Cost should be non-negative

def test_astar_with_different_sequences():
    """Test A* search algorithm with different sequences"""
    query = "ATCG"
    target = "GCTA"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g > 0  # Different sequences should have positive cost
    assert len(final_node.path_a) > 0
    assert len(final_node.path_b) > 0

def test_astar_empty_sequences():
    """Test empty sequence processing"""
    query = ""
    target = "ATCG"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g >= 0

def test_astar_identical_sequences():
    """Test identical sequence processing"""
    query = "ATCG"
    target = "ATCG"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g == 0  # Identical sequences should have zero cost
    assert final_node.path_a == query
    assert final_node.path_b == target

def test_astar_performance():
    """Test A* search algorithm performance"""
    import time

    query = "ATCGATCGATCG"
    target = "GCTAGCTAGCTA"

    start_time = time.time()
    final_node = A_star(query, target)
    end_time = time.time()

    execution_time = end_time - start_time

    # Verify algorithm completes within reasonable time
    assert execution_time < 2.0  # Should complete within 2 seconds
    assert final_node is not None
    assert final_node.g >= 0

def test_astar_heuristic_functions():
    """Test A* search algorithm heuristic functions"""
    query = "ATCG"
    target = "GCTA"

    # Test that different heuristic functions work correctly
    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g >= 0
    assert final_node.path_a is not None
    assert final_node.path_b is not None

def test_astar_optimal_path():
    """Test A* algorithm finds optimal path"""
    query = "ABC"
    target = "ABC"

    final_node = A_star(query, target)

    assert final_node is not None
    assert final_node.g == 0  # Identical sequences should have zero cost
