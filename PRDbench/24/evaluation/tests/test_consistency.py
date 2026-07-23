import pytest
import pandas as pd
import numpy as np
import subprocess
import sys
import os
import re

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_centroid_consistency():
    """Test the consistency of results from multiple runs of SingleCentroidMethod"""

    # Switch to project root directory
    root_dir = os.path.join(os.path.dirname(__file__), '../..')

    def run_centroid_script():
        """Run SingleCentroidMethod script and extract coordinates"""
        result = subprocess.run(
            ['python', 'src/SingleCentroidMethod.py'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            encoding='gbk'
        )

        if result.returncode != 0:
            raise Exception(f"Script execution failed: {result.stderr}")

        # Extract longitude and latitude from output
        output = result.stdout
        longitude_match = re.search(r'Centroid Longitude:\s*([\d.-]+)', output)
        latitude_match = re.search(r'Centroid Latitude:\s*([\d.-]+)', output)

        if not longitude_match or not latitude_match:
            raise Exception(f"Unable to extract coordinates from output: {output}")

        longitude = float(longitude_match.group(1))
        latitude = float(latitude_match.group(1))

        return longitude, latitude

    # First run
    lon1, lat1 = run_centroid_script()

    # Second run
    lon2, lat2 = run_centroid_script()

    # Verify consistency of both runs (accurate to 6 decimal places)
    lon_diff = abs(lon1 - lon2)
    lat_diff = abs(lat1 - lat2)

    tolerance = 1e-6  # Tolerance for 6 decimal places

    assert lon_diff < tolerance, f"Longitude consistency test failed: {lon1} vs {lon2}, difference={lon_diff}"
    assert lat_diff < tolerance, f"Latitude consistency test failed: {lat1} vs {lat2}, difference={lat_diff}"

    print(f"Consistency test passed: First run({lon1:.6f}, {lat1:.6f}), Second run({lon2:.6f}, {lat2:.6f})")