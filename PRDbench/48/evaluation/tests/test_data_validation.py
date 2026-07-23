"""
Data Validation Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_validator import MazeValidator


def test_format_validation():
    """Test maze format validation"""
    validator = MazeValidator()

    # Prepare 3 types of invalid maze matrices

    # 1. Matrix containing values other than 0 and 1
    invalid_values_maze = np.array([
        [0, 1, 0],
        [1, 2, 0],  # Contains value 2
        [0, 1, 0]
    ], dtype=np.uint8)

    # 2. Matrix with wrong data type
    wrong_type_maze = np.array([
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0]
    ], dtype=np.float32)  # Should be uint8

    # 3. Matrix with incorrect shape (non-square)
    wrong_shape_maze = np.array([
        [0, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 0, 1]
    ], dtype=np.uint8)  # 3x4 instead of square

    invalid_mazes = [
        (invalid_values_maze, "Contains values other than 0 and 1"),
        (wrong_type_maze, "Wrong data type"),
        (wrong_shape_maze, "Incorrect shape")
    ]

    # Verify ability to identify all format errors
    identified_errors = 0

    for maze, description in invalid_mazes:
        try:
            result = validator.validate(maze, [0, 0], [2, 2])
            if not result['valid']:
                identified_errors += 1
                print(f"Correctly identified error: {description}")
            else:
                print(f"Failed to identify error: {description}")
        except Exception as e:
            # If an exception is thrown, it also counts as identifying the error
            identified_errors += 1
            print(f"Identified error through exception: {description} - {e}")

    # Should identify at least 2 types of errors
    assert identified_errors >= 2, f"Only identified {identified_errors}/3 types of format errors"


def test_connectivity_validation():
    """Test connectivity validation"""
    validator = MazeValidator()

    # Create a disconnected maze
    disconnected_maze = np.array([
        [0, 1, 0, 1, 0],
        [1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 1, 0]
    ], dtype=np.uint8)

    start_point = [0, 0]  # Top-left corner
    end_point = [0, 4]    # Top-right corner (blocked by walls)

    # Verify ability to identify connectivity issues
    result = validator.validate(disconnected_maze, start_point, end_point)

    # Should identify connectivity issue
    assert not result['valid'], "Should identify connectivity issue"

    # Check if error information is provided
    assert 'errors' in result, "Should contain error information"

    # Create a connected maze for comparison
    connected_maze = np.array([
        [0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0]
    ], dtype=np.uint8)

    # Validate connected maze
    result2 = validator.validate(connected_maze, [0, 0], [4, 4])

    # Connected maze should pass validation
    assert result2['valid'], "Connected maze should pass validation"


def test_validation_components():
    """Test validation function return components completeness"""
    validator = MazeValidator()

    # Create a normal maze
    normal_maze = np.array([
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0]
    ], dtype=np.uint8)

    result = validator.validate(normal_maze, [0, 0], [4, 4])

    # Check return components
    required_keys = ['valid', 'errors']
    missing_keys = []

    for key in required_keys:
        if key not in result:
            missing_keys.append(key)

    assert len(missing_keys) == 0, f"Missing required return components: {missing_keys}"

    # Check data types
    assert isinstance(result['valid'], bool), "valid field should be a boolean value"
    assert isinstance(result['errors'], list), "errors field should be a list"
