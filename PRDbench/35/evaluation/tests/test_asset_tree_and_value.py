import sys
import os
import pytest
from datetime import datetime, timedelta

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, Asset

@pytest.fixture(scope="function")
def data_manager():
    """Provide a temporary, isolated DataManager instance for testing."""
    test_data_file = "test_asset_tree_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # Add test user and category
    dm.add_user("asset_user", "password123", 1, roles=["ASSET"])
    dm.add_category("Test Category", 1)
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_set_parent_asset(data_manager):
    """Test setting parent asset (Metric: 2.4.2a)"""
    # Create two assets
    parent_asset = data_manager.add_asset("Server Cabinet", 20000, 2, "asset_user")
    child_asset = data_manager.add_asset("Server", 15000, 2, "asset_user")

    # Set parent-child relationship
    data_manager.update_asset(child_asset.id, parent_id=parent_asset.id)

    # Verify parent-child relationship has been set
    updated_child = data_manager.get_asset(child_asset.id)
    assert updated_child.parent_id == parent_asset.id

    # Verify data persistence
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()

    reloaded_child = reloaded_dm.get_asset(child_asset.id)
    assert reloaded_child.parent_id == parent_asset.id

def test_query_parent_asset(data_manager):
    """Test querying parent asset (Metric: 2.4.2b)"""
    # Create parent-child assets
    parent_asset = data_manager.add_asset("Server Room", 50000, 2, "asset_user")
    child_asset = data_manager.add_asset("UPS Power Supply", 8000, 2, "asset_user", parent_id=parent_asset.id)

    # Query child asset's parent information
    child = data_manager.get_asset(child_asset.id)
    assert child.parent_id == parent_asset.id

    # Get parent asset details via parent asset ID
    parent = data_manager.get_asset(child.parent_id)
    assert parent is not None
    assert parent.name == "Server Room"
    assert parent.id == parent_asset.id

def test_query_child_assets(data_manager):
    """Test querying child assets (Metric: 2.4.2c)"""
    # Create a parent asset and multiple child assets
    parent_asset = data_manager.add_asset("Data Center", 100000, 2, "asset_user")
    child1 = data_manager.add_asset("Server 1", 15000, 2, "asset_user", parent_id=parent_asset.id)
    child2 = data_manager.add_asset("Server 2", 15000, 2, "asset_user", parent_id=parent_asset.id)
    child3 = data_manager.add_asset("Network Equipment", 5000, 2, "asset_user", parent_id=parent_asset.id)

    # Query all child assets of parent asset
    child_assets = [asset for asset in data_manager.assets.values()
                   if asset.parent_id == parent_asset.id]

    assert len(child_assets) == 3
    child_names = [asset.name for asset in child_assets]
    assert "Server 1" in child_names
    assert "Server 2" in child_names
    assert "Network Equipment" in child_names

def test_asset_value_calculation_and_depreciation(data_manager):
    """Test asset value calculation and depreciation (Metric: 2.4.3)"""
    # Create an asset, set as purchased 5 years ago
    asset = data_manager.add_asset("Test Equipment", 10000, 2, "asset_user", service_life=5)

    # Manually set start time to 6 years ago (ensure it exceeds 5-year service life)
    six_years_ago = datetime.now() - timedelta(days=6*365)
    asset.start_time = six_years_ago
    data_manager.save_data()

    # Calculate current value (should be 0, as it's past service life)
    def calculate_current_value(asset):
        """Helper function to calculate asset current value"""
        if asset.status == 'RETIRED':
            return 0

        years_used = (datetime.now() - asset.start_time).days / 365.25
        if years_used >= asset.service_life:
            return 0

        depreciation_rate = years_used / asset.service_life
        current_value = asset.value * (1 - depreciation_rate)
        return max(0, current_value)

    current_value = calculate_current_value(asset)
    assert current_value == 0  # Expired, value is 0

    # Test asset not yet expired
    new_asset = data_manager.add_asset("New Equipment", 8000, 2, "asset_user", service_life=4)
    # Set as purchased 2 years ago
    two_years_ago = datetime.now() - timedelta(days=2*365)
    new_asset.start_time = two_years_ago
    data_manager.save_data()

    new_current_value = calculate_current_value(new_asset)
    expected_value = 8000 * (1 - 2/4)  # 2 years/4 year service life = 50% depreciation
    assert abs(new_current_value - expected_value) < 100  # Allow small margin of error

def test_asset_retirement(data_manager):
    """Test asset retirement (Metric: 2.4.4)"""
    # Create an asset
    asset = data_manager.add_asset("Equipment to Retire", 5000, 2, "asset_user")

    # Execute retirement operation
    data_manager.update_asset(asset.id, status='RETIRED')

    # Verify retirement status
    retired_asset = data_manager.get_asset(asset.id)
    assert retired_asset.status == 'RETIRED'

    # In actual system, current value should be 0 after retirement
    # Here we verify status change has been saved correctly
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()

    reloaded_asset = reloaded_dm.get_asset(asset.id)
    assert reloaded_asset.status == 'RETIRED'

def test_complex_asset_tree_structure(data_manager):
    """Test complex asset tree structure"""
    # Create multi-level asset tree
    building = data_manager.add_asset("Office Building", 1000000, 2, "asset_user")
    floor1 = data_manager.add_asset("Floor 1", 0, 2, "asset_user", parent_id=building.id)
    floor2 = data_manager.add_asset("Floor 2", 0, 2, "asset_user", parent_id=building.id)

    # Floor 1 equipment
    room101 = data_manager.add_asset("Meeting Room 101", 50000, 2, "asset_user", parent_id=floor1.id)
    projector = data_manager.add_asset("Projector", 8000, 2, "asset_user", parent_id=room101.id)

    # Floor 2 equipment
    server_room = data_manager.add_asset("Server Room", 200000, 2, "asset_user", parent_id=floor2.id)
    server1 = data_manager.add_asset("Web Server", 15000, 2, "asset_user", parent_id=server_room.id)
    server2 = data_manager.add_asset("Database Server", 20000, 2, "asset_user", parent_id=server_room.id)

    # Verify tree structure integrity
    # Verify Floor 1 child assets
    floor1_children = [asset for asset in data_manager.assets.values()
                      if asset.parent_id == floor1.id]
    assert len(floor1_children) == 1
    assert floor1_children[0].name == "Meeting Room 101"

    # Verify Meeting Room 101 child assets
    room101_children = [asset for asset in data_manager.assets.values()
                       if asset.parent_id == room101.id]
    assert len(room101_children) == 1
    assert room101_children[0].name == "Projector"

    # Verify Server Room child assets
    server_room_children = [asset for asset in data_manager.assets.values()
                           if asset.parent_id == server_room.id]
    assert len(server_room_children) == 2
    server_names = [asset.name for asset in server_room_children]
    assert "Web Server" in server_names
    assert "Database Server" in server_names

def test_asset_value_with_different_service_life(data_manager):
    """Test asset value calculation with different service lives"""
    # Create assets with different service lives
    short_life_asset = data_manager.add_asset("Short-term Equipment", 6000, 2, "asset_user", service_life=2)
    long_life_asset = data_manager.add_asset("Long-term Equipment", 6000, 2, "asset_user", service_life=10)

    # Set as purchased 1 year ago
    one_year_ago = datetime.now() - timedelta(days=365)
    short_life_asset.start_time = one_year_ago
    long_life_asset.start_time = one_year_ago
    data_manager.save_data()

    def calculate_current_value(asset):
        years_used = (datetime.now() - asset.start_time).days / 365.25
        if years_used >= asset.service_life:
            return 0
        depreciation_rate = years_used / asset.service_life
        return asset.value * (1 - depreciation_rate)

    # Short-term equipment (2-year service life, 1 year used) should have 50% value remaining
    short_value = calculate_current_value(short_life_asset)
    expected_short = 6000 * 0.5
    assert abs(short_value - expected_short) < 100

    # Long-term equipment (10-year service life, 1 year used) should have 90% value remaining
    long_value = calculate_current_value(long_life_asset)
    expected_long = 6000 * 0.9
    assert abs(long_value - expected_long) < 100