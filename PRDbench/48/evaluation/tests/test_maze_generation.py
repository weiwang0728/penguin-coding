"""
Maze Generation Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder


def test_dfs_connectivity():
    """Test DFS maze connectivity"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    connected_count = 0
    total_tests = 5

    for i in range(total_tests):
        # Generate maze
        result = generator.generate('dfs', 10)

        maze_matrix = result['maze_matrix']
        start_point = result['start_point']
        end_point = result['end_point']

        # Check connectivity
        path_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)

        if path_result['found_solution']:
            connected_count += 1

    # At least 4 mazes should be connected
    assert connected_count >= 4, f"Only {connected_count}/{total_tests} mazes are connected"


def test_prim_connectivity():
    """Test PRIM maze connectivity"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    connected_count = 0
    total_tests = 5

    for i in range(total_tests):
        # Generate maze
        result = generator.generate('prim', 10)

        maze_matrix = result['maze_matrix']
        start_point = result['start_point']
        end_point = result['end_point']

        # Check connectivity
        path_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)

        if path_result['found_solution']:
            connected_count += 1

    # At least 4 mazes should be connected
    assert connected_count >= 4, f"Only {connected_count}/{total_tests} mazes are connected"


def test_maze_format():
    """Test maze format correctness"""
    generator = MazeGenerator()

    # Test DFS
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']

    # Check type and shape
    assert isinstance(maze_matrix, np.ndarray), "Maze matrix should be a numpy array"
    assert maze_matrix.dtype == np.uint8, f"Data type should be uint8, actually is {maze_matrix.dtype}"
    assert len(maze_matrix.shape) == 2, "Maze should be a 2D array"

    # Check value range
    unique_values = np.unique(maze_matrix)
    assert all(val in [0, 1] for val in unique_values), f"Maze values should only contain 0 and 1, actually contains {unique_values}"

    # Check required return components
    required_keys = ['maze_matrix', 'generation_time', 'start_point', 'end_point']
    for key in required_keys:
        assert key in result, f"Missing required return component: {key}"
