import pytest
import sys
import os

# AddsrcDirectorytoPythonpath
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from fare_calculator import Sum_money as calculate_fare


class TestFare:

    def test_fare_calculation(self):
        """Test basic fare calculation function"""
        # Test cases: short distance (expected 3 yuan), medium distance (expected 4-5 yuan), long distance (expected 6 yuan or more)
        test_cases = [
            # (distance (meters), expected fare (yuan))
            (3000, 3),    # 3km, should be 3 yuan
            (5000, 3),    # 5km, should be 3 yuan
            (8000, 4),    # 8km, should be 4 yuan
            (15000, 5),   # 15km, should be 5 yuan
            (25000, 6),   # 25km, should be 6 yuan
        ]

        for distance, expected_fare in test_cases:
            actual_fare = calculate_fare(distance)
            assert actual_fare == expected_fare, \
                f"Distance {distance} meters fare should be {expected_fare} yuan, actually calculated as {actual_fare} yuan"
            print(f"✓ {distance} meters -> {actual_fare} yuan")

    def test_fare_boundary_conditions(self):
        """Test fare rule boundary processing"""
        # Test boundary cases: distance near 6km, 12km, 22km, 32km thresholds
        boundary_test_cases = [
            # (distance (meters), expected fare (yuan), description)
            (5999, 3, "Near 6km boundary (below)"),
            (6000, 4, "6km boundary"),
            (6001, 4, "Near 6km boundary (above)"),
            (11999, 4, "Near 12km boundary (below)"),
            (12000, 5, "12km boundary"),
            (12001, 5, "Near 12km boundary (above)"),
            (21999, 5, "Near 22km boundary (below)"),
            (22000, 6, "22km boundary"),
            (22001, 6, "Near 22km boundary (above)"),
            (31999, 6, "Near 32km boundary (below)"),
            (32000, 7, "32km boundary"),
            (32001, 7, "Near 32km boundary (above)"),
        ]

        for distance, expected_fare, description in boundary_test_cases:
            actual_fare = calculate_fare(distance)
            assert actual_fare == expected_fare, \
                f"{description}: distance {distance} meters fare should be {expected_fare} yuan, actually calculated as {actual_fare} yuan"
            print(f"✓ {description}: {distance} meters -> {actual_fare} yuan")

    def test_extended_fare_rules(self):
        """Test extended fare rule verification"""
        # Test extended fare rule: after 32km, add 1 yuan for every additional 20km
        extended_test_cases = [
            # (distance (meters), expected fare (yuan), description)
            (35000, 7, "32-52km range"),
            (45000, 7, "32-52km range mid-section"),
            (51999, 7, "Near 52km boundary (below)"),
            (52000, 8, "52km boundary"),
            (52001, 8, "Near 52km boundary (above)"),
            (65000, 8, "52-72km range"),
            (71999, 8, "Near 72km boundary (below)"),
            (72000, 9, "72km boundary"),
            (72001, 9, "Near 72km boundary (above)"),
            (85000, 9, "72-92km range"),
            (92000, 10, "92km boundary"),
            (100000, 10, "100km"),
        ]

        for distance, expected_fare, description in extended_test_cases:
            actual_fare = calculate_fare(distance)
            assert actual_fare == expected_fare, \
                f"{description}: distance {distance} meters fare should be {expected_fare} yuan, actually calculated as {actual_fare} yuan"
            print(f"✓ {description}: {distance} meters -> {actual_fare} yuan")

    def test_fare_calculation_edge_cases(self):
        """Test fare calculation edge cases"""
        # Test some special cases
        edge_cases = [
            (0, 3),      # 0 distance, minimum fare
            (1, 3),      # 1 meter, minimum fare
            (100, 3),    # 100 meters, minimum fare
            (1000, 3),   # 1km, minimum fare
        ]

        for distance, expected_fare in edge_cases:
            actual_fare = calculate_fare(distance)
            assert actual_fare == expected_fare, \
                f"Edge case: distance {distance} meters fare should be {expected_fare} yuan, actually calculated as {actual_fare} yuan"
            print(f"✓ Edge case: {distance} meters -> {actual_fare} yuan")

    def test_fare_calculation_consistency(self):
        """Test fare calculation consistency"""
        # Ensure same distance always returns same fare
        test_distance = 15000  # 15km
        expected_fare = calculate_fare(test_distance)

        # Multiple calculations should get same result
        for _ in range(10):
            actual_fare = calculate_fare(test_distance)
            assert actual_fare == expected_fare, \
                f"Fare calculation should maintain consistency, distance {test_distance} meters should always return {expected_fare} yuan"

        print(f"✓ Consistency test passed: {test_distance} meters always returns {expected_fare} yuan")


if __name__ == "__main__":
    pytest.main([__file__])
