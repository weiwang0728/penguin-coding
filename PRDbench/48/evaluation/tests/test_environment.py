"""
Environment Validation Test
"""
import pytest
import os
import sys
import importlib.util


def test_core_modules_exist():
    """Test core module file existence"""
    # Add src directory to path
    src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
    sys.path.insert(0, src_path)

    # Core file list
    core_files = [
        'maze_generator.py',
        'path_finder.py',
        'maze_validator.py',
        'algorithms/dfs_generator.py',
        'algorithms/prim_generator.py',
        'algorithms/dfs_solver.py',
        'algorithms/bfs_solver.py',
        'algorithms/astar_solver.py',
        'utils/data_manager.py',
        'utils/performance.py'
    ]

    # Check file existence
    missing_files = []
    for file_path in core_files:
        full_path = os.path.join(src_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)

    assert len(missing_files) == 0, f"Missing core files: {missing_files}"

    # Try to import modules
    import_errors = []

    try:
        import maze_generator
        import path_finder
        import maze_validator
        from algorithms import dfs_generator, prim_generator
        from algorithms import dfs_solver, bfs_solver, astar_solver
        from utils import data_manager, performance
    except ImportError as e:
        import_errors.append(str(e))

    assert len(import_errors) == 0, f"Import errors: {import_errors}"


def test_numpy_available():
    """Test numpy dependency availability"""
    try:
        import numpy as np
        version = np.__version__
        # Check version validity
        major, minor = version.split('.')[:2]
        assert int(major) >= 1, f"numpy version too low: {version}"
    except ImportError:
        pytest.fail("numpy cannot be imported")
    except Exception as e:
        pytest.fail(f"numpy check failed: {e}")
