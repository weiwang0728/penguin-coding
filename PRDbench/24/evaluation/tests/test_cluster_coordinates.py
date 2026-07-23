import pytest
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

def test_cluster_centers_in_anhui_range():
    """Test whether K-means cluster center coordinates are within the geographical range of Anhui Province"""

    # Read data file
    data_path = os.path.join(os.path.dirname(__file__), '../../src/mdl4.xlsx')
    data = pd.read_excel(data_path)

    # Extract longitude and latitude column data
    coordinates = data.iloc[:, 1:].values

    # Feature scaling
    scaler = StandardScaler()
    scaled_coordinates = scaler.fit_transform(coordinates)

    # Set number of clusters
    k = 14

    # Run K-means algorithm
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_coordinates)

    # Inverse transform cluster center coordinates to original range
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)

    # Verify cluster center coordinates are within Anhui Province geographical range
    valid_centers = 0
    for i, center in enumerate(cluster_centers):
        longitude, latitude = center[0], center[1]
        if 115 <= longitude <= 120 and 30 <= latitude <= 35:
            valid_centers += 1
        print(f"Cluster center {i+1}: longitude={longitude:.6f}, latitude={latitude:.6f}")

    # At least 12 cluster centers should be within reasonable range
    assert valid_centers >= 12, f"Only {valid_centers} cluster centers are within Anhui Province range, less than the required 12"

    print(f"Cluster center coordinate verification passed: {valid_centers}/14 centers are within Anhui Province range")