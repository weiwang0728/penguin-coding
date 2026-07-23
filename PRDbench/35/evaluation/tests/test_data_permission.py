import sys
import os
import pytest

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager

@pytest.fixture(scope="function")
def data_manager_for_permission():
    """Provide a specific DataManager instance for permission testing."""
    test_data_file = "test_permission_data.json"

    if os.path.exists(test_data_file):
        os.remove(test_data_file)

    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data() # This will create 'Company' root department (ID=1)

    # Create two new departments
    dept_a = dm.add_department("Department A", 1)
    dept_b = dm.add_department("Department B", 1)

    # Create two users, belonging to different departments
    dm.add_user("user_a", "pass_a", dept_a.id, roles=["STAFF"])
    dm.add_user("user_b", "pass_b", dept_b.id, roles=["STAFF"])

    # Create two assets, belonging to users from different departments
    dm.add_asset("Asset A", 100, 2, "user_a") # Assume category ID is 2
    dm.add_asset("Asset B", 200, 2, "user_b")

    yield dm

    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_department_data_isolation(data_manager_for_permission):
    """
    Test department data isolation (Metric: 2.7.1)
    - Verify a department's user can only see their own assets.
    """
    dm = data_manager_for_permission

    # Get assets belonging to UserA
    assets_for_user_a = dm.get_assets_by_owner("user_a")
    assert len(assets_for_user_a) == 1
    assert assets_for_user_a[0].name == "Asset A"

    # Get assets belonging to UserB
    assets_for_user_b = dm.get_assets_by_owner("user_b")
    assert len(assets_for_user_b) == 1
    assert assets_for_user_b[0].name == "Asset B"

    # Verify UserA cannot see UserB's assets
    for asset in assets_for_user_a:
        assert asset.owner_username != "user_b"

    # Verify UserB cannot see UserA's assets
    for asset in assets_for_user_b:
        assert asset.owner_username != "user_a"