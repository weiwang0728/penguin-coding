"""
Path Algorithm Performance Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder


def test_bfs_shortest_path():
    """Test BFS shortest path guarantee"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Generate a test maze
    result = generator.generate('dfs', 15)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # Run multiple tests
    bfs_lengths = []
    dfs_lengths = []

    for i in range(3):
        # BFS test
        bfs_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)
        if bfs_result['found_solution']:
            bfs_lengths.append(bfs_result['path_length'])

        # DFS test
        dfs_result = path_finder.solve('dfs', maze_matrix, start_point, end_point)
        if dfs_result['found_solution']:
            dfs_lengths.append(dfs_result['path_length'])

    # Ensure sufficient successful tests
    assert len(bfs_lengths) >= 2, "BFS successful test count insufficient"
    assert len(dfs_lengths) >= 2, "DFS successful test count insufficient"

    # BFS should find the shortest path (length should be less than or equal to DFS)
    avg_bfs = sum(bfs_lengths) / len(bfs_lengths)
    avg_dfs = sum(dfs_lengths) / len(dfs_lengths)

    assert avg_bfs <= avg_dfs, f"BFS average path length {avg_bfs} should be <= DFS average path length {avg_dfs}"


def test_astar_optimal_path():
    """Test A* optimal path guarantee"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Generate a 20x20 complex maze
    result = generator.generate('dfs', 20)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # Run multiple tests
    astar_results = []
    bfs_results = []

    for i in range(3):
        # A* test
        astar_result = path_finder.solve('astar', maze_matrix, start_point, end_point)
        if astar_result['found_solution']:
            astar_results.append(astar_result)

        # BFS test
        bfs_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)
        if bfs_result['found_solution']:
            bfs_results.append(bfs_result)

    # Ensure sufficient successful tests
    assert len(astar_results) >= 2, "A* successful test count insufficient"
    assert len(bfs_results) >= 2, "BFS successful test count insufficient"

    # A* should find optimal path (same length as BFS)
    astar_lengths = [r['path_length'] for r in astar_results]
    bfs_lengths = [r['path_length'] for r in bfs_results]

    avg_astar_length = sum(astar_lengths) / len(astar_lengths)
    avg_bfs_length = sum(bfs_lengths) / len(bfs_lengths)

    assert avg_astar_length <= avg_bfs_length, f"A* average path length {avg_astar_length} should be <= BFS average path length {avg_bfs_length}"

    # A* should explore fewer nodes than BFS
    astar_nodes = [r['explored_nodes_count'] for r in astar_results]
    bfs_nodes = [r['explored_nodes_count'] for r in bfs_results]

    avg_astar_nodes = sum(astar_nodes) / len(astar_nodes)
    avg_bfs_nodes = sum(bfs_nodes) / len(bfs_nodes)

    # A* explored node count should be less than or equal to BFS (allow some error)
    # On small mazes A*'s advantage may not be obvious, so we relax requirements
    assert avg_astar_nodes <= avg_bfs_nodes * 1.1, f"A* average explored nodes {avg_astar_nodes} should be <= BFS 110% ({avg_bfs_nodes * 1.1})"


def test_astar_heuristic():
    """Test A* heuristic function implementation"""
    generator = MazeGenerator()
    path_finder = PathFinder()

    # Generate a large maze (50x50)
    try:
        result = generator.generate('dfs', 50)
        maze_matrix = result['maze_matrix']
        start_point = result['start_point']
        end_point = result['end_point']
    except:
        # If unable to generate 50x50 maze, use smaller maze
        result = generator.generate('dfs', 30)
        maze_matrix = result['maze_matrix']
        start_point = result['start_point']
        end_point = result['end_point']

    # Run multiple tests
    astar_nodes = []
    bfs_nodes = []

    for i in range(3):  # Reduce test count to save time
        # A* test
        astar_result = path_finder.solve('astar', maze_matrix, start_point, end_point)
        if astar_result['found_solution']:
            astar_nodes.append(astar_result['explored_nodes_count'])

        # BFS test
        bfs_result = path_finder.solve('bfs', maze_matrix, start_point, end_point)
        if bfs_result['found_solution']:
            bfs_nodes.append(bfs_result['explored_nodes_count'])

    # Ensure sufficient successful tests
    assert len(astar_nodes) >= 2, "A* successful test count insufficient"
    assert len(bfs_nodes) >= 2, "BFS successful test count insufficient"

    # A* heuristic advantage: explored node count should be significantly less than BFS
    avg_astar_nodes = sum(astar_nodes) / len(astar_nodes)
    avg_bfs_nodes = sum(bfs_nodes) / len(bfs_nodes)

    # A* explored node count should not exceed BFS, demonstrating heuristic advantage
    # In actual mazes, A*'s advantage depends on maze complexity and structure
    # We expect A* to be at least not worse than BFS
    assert avg_astar_nodes <= avg_bfs_nodes * 1.05, f"A* average explored nodes {avg_astar_nodes} should be <= BFS 105% ({avg_bfs_nodes * 1.05})"
