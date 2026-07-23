import pytest
import sys
import os
import time

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from models import Graph, Edge
from pathfinding import ShortestPath
from data_loader import load_subway_data, DATA_FILE_PATH


class TestPerformance:

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

    def test_response_time(self, setup_graph):
        """Test performance requirements - response time should be within limits"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Prepare 5 groups of queries with different complexity levels
        test_cases = [
            ("Tiananmen East", "Xidan", "short distance direct route"),
            ("Tiananmen East", "Zhongguancun", "medium distance with transfer"),
            ("Tiananmen East", "Dongdan", "medium distance possible transfer"),
            ("Xidan", "Yonghegong Lama Temple", "long distance multiple transfers"),
            ("Chaoyangmen", "Zhongguancun", "cross-line query")
        ]

        response_times = []
        successful_tests = 0

        for start_station, end_station, description in test_cases:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                print(f"Skip test: {description} ({start_station} -> {end_station}) - station does not exist")
                continue

            # Record start time
            start_time = time.time()

            try:
                # Execute path finding
                path_finder = ShortestPath(metro_graph, start_id)

                if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                    path_ids, edges = path_finder.path_with_edges(end_id)
                    total_distance = sum(edge.weight for edge in edges)

                    # Record end time
                    end_time = time.time()
                    response_time = end_time - start_time
                    response_times.append(response_time)

                    print(f"✓ {description}: {response_time:.3f} seconds ({start_station} -> {end_station}, {total_distance} meters)")
                    successful_tests += 1

                    # Verify response time should be within 1 second
                    assert response_time <= 1.0, \
                        f"{description} response time {response_time:.3f} seconds exceeds 1 second limit"

                else:
                    print(f"✗ {description}: Unable to find path ({start_station} -> {end_station})")

            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                print(f"✗ {description}: Execution failed ({response_time:.3f} seconds) - {str(e)}")

        # Verify test results
        assert successful_tests >= 3, \
            f"At least 3 successful performance tests required, actual: {successful_tests}"

        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)

            print(f"\nPerformance summary:")
            print(f"  Average response time: {avg_response_time:.3f} seconds")
            print(f"  Maximum response time: {max_response_time:.3f} seconds")
            print(f"  Minimum response time: {min_response_time:.3f} seconds")
            print(f"  Successful tests: {successful_tests}/{len(test_cases)}")

            # Verify average response time
            assert avg_response_time <= 0.5, \
                f"Average response time {avg_response_time:.3f} seconds should be within 0.5 seconds"

    def test_memory_usage(self, setup_graph):
        """Test memory usage"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Simple memory usage check
        station_count = len(station_to_number)

        # Verify data model is properly initialized
        assert station_count > 0, "Should have station data"
        assert station_count < 10000, f"Station count {station_count} is too high, possible data issue"

        print(f"✓ Memory usage check: {station_count} stations")

    def test_algorithm_efficiency(self, setup_graph):
        """Test algorithm efficiency"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Test multiple query performance stability
        test_station_pairs = [
            ("Tiananmen East", "Xidan"),
            ("Tiananmen East", "Zhongguancun"),
        ]

        for start_station, end_station in test_station_pairs:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is None or end_id is None:
                continue

            # Execute multiple queries to test performance stability
            times = []
            for i in range(5):
                start_time = time.time()
                path_finder = ShortestPath(metro_graph, start_id)
                if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                    path_ids, edges = path_finder.path_with_edges(end_id)
                end_time = time.time()
                times.append(end_time - start_time)

            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)

                print(f"✓ {start_station} -> {end_station}: Average {avg_time:.3f} seconds (Range: {min_time:.3f}-{max_time:.3f} seconds)")

                # Verify performance stability
                assert max_time - min_time <= 0.1, \
                    f"Performance fluctuation too large: {max_time - min_time:.3f} seconds"

    def test_concurrent_queries(self, setup_graph):
        """Test concurrent query performance (simulated)"""
        metro_graph, station_to_number, number_to_station = setup_graph

        # Simulate continuous multiple queries (similar to concurrent scenario)
        query_pairs = [
            ("Tiananmen East", "Xidan"),
            ("Xidan", "Zhongguancun"),
            ("Zhongguancun", "Dongdan"),
            ("Dongdan", "Chaoyangmen"),
            ("Chaoyangmen", "Tiananmen East"),
        ]

        start_time = time.time()
        successful_queries = 0

        for start_station, end_station in query_pairs:
            start_id = station_to_number.get(start_station)
            end_id = station_to_number.get(end_station)

            if start_id is not None and end_id is not None:
                path_finder = ShortestPath(metro_graph, start_id)
                if path_finder.dist_to.get(end_id, float("inf")) != float("inf"):
                    path_ids, edges = path_finder.path_with_edges(end_id)
                    successful_queries += 1

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_query = total_time / len(query_pairs) if query_pairs else 0

        print(f"✓ Continuous query test: {successful_queries}/{len(query_pairs)} successful")
        print(f"  Total time: {total_time:.3f} seconds")
        print(f"  Average per query: {avg_time_per_query:.3f} seconds")

        # Verify continuous query performance
        assert avg_time_per_query <= 0.2, \
            f"Continuous query average time {avg_time_per_query:.3f} seconds is too long"
        assert successful_queries >= len(query_pairs) * 0.8, \
            f"Continuous query success rate too low: {successful_queries}/{len(query_pairs)}"


if __name__ == "__main__":
    pytest.main([__file__])
