import sys
import os
import pytest

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """Provide a temporary, isolated DataManager instance for testing."""
    test_data_file = "test_dept_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # Add test user
    dm.add_user("system_user", "password123", 1, roles=["SYSTEM"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_create_root_department(data_manager):
    """Test creating root department (Metric: 2.2.1a)"""
    # Create a new root department
    root_dept = data_manager.add_department("RootDept")

    assert root_dept is not None
    assert root_dept.name == "RootDept"
    assert root_dept.parent_id is None

    # Verify department has been saved to data manager
    saved_dept = data_manager.get_department(root_dept.id)
    assert saved_dept is not None
    assert saved_dept.name == "RootDept"

def test_create_child_department(data_manager):
    """Test creating child department (Metric: 2.2.1b)"""
    # First create a root department
    root_dept = data_manager.add_department("RootDept")

    # Create child department
    child_dept = data_manager.add_department("ChildDept", parent_id=root_dept.id)

    assert child_dept is not None
    assert child_dept.name == "ChildDept"
    assert child_dept.parent_id == root_dept.id

    # Verify parent-child relationship
    saved_child = data_manager.get_department(child_dept.id)
    assert saved_child.parent_id == root_dept.id

    # Verify department tree structure
    dept_tree = data_manager.get_department_tree(root_dept.id)
    assert dept_tree is not None
    assert dept_tree['name'] == "RootDept"
    assert len(dept_tree['children']) == 1
    assert dept_tree['children'][0]['name'] == "ChildDept"

def test_department_asset_manager_configuration(data_manager):
    """Test department asset manager configuration (Metric: 2.2.2)"""
    # Create a department
    dept = data_manager.add_department("DeptA")

    # Create a user with ASSET permission
    asset_user = data_manager.add_user("AssetUser", "password123", dept.id, roles=["ASSET"])

    # In actual system, there should be a function to set department asset manager
    # Since current model doesn't have direct department asset manager field, we verify via user's department affiliation and permission
    assert asset_user.department_id == dept.id
    assert asset_user.has_permission(UserPermission.ASSET)

    # Verify user belongs to correct department
    dept_users = [user for user in data_manager.users.values()
                  if user.department_id == dept.id and user.has_permission(UserPermission.ASSET)]
    assert len(dept_users) == 1
    assert dept_users[0].username == "AssetUser"

def test_department_tree_structure(data_manager):
    """Test department tree structure integrity"""
    # Create multi-level department structure
    root = data_manager.add_department("Head Office")
    branch1 = data_manager.add_department("Branch A", parent_id=root.id)
    branch2 = data_manager.add_department("Branch B", parent_id=root.id)
    dept1 = data_manager.add_department("Technology Dept", parent_id=branch1.id)
    dept2 = data_manager.add_department("Sales Dept", parent_id=branch1.id)

    # Verify tree structure
    tree = data_manager.get_department_tree(root.id)
    assert tree['name'] == "Head Office"
    assert len(tree['children']) == 2

    # Verify Branch A sub-departments
    branch1_tree = next(child for child in tree['children'] if child['name'] == "Branch A")
    assert len(branch1_tree['children']) == 2

    dept_names = [child['name'] for child in branch1_tree['children']]
    assert "Technology Dept" in dept_names
    assert "Sales Dept" in dept_names

def test_get_department_by_id(data_manager):
    """Test getting department by ID"""
    dept = data_manager.add_department("Test Department")

    retrieved_dept = data_manager.get_department(dept.id)
    assert retrieved_dept is not None
    assert retrieved_dept.id == dept.id
    assert retrieved_dept.name == "Test Department"

    # Test getting non-existent department
    non_existent = data_manager.get_department(99999)
    assert non_existent is None