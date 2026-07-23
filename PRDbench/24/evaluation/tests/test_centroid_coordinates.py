import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_centroid_in_anhui_range():
    """Test whether the centroid coordinates calculated by the single centroid method are within the geographical range of Anhui Province"""

    # Read data file
    data_path = os.path.join(os.path.dirname(__file__), '../../src/AfterClustering.xlsx')
    data = pd.read_excel(data_path)

    # Extract longitude, latitude and weight columns
    longitudes = data.iloc[:, 1].values
    latitudes = data.iloc[:, 2].values
    weights = data.iloc[:, 3].values.astype(float)

    # Normalize weights
    weights /= np.sum(weights)

    # Calculate centroid
    center_longitude = np.dot(longitudes, weights)
    center_latitude = np.dot(latitudes, weights)

    # Verify centroid coordinates are within Anhui Province geographical range
    assert 115 <= center_longitude <= 120, f"Centroid longitude {center_longitude} is not within Anhui Province range (115-120)"
    assert 30 <= center_latitude <= 35, f"Centroid latitude {center_latitude} is not within Anhui Province range (30-35)"

    print(f"Centroid coordinate verification passed: longitude={center_longitude:.6f}, latitude={center_latitude:.6f}")