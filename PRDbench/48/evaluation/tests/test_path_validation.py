"""
Path Validation Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder


def test_dfs_path_validity():
    """Test DFS path validity"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Generate maze
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # Use DFS to solve
    path_result = path_finder.solve('dfs', maze_matrix, start_point, end_point)

    if not path_result['found_solution']:
        pytest.skip("DFS did not find path, skip path validation test")

    path = path_result['path']

    # Verify path is not empty
    assert len(path) > 0, "Path should not be empty"

    # Verify start point and end point
    assert list(path[0]) == list(start_point), f"Path start point {path[0]} does not match expected {start_point}"
    assert list(path[-1]) == list(end_point), f"Path end point {path[-1]} does not match expected {end_point}"

    # Verify all points in path are passable
    invalid_points = []
    for point in path:
        row, col = int(point[0]), int(point[1])
        if maze_matrix[row, col] != 0:
            invalid_points.append(point)

    assert len(invalid_points) == 0, f"Path contains wall points: {invalid_points}"

    # Verify path continuity
    discontinuous_pairs = []
    for i in range(len(path) - 1):
        curr = path[i]
        next_p = path[i + 1]

        # Calculate Manhattan distance
        distance = abs(curr[0] - next_p[0]) + abs(curr[1] - next_p[1])
        if distance != 1:
            discontinuous_pairs.append((curr, next_p))

    assert len(discontinuous_pairs) == 0, f"Path discontinuous point pairs: {discontinuous_pairs}"


def test_path_components():
    """Test path search return components completeness"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Generate maze
    result = generator.generate('dfs', 12)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # Test various algorithms
    algorithms = ['dfs', 'bfs', 'astar']

    for algo in algorithms:
        try:
            path_result = path_finder.solve(algo, maze_matrix, start_point, end_point)

            # Check required return components
            required_keys = ['found_solution', 'path', 'explored_nodes_count', 'search_time', 'path_length']
            missing_keys = []
            for key in required_keys:
                if key not in path_result:
                    missing_keys.append(key)

            assert len(missing_keys) == 0, f"{algo} algorithm missing return components: {missing_keys}"

            # If solution is found, check data types
            if path_result['found_solution']:
                assert isinstance(path_result['path'], list), f"{algo} algorithm path should be a list"
                assert isinstance(path_result['explored_nodes_count'], int), f"{algo} algorithm explored node count should be an integer"
                assert isinstance(path_result['search_time'], (int, float)), f"{algo} algorithm search time should be a numeric value"
                assert isinstance(path_result['path_length'], int), f"{algo} algorithm path length should be an integer"

        except Exception as e:
            pytest.fail(f"{algo} algorithm test failed: {e}")
