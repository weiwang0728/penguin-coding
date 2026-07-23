import os
import sys
import time

# Add src directory to the Python path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from models import Graph, Edge
from pathfinding import ShortestPath
from fare_calculator import calculate_estimated_time
from data_loader import load_subway_data, DATA_FILE_PATH


class TestPathfinding:

    @pytest.fixture
    def setup_graph(self):
        """Set up test subway network graph"""
        subway_data = load_subway_data(DATA_FILE_PATH)
        if not subway_data:
            pytest.skip("Unable to load subway data")
    
        metro_graph = Graph()
        station_to_number = {}
        number_to_station = {}
        current_station_id = 1

        # Build station mapping
        for station_info in subway_data['stations']:
            station_name = station_info['name']
            station_lines = station_info['lines']

            if station_name not in station_to_number:
                station_to_number[station_name] = current_station_id
                number_to_station[current_station_id] = station_name
                current_station_id += 1

            metro_graph.set_station_lines(station_name, station_lines)

        # Build connection relationships
        for conn in subway_data['connections']:
            source_name = conn['source']
            dest_name = conn['dest']
            distance = conn['distance']
            line = conn['line']

            source_id = station_to_number.get(source_name)
            dest_id = station_to_number.get(dest_name)

            if source_id is not None and dest_id is not None:
                edge = Edge(source_id, dest_id, distance, line)
                metro_graph.add_edge(edge)
    
        return metro_graph, station_to_number, number_to_station

    def test_multiple_path_modes(self, setup_graph):
        """Test Various path query modes"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Choose stations requiring transfers for representative testing
        start_station = "Tiananmen East"
        end_station = "Zhongguancun"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        # Test basic shortest path algorithm
        path_finder = ShortestPath(metro_graph, start_id)

        # Verify path can be found
        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "Should be able to find valid path"

        # Get path information
        path_ids, edges = path_finder.path_with_edges(end_id)

        # Verify basic path properties
        assert len(path_ids) >= 2, "Path should contain at least start and end points"
        assert path_ids[0] == start_id, "Path should start from start point"
        assert path_ids[-1] == end_id, "Path should end at end point"
        assert len(edges) == len(path_ids) - 1, "Number of edges should be 1 less than number of stations"

        # Note: Since only basic shortest path algorithm is currently implemented, we mainly verify algorithm correctness here
        # In actual implementation, there should be different path query modes
        print(f"Found path: {' -> '.join([number_to_station[id] for id in path_ids])}")

    def test_path_preferences(self, setup_graph):
        """Test Path preference settings"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Choose test stations
        start_station = "Tiananmen East"
        end_station = "Xidan"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        # Test basic path finding
        path_finder = ShortestPath(metro_graph, start_id)

        # Verify path can be found
        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "Should be able to find valid path"

        # Get path information
        path_ids, edges = path_finder.path_with_edges(end_id)

        # Calculate transfer count
        transfer_count = 0
        previous_line = None
        for edge in edges:
            if previous_line and previous_line != edge.line:
                transfer_count += 1
            previous_line = edge.line

        # Verify path constraints (mainly verify transfer count is reasonable here)
        assert transfer_count <= 5, "Transfer count should be within reasonable range"

        print(f"Path transfer count: {transfer_count}")

    def test_complex_transfer_handling(self, setup_graph):
        """Test Transfer station special handling"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Choose path with complex transfers
        start_station = "Tiananmen East"
        end_station = "Zhongguancun"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        path_finder = ShortestPath(metro_graph, start_id)

        # Verify path can be found
        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "Should be able to find valid path"

        # Get path information
        path_ids, edges = path_finder.path_with_edges(end_id)

        # Check transfer station handling
        transfer_stations = []
        previous_line = None

        for i, edge in enumerate(edges):
            if previous_line and previous_line != edge.line:
                # Found transfer point
                transfer_station_id = path_ids[i]
                transfer_station_name = number_to_station[transfer_station_id]
                transfer_stations.append(transfer_station_name)

                # Verify transfer station actually supports multiple lines
                station_lines = metro_graph.station_lines.get(transfer_station_name, [])
                assert len(station_lines) > 1, f"Transfer station {transfer_station_name} should support multiple lines"

            previous_line = edge.line

        print(f"Detected transfer stations: {transfer_stations}")

    def test_shortest_path(self, setup_graph):
        """Test shortest path algorithm verification"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Test Case 1: Direct path
        test_cases = [
            ("Tiananmen East", "Xidan", 2142),  # Direct or short path, expected distance
            ("Tiananmen East", "Zhongguancun", 13771),  # Path requiring transfers, expected distance
            ("Xidan", "Dongdan", 3768)  # Another test path, expected distance
        ]

        successful_tests = 0

        for start_station, end_station, expected_distance in test_cases:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                print(f"Skip test: {start_station} -> {end_station} (station does not exist)")
                continue

            from pathfinding import PathfindingConfig # Ensure PathfindingConfig is imported
            config = PathfindingConfig()
            config.mode = "shortest_distance" # Explicitly test shortest_distance mode
            path_finder = ShortestPath(metro_graph, start_id, config)

            if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                path_ids, edges = path_finder.path_with_edges(end_id)
                total_distance = sum(edge.weight for edge in edges)

                # Verify basic path properties
                assert len(path_ids) >= 2, f"Path {start_station} -> {end_station} should contain at least start and end points"
                assert path_ids[0] == start_id, f"Path should start from {start_station}"
                assert path_ids[-1] == end_id, f"Path should end at {end_station}"
                assert total_distance > 0, "Path total distance should be greater than 0"

                # Verify if shortest path is found (by distance)
                assert total_distance == expected_distance, f"Path {start_station} -> {end_station} total distance incorrect. Expected: {expected_distance} meters, Actual: {total_distance} meters"

                successful_tests += 1
                print(f"✓ {start_station} -> {end_station}: {total_distance} meters (Expected: {expected_distance} meters)")
            else:
                print(f"✗ {start_station} -> {end_station}: Unable to find path")

        # Should have at least 2 successful test cases
        assert successful_tests >= 2, f"Should have at least 2 successful path tests, actual success: {successful_tests}"

    def test_time_estimation(self, setup_graph):
        """Test travel time estimation calculation function"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Test different distances and transfer counts for time estimation calculation
        test_cases = [
            ("Tiananmen East", "Xidan", 3000, 0),  # Short distance, no transfer
            ("Tiananmen East", "Zhongguancun", 15000, 2),  # Medium distance, has transfers
        ]

        for start_station, end_station, expected_distance, expected_transfers in test_cases:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                continue

            path_finder = ShortestPath(metro_graph, start_id)

            if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                path_ids, edges = path_finder.path_with_edges(end_id)
                total_distance = sum(edge.weight for edge in edges)

                # Calculate transfer count
                transfer_count = 0
                previous_line = None
                for edge in edges:
                    if previous_line and previous_line != edge.line:
                        transfer_count += 1
                    previous_line = edge.line

                # Test travel time estimation function
                estimated_time = calculate_estimated_time(total_distance, transfer_count)

                # Verify travel time estimation reasonableness
                assert estimated_time > 0, "Estimated travel time should be greater than 0"

                # Basic reasonableness check for time estimation (1-2 minutes per km, 2-3 minutes per transfer)
                min_expected_time = (total_distance / 1000) * 1 + transfer_count * 2
                max_expected_time = (total_distance / 1000) * 3 + transfer_count * 5

                assert min_expected_time <= estimated_time <= max_expected_time, \
                    f"Estimated time {estimated_time} minutes should be within reasonable range [{min_expected_time:.1f}, {max_expected_time:.1f}]"

                print(f"{start_station} -> {end_station}: {total_distance} meters, {transfer_count} transfers, estimated {estimated_time} minutes")

    def test_least_transfer_mode(self, setup_graph):
        """Test least transfer mode"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "Tiananmen East"
        end_station = "Zhongguancun" # This route typically involves transfers

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        from pathfinding import PathfindingConfig # important here to avoid circular dependency if not already imported
        config = PathfindingConfig()
        config.mode = "least_transfer"
        path_finder = ShortestPath(metro_graph, start_id, config)

        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "Should be able to find valid path"

        path_ids, edges = path_finder.path_with_edges(end_id)
        transfer_count = path_finder.get_transfer_count(end_id)

        # For "Tiananmen East" to "Zhongguancun", the least transfers should be 1 ( 1 to  4)
        # This assertion might need adjustment based on actual data and optimal path
        assert transfer_count == 1, f"In least transfer mode, transfer count should be 1, actual: {transfer_count}"
        print(f"Least transfer mode: {start_station} -> {end_station}, transfer count: {transfer_count}")

    def test_comprehensive_mode(self, setup_graph):
        """Test comprehensive optimization mode"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "Tiananmen East"
        end_station = "Zhongguancun"

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        from pathfinding import PathfindingConfig
        config = PathfindingConfig()
        config.mode = "comprehensive"
        path_finder = ShortestPath(metro_graph, start_id, config)

        assert path_finder.dist_to.get(end_id, float("inf")) != float("inf"), "Should be able to find valid path"

        path_ids, edges = path_finder.path_with_edges(end_id)
        transfer_count = path_finder.get_transfer_count(end_id)
        total_distance = sum(edge.weight for edge in edges)

        # Comprehensive mode should balance distance and transfers.
        # For "Tiananmen East" to "Zhongguancun", it's likely 1 transfer, similar to least_transfer,
        # but the exact path might differ slightly if there are multiple 1-transfer options.
        # We can assert that it's not excessively high in transfers or distance.
        assert transfer_count <= 2, f"In comprehensive optimization mode, transfer count should not exceed 2, actual: {transfer_count}"
        assert total_distance < 20000, f"In comprehensive optimization mode, total distance should not be excessive, actual: {total_distance}"
        print(f"Comprehensive optimization mode: {start_station} -> {end_station}, distance: {total_distance}, transfer count: {transfer_count}")

    def test_max_transfers_limit(self, setup_graph):
        """Test maximum transfer count limit control"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "Tiananmen East"
        end_station = "Zhongguancun" # This route requires transfers

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        # test with max_transfers = 0 (should find no path for this route)
        from pathfinding import PathfindingConfig
        config_zero_transfers = PathfindingConfig()
        config_zero_transfers.mode = "shortest_distance" # Can be any mode, limit applies
        config_zero_transfers.max_transfers = 0
        path_finder_zero = ShortestPath(metro_graph, start_id, config_zero_transfers)
        assert path_finder_zero.dist_to.get(end_id, float("inf")) == float("inf"), "With max_transfers=0, should not find paths that require transfers"
        print(f"max_transfers=0: {start_station} -> {end_station}, Result: No path (as expected)")

        # test with a reasonable max_transfers (e.g., 1)
        config_one_transfer = PathfindingConfig()
        config_one_transfer.mode = "shortest_distance"
        config_one_transfer.max_transfers = 1
        path_finder_one = ShortestPath(metro_graph, start_id, config_one_transfer)
        assert path_finder_one.dist_to.get(end_id, float("inf")) != float("inf"), "With max_transfers=1, should be able to find a path"
        transfer_count_one = path_finder_one.get_transfer_count(end_id)
        assert transfer_count_one <= 1, f"With max_transfers=1, transfer count should be <= 1, actual: {transfer_count_one}"
        print(f"max_transfers=1: {start_station} -> {end_station}, transfer count: {transfer_count_one} (as expected)")

    def test_line_preference(self, setup_graph):
        """Test line preference setting function"""
        metro_graph, station_to_number, number_to_station = setup_graph

        start_station = "Tiananmen East"
        end_station = "Zhongguancun" # Route that can use different lines for transfer

        start_id = station_to_number.get(start_station)
        end_id = station_to_number.get(end_station)

        if start_id is None or end_id is None:
            pytest.skip(f"test station {start_station} or {end_station} does not exist")

        # test with a preferred line (e.g., " 1")
        from pathfinding import PathfindingConfig
        config_pref_line = PathfindingConfig()
        config_pref_line.mode = "shortest_distance"
        config_pref_line.preferred_lines = [" 1"] #  1 is part of the path
        path_finder_pref = ShortestPath(metro_graph, start_id, config_pref_line)

        assert path_finder_pref.dist_to.get(end_id, float("inf")) != float("inf"), "After setting preferred line, should be able to find path"

        path_ids, edges = path_finder_pref.path_with_edges(end_id)
        # This assertion is tricky due to the current _is_line_acceptable implementation.
        # It only checks if the line is acceptable, not if it's strictly preferred.
        # For now, we can just ensure the path is found and doesn't use avoided lines (if any).
        # A more robust test would require a more robust _is_line_acceptable.

        # Check if any edge in the path uses the preferred line (if applicable)
        uses_preferred_line = any(" 1" in edge.line for edge in edges) # Assuming line is a string like " 1"
        print(f"Line preference ' 1': {start_station} -> {end_station}, path contains Line 1: {uses_preferred_line}")
        # For this specific route, it should contain  1.
        assert uses_preferred_line, "Path should contain preferred line ' 1'"

if __name__ == "__main__":
    pytest.main([__file__])
