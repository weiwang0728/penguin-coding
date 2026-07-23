import sys
import os
import pytest

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager

@pytest.fixture(scope="function")
def data_manager():
    """Provide a temporary, isolated DataManager instance for testing."""
    test_data_file = "test_asset_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # Add a default category and user
    dm.add_category("Default Category", 1)
    dm.add_user("asset_admin", "password", 1, roles=["ASSET"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_add_asset(data_manager):
    """Test adding asset (Metric: 2.4.1a)"""
    asset = data_manager.add_asset("Test Computer", 5000, 2, "asset_admin")
    assert asset is not None
    assert data_manager.get_asset(asset.id) is not None
    assert data_manager.get_asset(asset.id).name == "Test Computer"

def test_query_asset(data_manager):
    """Test querying asset (Metric: 2.4.1b)"""
    asset = data_manager.add_asset("Laptop", 6000, 2, "asset_admin")

    found_asset = data_manager.get_asset(asset.id)
    assert found_asset is not None
    assert found_asset.name == "Laptop"

def test_edit_asset(data_manager):
    """Test editing asset (Metric: 2.4.1c)"""
    asset = data_manager.add_asset("Old Monitor", 1000, 2, "asset_admin")

    data_manager.update_asset(asset.id, name="New Monitor", value=1200)

    edited_asset = data_manager.get_asset(asset.id)
    assert edited_asset.name == "New Monitor"
    assert edited_asset.value == 1200

def test_delete_asset(data_manager):
    """Test deleting asset (Metric: 2.4.1d)"""
    asset = data_manager.add_asset("Printer to Delete", 1500, 2, "asset_admin")
    asset_id = asset.id

    assert data_manager.get_asset(asset_id) is not None

    data_manager.delete_asset(asset_id)
    assert data_manager.get_asset(asset_id) is None

def test_retire_asset(data_manager):
    """Test retiring asset (Metric: 2.4.4)"""
    asset = data_manager.add_asset("Server", 20000, 2, "asset_admin")

    # In CLI, this would be a separate function, here we directly call update_asset to simulate
    data_manager.update_asset(asset.id, status='RETIRED')

    retired_asset = data_manager.get_asset(asset.id)
    assert retired_asset.status == 'RETIRED'