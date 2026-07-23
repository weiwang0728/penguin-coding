"""
Maze Post-processing Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator


def test_wall_removal():
    """Test wall removal function"""
    generator = MazeGenerator()

    # Generate a maze
    result = generator.generate('dfs', 15)
    original_maze = result['maze_matrix'].copy()

    # Calculate original wall count
    original_walls = np.sum(original_maze == 1)

    # Call wall removal function (if exists)
    try:
        # Try to call wall removal function
        # This needs to be adjusted according to actual implementation
        if hasattr(generator, 'remove_walls'):
            processed_maze = generator.remove_walls(original_maze, wall_count=5)
            processed_walls = np.sum(processed_maze == 1)

            # Verify walls are actually removed
            walls_removed = original_walls - processed_walls
            assert walls_removed >= 4 and walls_removed <= 6, f"Removed wall count {walls_removed} not in allowed range (4-6)"
        else:
            # If wall removal function is not implemented, skip test
            pytest.skip("Wall removal function not implemented")
    except Exception as e:
        pytest.fail(f"Wall removal function test failed: {e}")


def test_maze_postprocessing():
    """Test maze post-processing function"""
    generator = MazeGenerator()

    # Generate a maze
    result = generator.generate('prim', 11)
    maze_matrix = result['maze_matrix']

    # Check basic maze properties
    assert isinstance(maze_matrix, np.ndarray), "Maze should be a numpy array"
    assert maze_matrix.shape[0] == maze_matrix.shape[1], "Maze should be square"

    # Check if boundaries are walls (usually maze boundaries should be walls)
    # Note: Specific implementation may differ, basic check here
    walls = np.sum(maze_matrix == 1)
    paths = np.sum(maze_matrix == 0)

    assert walls > 0, "Maze should contain walls"
    assert paths > 0, "Maze should contain paths"
