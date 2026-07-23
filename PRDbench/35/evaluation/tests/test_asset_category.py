import sys
import os
import pytest

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """Provide a temporary, isolated DataManager instance for testing."""
    test_data_file = "test_category_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # Add test user
    dm.add_user("asset_user", "password123", 1, roles=["ASSET"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_create_root_asset_category(data_manager):
    """Test creating root asset category (Metric: 2.3.1a)"""
    # Create a new root asset category
    root_category = data_manager.add_category("RootCategory")

    assert root_category is not None
    assert root_category.name == "RootCategory"
    assert root_category.parent_id is None

    # Verify category has been saved to data manager
    saved_category = data_manager.get_category(root_category.id)
    assert saved_category is not None
    assert saved_category.name == "RootCategory"

def test_create_child_asset_category(data_manager):
    """Test creating child asset category (Metric: 2.3.1b)"""
    # First create a root category
    root_category = data_manager.add_category("RootCategory")

    # Create child category
    child_category = data_manager.add_category("ChildCategory", parent_id=root_category.id)

    assert child_category is not None
    assert child_category.name == "ChildCategory"
    assert child_category.parent_id == root_category.id

    # Verify parent-child relationship
    saved_child = data_manager.get_category(child_category.id)
    assert saved_child.parent_id == root_category.id

    # Verify category tree structure
    category_tree = data_manager.get_category_tree(root_category.id)
    assert category_tree is not None
    assert category_tree['name'] == "RootCategory"
    assert len(category_tree['children']) == 1
    assert category_tree['children'][0]['name'] == "ChildCategory"

def test_create_custom_attribute(data_manager):
    """Test creating custom attribute (Metric: 2.3.2a)"""
    # Add custom attribute
    data_manager.custom_attrs.add("Brand")
    data_manager.save_data()

    # Verify attribute has been added
    assert "Brand" in data_manager.custom_attrs

    # Reload data to verify persistence
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()

    assert "Brand" in reloaded_dm.custom_attrs

def test_add_custom_attribute_to_asset(data_manager):
    """Test adding custom attribute value to asset (Metric: 2.3.2b)"""
    # First create an asset category and asset
    category = data_manager.add_category("Computer Equipment")
    asset = data_manager.add_asset("Test Computer", 5000, category.id, "asset_user")

    # Add custom attribute
    data_manager.custom_attrs.add("Brand")

    # Set custom attribute value for asset
    asset.custom_attrs["Brand"] = "Dell"
    data_manager.save_data()

    # Verify attribute value has been set
    saved_asset = data_manager.get_asset(asset.id)
    assert "Brand" in saved_asset.custom_attrs
    assert saved_asset.custom_attrs["Brand"] == "Dell"

    # Reload data to verify persistence
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()

    reloaded_asset = reloaded_dm.get_asset(asset.id)
    assert "Brand" in reloaded_asset.custom_attrs
    assert reloaded_asset.custom_attrs["Brand"] == "Dell"

def test_asset_category_tree_structure(data_manager):
    """Test asset category tree structure integrity"""
    # Create multi-level category structure
    root = data_manager.add_category("Equipment")
    it_equipment = data_manager.add_category("IT Equipment", parent_id=root.id)
    office_equipment = data_manager.add_category("Office Equipment", parent_id=root.id)
    computers = data_manager.add_category("Computers", parent_id=it_equipment.id)
    servers = data_manager.add_category("Servers", parent_id=it_equipment.id)

    # Verify tree structure
    tree = data_manager.get_category_tree(root.id)
    assert tree['name'] == "Equipment"
    assert len(tree['children']) == 2

    # Verify IT Equipment subcategories
    it_tree = next(child for child in tree['children'] if child['name'] == "IT Equipment")
    assert len(it_tree['children']) == 2

    category_names = [child['name'] for child in it_tree['children']]
    assert "Computers" in category_names
    assert "Servers" in category_names

def test_get_assets_by_category(data_manager):
    """Test getting assets by category"""
    # Create categories and assets
    category = data_manager.add_category("Laptops")
    asset1 = data_manager.add_asset("ThinkPad", 8000, category.id, "asset_user")
    asset2 = data_manager.add_asset("MacBook", 12000, category.id, "asset_user")

    # Create asset in another category
    other_category = data_manager.add_category("Printers")
    asset3 = data_manager.add_asset("HP Printer", 2000, other_category.id, "asset_user")

    # Get laptop category assets
    laptop_assets = data_manager.get_assets_by_category(category.id)
    assert len(laptop_assets) == 2

    asset_names = [asset.name for asset in laptop_assets]
    assert "ThinkPad" in asset_names
    assert "MacBook" in asset_names
    assert "HP Printer" not in asset_names

def test_multiple_custom_attributes(data_manager):
    """Test multiple custom attributes"""
    # Add multiple custom attributes
    attributes = ["Brand", "Model", "SerialNumber", "PurchaseDate"]
    for attr in attributes:
        data_manager.custom_attrs.add(attr)

    # Create asset and set multiple attributes
    category = data_manager.add_category("Servers")
    asset = data_manager.add_asset("Web Server", 15000, category.id, "asset_user")

    asset.custom_attrs.update({
        "Brand": "Dell",
        "Model": "PowerEdge R740",
        "SerialNumber": "ABC123456",
        "PurchaseDate": "2024-01-15"
    })
    data_manager.save_data()

    # Verify all attributes have been set correctly
    saved_asset = data_manager.get_asset(asset.id)
    assert saved_asset.custom_attrs["Brand"] == "Dell"
    assert saved_asset.custom_attrs["Model"] == "PowerEdge R740"
    assert saved_asset.custom_attrs["SerialNumber"] == "ABC123456"
    assert saved_asset.custom_attrs["PurchaseDate"] == "2024-01-15"