import pytest
import os

def test_standard_scaler_usage():
    """Test whether StandardScaler is used for coordinate standardization in ClusteringAlgorithm.py"""

    # Read ClusteringAlgorithm.py file
    code_path = os.path.join(os.path.dirname(__file__), '../../src/ClusteringAlgorithm.py')

    with open(code_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if StandardScaler related code is included
    has_standard_scaler = 'StandardScaler' in content
    has_fit_transform = 'fit_transform' in content
    has_import_scaler = 'from sklearn.preprocessing import StandardScaler' in content

    assert has_standard_scaler, "StandardScaler not found in code"
    assert has_fit_transform, "fit_transform method not found in code"
    assert has_import_scaler, "StandardScaler not imported in code"

    print("StandardScaler usage verification passed")

def test_weight_normalization():
    """Test whether SingleCentroidMethod.py contains weight normalization processing logic"""

    # Read SingleCentroidMethod.py file
    code_path = os.path.join(os.path.dirname(__file__), '../../src/SingleCentroidMethod.py')

    with open(code_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if weight normalization related code is included
    has_weight_normalization = (
        'weights /=' in content or
        'weights = weights /' in content or
        'np.sum(weights)' in content
    )

    assert has_weight_normalization, "Weight normalization processing logic not found in code"

    print("Weight normalization processing verification passed")