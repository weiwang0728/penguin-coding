"""
Performance Analysis Test
"""
import pytest
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from maze_generator import MazeGenerator
from path_finder import PathFinder
from utils.performance import PerformanceAnalyzer


def test_algorithm_recommendations():
    """Test algorithm recommendation suggestions"""
    generator = MazeGenerator()
    analyzer = PerformanceAnalyzer()

    # Generate test maze
    result = generator.generate('dfs', 15)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # Perform performance comparison
    algorithms = ['dfs', 'bfs', 'astar']
    iterations = 3

    try:
        comparison_result = analyzer.compare_algorithms(
            maze_matrix, start_point, end_point, algorithms, iterations
        )

        # Check if recommendations are included
        assert 'recommendations' in comparison_result, "Should contain recommendations"

        recommendations = comparison_result['recommendations']
        assert isinstance(recommendations, list), "Recommendations should be a list"
        assert len(recommendations) > 0, "Should provide at least one recommendation"

        # Check recommendation content quality
        # Recommendations should be based on algorithm characteristics
        recommendation_text = ' '.join(recommendations).lower()

        # Should mention algorithm characteristics
        algorithm_mentions = 0
        if 'bfs' in recommendation_text or 'breadth-first' in recommendation_text:
            algorithm_mentions += 1
        if 'dfs' in recommendation_text or 'depth-first' in recommendation_text:
            algorithm_mentions += 1
        if 'astar' in recommendation_text or 'a*' in recommendation_text:
            algorithm_mentions += 1

        assert algorithm_mentions >= 2, f"Recommendations should mention at least 2 algorithms, actually mentioned {algorithm_mentions}"

    except Exception as e:
        pytest.fail(f"Algorithm recommendation test failed: {e}")


def test_performance_comparison():
    """Test performance comparison function"""
    generator = MazeGenerator()
    analyzer = PerformanceAnalyzer()

    # Generate test maze
    result = generator.generate('dfs', 12)
    maze_matrix = result['maze_matrix']
    start_point = result['start_point']
    end_point = result['end_point']

    # Perform performance comparison
    algorithms = ['dfs', 'bfs', 'astar']
    iterations = 3

    try:
        comparison_result = analyzer.compare_algorithms(
            maze_matrix, start_point, end_point, algorithms, iterations
        )

        # Check return result structure
        required_keys = ['individual_results', 'comparison_report', 'recommendations']
        missing_keys = []

        for key in required_keys:
            if key not in comparison_result:
                missing_keys.append(key)

        assert len(missing_keys) == 0, f"Missing required return components: {missing_keys}"

        # Check individual_results
        individual_results = comparison_result['individual_results']
        assert isinstance(individual_results, dict), "individual_results should be a dictionary"

        # Check each algorithm's results
        for algo in algorithms:
            if algo in individual_results:
                algo_result = individual_results[algo]
                if 'error' not in algo_result:
                    # If algorithm ran successfully, check statistics
                    assert 'average_stats' in algo_result, f"{algo} should contain average statistics"
                    avg_stats = algo_result['average_stats']

                    expected_stats = ['search_time', 'path_length', 'explored_nodes_count']
                    for stat in expected_stats:
                        assert stat in avg_stats, f"{algo} average statistics should contain {stat}"

    except Exception as e:
        pytest.fail(f"Performance comparison test failed: {e}")


def test_complexity_evaluation():
    """Test complexity evaluation function"""
    generator = MazeGenerator()
    analyzer = PerformanceAnalyzer()

    # Generate two different sized mazes
    small_maze_result = generator.generate('dfs', 10)
    large_maze_result = generator.generate('dfs', 20)

    small_maze = small_maze_result['maze_matrix']
    large_maze = large_maze_result['maze_matrix']

    try:
        # Analyze small maze complexity
        small_complexity = analyzer.evaluate_maze_complexity(small_maze)

        # Analyze large maze complexity
        large_complexity = analyzer.evaluate_maze_complexity(large_maze)

        # Check return result structure
        required_sections = ['basic_stats', 'path_analysis', 'structure_analysis', 'complexity_evaluation']

        for complexity_result, description in [(small_complexity, "Small maze"), (large_complexity, "Large maze")]:
            missing_sections = []
            for section in required_sections:
                if section not in complexity_result:
                    missing_sections.append(section)

            assert len(missing_sections) == 0, f"{description} complexity evaluation missing sections: {missing_sections}"

        # Verify large maze complexity score should be higher than small maze
        small_score = small_complexity['complexity_evaluation']['complexity_score']
        large_score = large_complexity['complexity_evaluation']['complexity_score']

        # Allow some error, as complexity doesn't only depend on size
        assert large_score >= small_score * 0.8, f"Large maze complexity score {large_score} should not be lower than 80% of small maze ({small_score * 0.8})"

    except Exception as e:
        pytest.fail(f"Complexity evaluation test failed: {e}")
