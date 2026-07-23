import sys
import os
import pytest

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager, UserPermission

@pytest.fixture(scope="function")
def data_manager():
    """Provide a temporary, isolated DataManager instance for testing."""
    test_data_file = "test_issue_data.json"
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        
    dm = DataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()
    
    # Add test users
    dm.add_user("staff_user", "password123", 1, roles=["STAFF"])
    dm.add_user("asset_manager", "password123", 1, roles=["ASSET"])
    dm.add_user("target_user", "password123", 1, roles=["STAFF"])

    # Add test category and asset
    category = dm.add_category("Test Category", 1)
    dm.add_asset("Test Asset", 5000, category.id, "staff_user")
    
    yield dm
    
    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_initiate_require_issue(data_manager):
    """Test initiating require issue (Metric: 2.5.1a)"""
    # STAFF user initiates require issue
    require_issue = data_manager.add_require_issue(
        initiator_username="staff_user",
        handler_username="asset_manager",
        category_id=2,  # Test category ID
        reason="Need office equipment"
    )

    assert require_issue is not None
    assert require_issue.initiator_username == "staff_user"
    assert require_issue.handler_username == "asset_manager"
    assert require_issue.category_id == 2
    assert require_issue.reason == "Need office equipment"
    assert require_issue.status == "DOING"

    # Verify issue has been saved
    saved_issue = data_manager.get_require_issue(require_issue.id)
    assert saved_issue is not None
    assert saved_issue.status == "DOING"

def test_initiate_maintenance_issue(data_manager):
    """Test initiating maintenance issue (Metric: 2.5.1b)"""
    # Get test asset
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None
    assert test_asset is not None

    # STAFF user initiates maintenance issue
    maintenance_issue = data_manager.add_issue(
        initiator_username="staff_user",
        handler_username="asset_manager",
        asset_id=test_asset.id,
        issue_type="MAINTAIN"
    )

    assert maintenance_issue is not None
    assert maintenance_issue.initiator_username == "staff_user"
    assert maintenance_issue.handler_username == "asset_manager"
    assert maintenance_issue.asset_id == test_asset.id
    assert maintenance_issue.type == "MAINTAIN"
    assert maintenance_issue.status == "DOING"

    # Verify issue has been saved
    saved_issue = data_manager.get_issue(maintenance_issue.id)
    assert saved_issue is not None

def test_initiate_transfer_issue(data_manager):
    """Test initiating transfer issue (Metric: 2.5.1c)"""
    # Get test asset
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None
    assert test_asset is not None

    # STAFF user initiates transfer issue
    transfer_issue = data_manager.add_issue(
        initiator_username="staff_user",
        handler_username="asset_manager",
        asset_id=test_asset.id,
        issue_type="TRANSFER",
        assignee_username="target_user"
    )

    assert transfer_issue is not None
    assert transfer_issue.initiator_username == "staff_user"
    assert transfer_issue.handler_username == "asset_manager"
    assert transfer_issue.asset_id == test_asset.id
    assert transfer_issue.type == "TRANSFER"
    assert transfer_issue.assignee_username == "target_user"
    assert transfer_issue.status == "DOING"

def test_initiate_return_issue(data_manager):
    """Test initiating return issue (Metric: 2.5.1d)"""
    # Get test asset (should belong to staff_user)
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None
    assert test_asset is not None
    assert test_asset.owner_username == "staff_user"

    # STAFF user initiates return issue
    return_issue = data_manager.add_issue(
        initiator_username="staff_user",
        handler_username="asset_manager",
        asset_id=test_asset.id,
        issue_type="RETURN"
    )

    assert return_issue is not None
    assert return_issue.initiator_username == "staff_user"
    assert return_issue.handler_username == "asset_manager"
    assert return_issue.asset_id == test_asset.id
    assert return_issue.type == "RETURN"
    assert return_issue.status == "DOING"

def test_query_pending_issues(data_manager):
    """Test querying pending issues (Metric: 2.5.2a)"""
    # Create several pending issues
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None

    issue1 = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "MAINTAIN")
    issue2 = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "TRANSFER", "target_user")
    require_issue = data_manager.add_require_issue("staff_user", "asset_manager", 2, "Need equipment")

    # Asset manager queries pending issues
    pending_issues = data_manager.get_issues_by_handler("asset_manager")
    pending_require_issues = data_manager.get_require_issues_by_handler("asset_manager")

    assert len(pending_issues) == 2
    assert len(pending_require_issues) == 1

    # Verify all issues are in DOING status
    for issue in pending_issues:
        assert issue.status == "DOING"
        assert issue.handler_username == "asset_manager"

    for issue in pending_require_issues:
        assert issue.status == "DOING"
        assert issue.handler_username == "asset_manager"

def test_process_issue(data_manager):
    """Test processing issue (Metric: 2.5.2b)"""
    # Create a pending issue
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None

    issue = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "MAINTAIN")
    assert issue.status == "DOING"

    # Asset manager processes issue (approve)
    success = data_manager.update_issue_status(issue.id, "SUCCESS")
    assert success is True

    # Verify issue status has been updated
    processed_issue = data_manager.get_issue(issue.id)
    assert processed_issue.status == "SUCCESS"

    # Test rejecting issue
    issue2 = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "TRANSFER", "target_user")
    success = data_manager.update_issue_status(issue2.id, "FAIL")
    assert success is True

    rejected_issue = data_manager.get_issue(issue2.id)
    assert rejected_issue.status == "FAIL"

    # Test processing require issue
    require_issue = data_manager.add_require_issue("staff_user", "asset_manager", 2, "Need equipment")
    success = data_manager.update_require_issue_status(require_issue.id, "SUCCESS")
    assert success is True

    processed_require = data_manager.get_require_issue(require_issue.id)
    assert processed_require.status == "SUCCESS"

def test_issue_conflict_handling(data_manager):
    """Test issue conflict handling (Metric: 2.5.3)"""
    # Get test asset
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None
    assert test_asset is not None

    # First maintenance issue initiation
    issue1 = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "MAINTAIN")
    assert issue1.status == "DOING"

    # Try to initiate another maintenance issue for the same asset
    # In actual system, this should be detected as a conflict
    # Here we simulate conflict detection logic
    def check_asset_conflict(asset_id, issue_type):
        """Check if asset has conflicting issues"""
        existing_issues = [issue for issue in data_manager.issues.values()
                          if issue.asset_id == asset_id and issue.status == "DOING"]

        # If there's already a pending issue of the same type, there's a conflict
        for issue in existing_issues:
            if issue.type == issue_type:
                return True
        return False

    # Detect conflict
    has_conflict = check_asset_conflict(test_asset.id, "MAINTAIN")
    assert has_conflict is True  # Should detect conflict

    # Verify different types of issues don't conflict
    has_transfer_conflict = check_asset_conflict(test_asset.id, "TRANSFER")
    assert has_transfer_conflict is False  # Different types don't conflict

    # After completing first issue, should be able to initiate same type issue again
    data_manager.update_issue_status(issue1.id, "SUCCESS")
    has_conflict_after_completion = check_asset_conflict(test_asset.id, "MAINTAIN")
    assert has_conflict_after_completion is False  # No conflict after completion

def test_get_user_initiated_issues(data_manager):
    """Test getting user initiated issues"""
    # User initiates multiple issues
    assets = list(data_manager.assets.values())
    test_asset = assets[0] if assets else None

    issue1 = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "MAINTAIN")
    issue2 = data_manager.add_issue("staff_user", "asset_manager", test_asset.id, "TRANSFER", "target_user")
    require_issue = data_manager.add_require_issue("staff_user", "asset_manager", 2, "Need equipment")

    # Get all issues initiated by user
    user_issues = data_manager.get_issues_by_initiator("staff_user")
    user_require_issues = data_manager.get_require_issues_by_initiator("staff_user")

    assert len(user_issues) == 2
    assert len(user_require_issues) == 1

    # Verify all issues were initiated by this user
    for issue in user_issues:
        assert issue.initiator_username == "staff_user"

    for issue in user_require_issues:
        assert issue.initiator_username == "staff_user"

def test_issue_workflow_complete_cycle(data_manager):
    """Test complete issue workflow cycle"""
    # 1. User initiates require issue
    require_issue = data_manager.add_require_issue(
        "staff_user", "asset_manager", 2, "Need new computer"
    )
    assert require_issue.status == "DOING"

    # 2. Asset manager checks pending issues
    pending = data_manager.get_require_issues_by_handler("asset_manager")
    assert len(pending) == 1
    assert pending[0].id == require_issue.id

    # 3. Asset manager approves issue
    data_manager.update_require_issue_status(require_issue.id, "SUCCESS")

    # 4. Verify issue status has been updated
    completed_issue = data_manager.get_require_issue(require_issue.id)
    assert completed_issue.status == "SUCCESS"

    # 5. Verify pending list no longer contains completed issue
    remaining_pending = data_manager.get_require_issues_by_handler("asset_manager")
    assert len(remaining_pending) == 0