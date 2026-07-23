import os
import sys

# Add src directory to the Python path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest
from models import Graph, Edge
from data_loader import load_subway_data, DATA_FILE_PATH

class TestData:

    @pytest.fixture
    def subway_data(self):
        """Load subway data"""
        data = load_subway_data(DATA_FILE_PATH)
        if not data:
            pytest.skip("Unable to load subway data file")
        return data
    
    def test_data_coverage(self, subway_data):
        """Test data coverage verification"""
        # Extract main line stations mentioned in PRD
        required_stations = [
            # Line 1
            "Tiananmen East", "Xidan",
            # Line 2
            "Chaoyangmen", "Dongzhimen",
            # Line 4
            "Zhongguancun",
            # Line 5
            "Dongdan", "Yonghegong Lama Temple",
            # Other important stations
            "Tiananmen West"
        ]

        # Extract all station names from data
        available_stations = set()
        for station_info in subway_data['stations']:
            available_stations.add(station_info['name'])

        # Check if each required station exists
        found_stations = []
        missing_stations = []

        for station in required_stations:
            if station in available_stations:
                found_stations.append(station)
                print(f"✓ Found station: {station}")
            else:
                missing_stations.append(station)
                print(f"✗ Missing station: {station}")

        # Verify data coverage
        coverage_ratio = len(found_stations) / len(required_stations)
        print(f"Data coverage: {coverage_ratio:.2%} ({len(found_stations)}/{len(required_stations)})")

        # Should identify at least 6 main line stations
        assert len(found_stations) >= 6, \
            f"Should identify at least 6 main line stations, actually identified {len(found_stations)}: {found_stations}"

        if missing_stations:
            print(f"Warning: Missing the following stations: {missing_stations}")

    def test_data_management(self, subway_data):
        """Test data management functionality verification"""

        # 1. Test station data coverage
        stations = subway_data['stations']
        connections = subway_data['connections']

        assert len(stations) > 0, "Should contain station data"
        assert len(connections) > 0, "Should contain connection data"

        print(f"✓ Station data: {len(stations)} stations")
        print(f"✓ Connection data: {len(connections)} connections")

        # 2. Test connection relationship completeness check
        station_names = set(station['name'] for station in stations)

        # Check if stations in connections are all in station list
        connection_stations = set()
        invalid_connections = []

        for conn in connections:
            source = conn['source']
            dest = conn['dest']
            connection_stations.add(source)
            connection_stations.add(dest)

            if source not in station_names:
                invalid_connections.append(f"Source station '{source}' not in station list")
            if dest not in station_names:
                invalid_connections.append(f"Destination station '{dest}' not in station list")

        # Connection relationship completeness verification
        if invalid_connections:
            print(f"Warning: Found {len(invalid_connections)} invalid connections")
            for invalid in invalid_connections[:5]:  # Display first 5 only
                print(f"  - {invalid}")
        else:
            print("✓ Connection relationship completeness check passed")

        # Most connections should be valid
        valid_connection_ratio = 1 - (len(invalid_connections) / len(connections))
        assert valid_connection_ratio >= 0.95, \
            f"Connection validity rate should be at least 95%, actually {valid_connection_ratio:.2%}"

        # 3. Test distance data validity
        distance_issues = []

        for conn in connections:
            distance = conn.get('distance', 0)
            if distance <= 0:
                distance_issues.append(f"Connection {conn['source']} -> {conn['dest']} distance invalid: {distance}")
            elif distance > 50000:  # 50km, subway station distance should not exceed this value
                distance_issues.append(f"Connection {conn['source']} -> {conn['dest']} distance abnormal: {distance} meter(s)")

        if distance_issues:
            print(f"Warning: Found {len(distance_issues)} distance data issues")
            for issue in distance_issues[:5]:  # Display first 5 only
                print(f"  - {issue}")
        else:
            print("✓ Distance data validity check passed")

        # Most distance data should be valid
        valid_distance_ratio = 1 - (len(distance_issues) / len(connections))
        assert valid_distance_ratio >= 0.9, \
            f"Distance data validity rate should be at least 90%, actually {valid_distance_ratio:.2%}"

        # 4. Test line information completeness
        line_coverage = {}

        for station in stations:
            lines = station.get('lines', [])
            for line in lines:
                if line not in line_coverage:
                    line_coverage[line] = 0
                line_coverage[line] += 1

        print(f"✓ Line coverage situation:")
        for line, count in sorted(line_coverage.items()):
            print(f"  - {line}: {count} stations")

        # Should cover at least several main lines
        assert len(line_coverage) >= 3, \
            f"Should cover at least 3 subway lines, actually covered {len(line_coverage)} lines"

    def test_data_structure_validation(self, subway_data):
        """Test data structure verification"""

        # Verify station data structure
        for i, station in enumerate(subway_data['stations']):
            assert 'name' in station, f"Station {i} missing 'name' field"
            assert 'lines' in station, f"Station {i} missing 'lines' field"
            assert isinstance(station['name'], str), f"Station {i} 'name' should be string"
            assert isinstance(station['lines'], list), f"Station {i} 'lines' should be list"
            assert len(station['name'].strip()) > 0, f"Station {i} name cannot be empty"

        print(f"✓ Station data structure verification passed: {len(subway_data['stations'])} stations")

        # Verify connection data structure
        for i, conn in enumerate(subway_data['connections']):
            required_fields = ['source', 'dest', 'distance', 'line']
            for field in required_fields:
                assert field in conn, f"Connection {i} missing '{field}' field"

            assert isinstance(conn['source'], str), f"Connection {i} 'source' should be string"
            assert isinstance(conn['dest'], str), f"Connection {i} 'dest' should be string"
            assert isinstance(conn['distance'], (int, float)), f"Connection {i} 'distance' should be number"
            assert isinstance(conn['line'], str), f"Connection {i} 'line' should be string"

            assert len(conn['source'].strip()) > 0, f"Connection {i} source station name cannot be empty"
            assert len(conn['dest'].strip()) > 0, f"Connection {i} destination station name cannot be empty"
            assert conn['distance'] > 0, f"Connection {i} distance should be greater than 0"

        print(f"✓ Connection data structure verification passed: {len(subway_data['connections'])} connections")

    def test_graph_construction(self, subway_data):
        """Test graph construction function"""

        # Build graph
        metro_graph = Graph()
        station_to_number = {}
        current_station_id = 1

        for station_info in subway_data['stations']:
            station_name = station_info['name']
            station_lines = station_info['lines']

            if station_name not in station_to_number:
                station_to_number[station_name] = current_station_id
                current_station_id += 1

            metro_graph.set_station_lines(station_name, station_lines)

        valid_edges = 0
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
                valid_edges += 1

        # Verify graph construction result
        assert len(station_to_number) > 0, "Should successfully add stations to graph"
        assert valid_edges > 0, "Should successfully add edges to graph"

        print(f"✓ Graph construction successful: {len(station_to_number)} stations, {valid_edges} edges")

        # Verify graph connectivity (simple check)
        # Check if any stations have no connections
        connected_stations = set()
        for conn in subway_data['connections']:
            if conn['source'] in station_to_number and conn['dest'] in station_to_number:
                connected_stations.add(conn['source'])
                connected_stations.add(conn['dest'])

        connectivity_ratio = len(connected_stations) / len(station_to_number)
        print(f"✓ Graph connectivity: {connectivity_ratio:.2%} stations have connections")

        # Most stations should be connected
        assert connectivity_ratio >= 0.8, \
            f"At least 80% of stations should have connections, actually {connectivity_ratio:.2%}"


if __name__ == "__main__":
    pytest.main([__file__])
