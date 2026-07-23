"""
Error Handling Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder
from maze_validator import MazeValidator


def test_exception_handling():
    """Test exception input handling"""
    generator = MazeGenerator()
    path_finder = PathFinder()
    validator = MazeValidator()

    # Prepare 5 types of exception inputs
    test_cases = [
        {
            'name': 'Negative maze size',
            'test_func': lambda: generator.generate('dfs', -5),
            'should_handle': True
        },
        {
            'name': 'Start point coordinate out of bounds',
            'test_func': lambda: test_invalid_coordinates(),
            'should_handle': True
        },
        {
            'name': 'Invalid maze matrix (contains strings)',
            'test_func': lambda: test_string_matrix(),
            'should_handle': True
        },
        {
            'name': 'Empty maze matrix',
            'test_func': lambda: test_empty_matrix(),
            'should_handle': True
        },
        {
            'name': 'Wrong data type',
            'test_func': lambda: test_wrong_data_type(),
            'should_handle': True
        }
    ]

    handled_exceptions = 0

    for test_case in test_cases:
        try:
            # Try to execute operations that might cause exceptions
            test_case['test_func']()
            # If no exception is thrown, check if it should handle
            print(f"✓ {test_case['name']}: No exception thrown (may be gracefully handled)")
            handled_exceptions += 1
        except Exception as e:
            # Check if exception is gracefully handled (meaningful error message)
            error_message = str(e)
            if len(error_message) > 0 and not "Traceback" in error_message:
                print(f"✓ {test_case['name']}: Gracefully handled exception - {error_message}")
                handled_exceptions += 1
            else:
                print(f"✗ {test_case['name']}: Exception not gracefully handled - {e}")

    # Should gracefully handle at least 4 types of exceptions
    assert handled_exceptions >= 4, f"Only gracefully handled {handled_exceptions}/5 types of exception inputs"


def test_invalid_coordinates():
    """Test invalid coordinate handling"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Generate a normal maze
    result = generator.generate('dfs', 10)
    maze_matrix = result['maze_matrix']

    # Test coordinates out of bounds
    invalid_start = [20, 20]  # Out of bounds for 10x10 maze
    valid_end = [5, 5]

    # This should be gracefully handled
    path_result = path_finder.solve('bfs', maze_matrix, invalid_start, valid_end)

    # Check if gracefully handled (return solution not found instead of crashing)
    assert 'found_solution' in path_result, "Should return found_solution field"
    # Normally coordinates out of bounds should lead to solution not found
    assert not path_result['found_solution'], "Coordinates out of bounds should lead to solution not found"


def test_string_matrix():
    """Test string matrix handling"""
    validator = MazeValidator()

    # Create a "maze" containing strings
    string_matrix = [
        ['0', '1', '0'],
        ['1', 'wall', '0'],
        ['0', '1', '0']
    ]

    # This should be detected as invalid format
    result = validator.validate(string_matrix, [0, 0], [2, 2])

    # Should be identified as invalid
    assert 'valid' in result, "Should return valid field"
    assert not result['valid'], "String matrix should be identified as invalid"


def test_empty_matrix():
    """Test empty matrix handling"""
    path_finder = PathFinder()

    # Empty matrix
    empty_matrix = np.array([])

    try:
        result = path_finder.solve('dfs', empty_matrix, [0, 0], [1, 1])
        # If no exception is thrown, check if gracefully handled
        assert 'found_solution' in result, "Should return found_solution field"
        assert not result['found_solution'], "Empty matrix should lead to solution not found"
    except Exception as e:
        # If exception is thrown, check if error message is meaningful
        error_msg = str(e)
        assert len(error_msg) > 5, f"Error message too brief: {error_msg}"


def test_wrong_data_type():
    """Test wrong data type handling"""
    generator = MazeGenerator()

    # Test string as size parameter
    try:
        result = generator.generate('dfs', "ten")
        # If no exception is thrown, should have error flag
        assert 'error' in result or 'maze_matrix' not in result, "Should identify wrong data type"
    except Exception as e:
        # Check error message quality
        error_msg = str(e)
        assert len(error_msg) > 5, f"Error message too brief: {error_msg}"


def test_algorithm_error_handling():
    """Test algorithm error handling"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Test non-existent algorithms
    invalid_algorithms = ['xyz', 'invalid', '']

    handled_count = 0

    for algo in invalid_algorithms:
        try:
            # Generation algorithm test
            gen_result = generator.generate(algo, 10)
            if 'error' in gen_result or 'maze_matrix' not in gen_result:
                handled_count += 1
        except Exception as e:
            if len(str(e)) > 0:  # Meaningful error message
                handled_count += 1

        try:
            # Create a test maze
            valid_result = generator.generate('dfs', 10)
            maze_matrix = valid_result['maze_matrix']

            # Path search algorithm test
            path_result = path_finder.solve(algo, maze_matrix, [1, 1], [5, 5])
            if 'error' in path_result or not path_result.get('found_solution', True):
                handled_count += 1
        except Exception as e:
            if len(str(e)) > 0:  # Meaningful error message
                handled_count += 1

    # Should be able to handle most invalid algorithm requests
    assert handled_count >= 4, f"Only handled {handled_count}/6 invalid algorithm requests"
