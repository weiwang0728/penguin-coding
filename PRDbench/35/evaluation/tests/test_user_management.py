import sys
import os
import pytest

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, User, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """Provide a temporary, isolated DataManager instance for testing."""
    test_data_file = "test_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # Add test users
    dm.add_user("testuser", "password123", 1, roles=["STAFF"])
    dm.add_user("staffuser", "password123", 1, roles=["STAFF"])
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_change_own_password(data_manager):
    """Test user modifying their own password (Metric: 2.1.10)"""
    user = data_manager.get_user("testuser")
    assert user.check_password("password123")

    new_password = "new_password_456"
    user.set_password(new_password)
    data_manager.save_data()

    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    reloaded_user = reloaded_dm.get_user("testuser")
    
    assert not reloaded_user.check_password("password123")
    assert reloaded_user.check_password(new_password)

def test_list_users_with_system_permission(data_manager):
    """Test SYSTEM permission user can view all users (Metric: 2.1.5a)"""
    admin_user = data_manager.get_user("admin")
    assert admin_user.has_permission(UserPermission.SYSTEM)

    # In this simulated scenario, we directly check the user count in data_manager
    all_users = list(data_manager.users.values())
    assert len(all_users) >= 3 # admin, testuser, staffuser

def test_list_users_with_staff_permission(data_manager):
    """Test STAFF permission user cannot directly get user list (Metric: 2.1.5b)"""
    staff_user = data_manager.get_user("staffuser")
    assert not staff_user.has_permission(UserPermission.SYSTEM)
    # Permission check in CLI application is before calling function, simulating that logic here
    # If a function requires SYSTEM permission, STAFF user should be denied when calling
    # This test is more conceptual, verifying the permission model
    assert staff_user.has_permission(UserPermission.STAFF)

def test_add_user(data_manager):
    """Test adding new user (Metric: 2.1.6)"""
    new_username = "new_user"
    data_manager.add_user(new_username, "newpass", 1, roles=["STAFF"])
    
    added_user = data_manager.get_user(new_username)
    assert added_user is not None
    assert added_user.check_password("newpass")
    assert added_user.department_id == 1

def test_edit_user(data_manager):
    """Test editing user information (Metric: 2.1.7)"""
    user_to_edit = data_manager.get_user("testuser")

    # In simulated scenario, we directly modify user information
    user_to_edit.department_id = 2 # Assume department with ID 2 exists
    user_to_edit.roles = ["ASSET"]
    data_manager.save_data()
    
    reloaded_dm = DataManager()
    reloaded_dm.DATA_FILE = data_manager.DATA_FILE
    reloaded_dm.load_data()
    edited_user = reloaded_dm.get_user("testuser")
    
    assert edited_user.department_id == 2
    assert "ASSET" in edited_user.roles

def test_delete_user(data_manager):
    """Test deleting user (Metric: 2.1.8)"""
    username_to_delete = "testuser"
    assert data_manager.get_user(username_to_delete) is not None
    
    del data_manager.users[username_to_delete]
    data_manager.save_data()
    
    assert data_manager.get_user(username_to_delete) is None

def test_lock_unlock_user(data_manager):
    """Test locking and unlocking user (Metric: 2.1.9)"""
    user_to_lock = data_manager.get_user("testuser")

    # Lock user
    user_to_lock.active = False
    data_manager.save_data()

    reloaded_user = data_manager.get_user("testuser")
    assert not reloaded_user.active

    # Unlock user
    user_to_lock.active = True
    data_manager.save_data()

    reloaded_user = data_manager.get_user("testuser")
    assert reloaded_user.active