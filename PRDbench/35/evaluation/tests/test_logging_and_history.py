import sys
import os
import pytest
from datetime import datetime

# Add src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from models import DataManager

# Simple logging class for testing
class ChangeLog:
    """Change log class"""
    def __init__(self, log_id, entity_type, entity_id, operation, user, timestamp, details=None):
        self.id = log_id
        self.entity_type = entity_type  # 'asset', 'user', 'department', etc.
        self.entity_id = entity_id
        self.operation = operation  # 'CREATE', 'UPDATE', 'DELETE'
        self.user = user
        self.timestamp = timestamp
        self.details = details or {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'operation': self.operation,
            'user': self.user,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data):
        log = cls(
            data['id'],
            data['entity_type'],
            data['entity_id'],
            data['operation'],
            data['user'],
            datetime.fromisoformat(data['timestamp']),
            data.get('details', {})
        )
        return log

class SystemLog:
    """System operation log class"""
    def __init__(self, log_id, user, operation, timestamp, details=None):
        self.id = log_id
        self.user = user
        self.operation = operation  # 'LOGIN', 'LOGOUT', 'CREATE_ASSET', etc.
        self.timestamp = timestamp
        self.details = details or {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'operation': self.operation,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details
        }
    
    @classmethod
    def from_dict(cls, data):
        log = cls(
            data['id'],
            data['user'],
            data['operation'],
            datetime.fromisoformat(data['timestamp']),
            data.get('details', {})
        )
        return log

# Extend DataManager to support logging
class LoggingDataManager(DataManager):
    """Data manager with logging support"""
    def __init__(self):
        super().__init__()
        self.change_logs = {}
        self.system_logs = {}
        self.next_ids.update({
            'change_log': 1,
            'system_log': 1
        })

    def add_change_log(self, entity_type, entity_id, operation, user, details=None):
        """Add change log"""
        log_id = self.get_next_id('change_log')
        log = ChangeLog(log_id, entity_type, entity_id, operation, user, datetime.now(), details)
        self.change_logs[log_id] = log
        return log

    def add_system_log(self, user, operation, details=None):
        """Add system log"""
        log_id = self.get_next_id('system_log')
        log = SystemLog(log_id, user, operation, datetime.now(), details)
        self.system_logs[log_id] = log
        return log

    def get_asset_change_history(self, asset_id):
        """Get asset change history"""
        return [log for log in self.change_logs.values()
                if log.entity_type == 'asset' and log.entity_id == asset_id]

    def get_system_logs_by_user(self, user):
        """Get system operation logs by user"""
        return [log for log in self.system_logs.values() if log.user == user]

    def update_asset_with_logging(self, asset_id, user, **kwargs):
        """Update asset and record change log"""
        asset = self.get_asset(asset_id)
        if not asset:
            return False

        # Record values before change
        old_values = {}
        for key, new_value in kwargs.items():
            if hasattr(asset, key):
                old_values[key] = getattr(asset, key)

        # Execute update
        success = self.update_asset(asset_id, **kwargs)

        if success and old_values:
            # Record change log
            details = {
                'old_values': old_values,
                'new_values': kwargs
            }
            self.add_change_log('asset', asset_id, 'UPDATE', user, details)

        return success

@pytest.fixture(scope="function")
def logging_data_manager():
    """Provide a data manager instance with logging support"""
    test_data_file = "test_logging_data.json"

    if os.path.exists(test_data_file):
        os.remove(test_data_file)

    dm = LoggingDataManager()
    dm.DATA_FILE = test_data_file
    dm.load_data()

    # Add test user
    dm.add_user("test_user", "password123", 1, roles=["ASSET"])

    yield dm

    if os.path.exists(test_data_file):
        os.remove(test_data_file)

def test_asset_change_history_recording(logging_data_manager):
    """Test asset change history recording (Metric: 2.6.1)"""
    dm = logging_data_manager

    # Create asset
    asset = dm.add_asset("Test Computer", 5000, 2, "test_user")

    # Record creation log
    create_log = dm.add_change_log('asset', asset.id, 'CREATE', 'test_user',
                                  {'name': 'Test Computer', 'value': 5000})

    # Modify asset name
    dm.update_asset_with_logging(asset.id, 'test_user', name="New Computer", value=6000)

    # Modify asset status again
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_USE')

    # Get asset change history
    change_history = dm.get_asset_change_history(asset.id)

    # Verify change history records
    assert len(change_history) >= 3  # Create + 2 modifications

    # Verify creation record
    create_record = next((log for log in change_history if log.operation == 'CREATE'), None)
    assert create_record is not None
    assert create_record.user == 'test_user'
    assert create_record.entity_id == asset.id

    # Verify modification records
    update_records = [log for log in change_history if log.operation == 'UPDATE']
    assert len(update_records) == 2

    # Verify first modification record (name and value)
    name_update = next((log for log in update_records
                       if 'name' in log.details.get('new_values', {})), None)
    assert name_update is not None
    assert name_update.details['old_values']['name'] == 'Test Computer'
    assert name_update.details['new_values']['name'] == 'New Computer'
    assert name_update.details['old_values']['value'] == 5000
    assert name_update.details['new_values']['value'] == 6000

    # Verify second modification record (status)
    status_update = next((log for log in update_records
                         if 'status' in log.details.get('new_values', {})), None)
    assert status_update is not None
    assert status_update.details['old_values']['status'] == 'IDLE'
    assert status_update.details['new_values']['status'] == 'IN_USE'

def test_system_operation_logging(logging_data_manager):
    """Test system operation logging (Metric: 2.6.2)"""
    dm = logging_data_manager

    # Record user login
    login_log = dm.add_system_log('test_user', 'LOGIN', {'ip': '192.168.1.100'})

    # Record create asset operation
    asset = dm.add_asset("Server", 15000, 2, "test_user")
    create_asset_log = dm.add_system_log('test_user', 'CREATE_ASSET',
                                        {'asset_id': asset.id, 'asset_name': 'Server'})

    # Record modify user operation
    modify_user_log = dm.add_system_log('admin', 'MODIFY_USER',
                                       {'target_user': 'test_user', 'action': 'change_role'})

    # Record user logout
    logout_log = dm.add_system_log('test_user', 'LOGOUT')

    # Verify all logs have been recorded
    all_logs = list(dm.system_logs.values())
    assert len(all_logs) == 4

    # Verify login log
    assert login_log.user == 'test_user'
    assert login_log.operation == 'LOGIN'
    assert login_log.details['ip'] == '192.168.1.100'

    # Verify create asset log
    assert create_asset_log.user == 'test_user'
    assert create_asset_log.operation == 'CREATE_ASSET'
    assert create_asset_log.details['asset_name'] == 'Server'

    # Verify modify user log
    assert modify_user_log.user == 'admin'
    assert modify_user_log.operation == 'MODIFY_USER'
    assert modify_user_log.details['target_user'] == 'test_user'

    # Verify logout log
    assert logout_log.user == 'test_user'
    assert logout_log.operation == 'LOGOUT'

def test_get_user_operation_logs(logging_data_manager):
    """Test getting specific user's operation logs"""
    dm = logging_data_manager

    # Record multiple user operations
    dm.add_system_log('user1', 'LOGIN')
    dm.add_system_log('user2', 'LOGIN')
    dm.add_system_log('user1', 'CREATE_ASSET', {'asset_name': 'Computer'})
    dm.add_system_log('user1', 'LOGOUT')
    dm.add_system_log('user2', 'DELETE_ASSET', {'asset_id': 123})

    # Get user1's operation logs
    user1_logs = dm.get_system_logs_by_user('user1')
    assert len(user1_logs) == 3

    operations = [log.operation for log in user1_logs]
    assert 'LOGIN' in operations
    assert 'CREATE_ASSET' in operations
    assert 'LOGOUT' in operations

    # Get user2's operation logs
    user2_logs = dm.get_system_logs_by_user('user2')
    assert len(user2_logs) == 2

    user2_operations = [log.operation for log in user2_logs]
    assert 'LOGIN' in user2_operations
    assert 'DELETE_ASSET' in user2_operations

def test_comprehensive_asset_lifecycle_logging(logging_data_manager):
    """Test complete asset lifecycle logging"""
    dm = logging_data_manager

    # 1. Create asset
    asset = dm.add_asset("Lifecycle Test Equipment", 8000, 2, "test_user")
    dm.add_change_log('asset', asset.id, 'CREATE', 'test_user',
                     {'name': 'Lifecycle Test Equipment', 'value': 8000, 'status': 'IDLE'})
    dm.add_system_log('test_user', 'CREATE_ASSET', {'asset_id': asset.id})

    # 2. Modify asset information
    dm.update_asset_with_logging(asset.id, 'test_user', description="Add description information")
    dm.add_system_log('test_user', 'UPDATE_ASSET', {'asset_id': asset.id, 'field': 'description'})

    # 3. Asset put into use
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_USE')
    dm.add_system_log('test_user', 'ASSET_IN_USE', {'asset_id': asset.id})

    # 4. Asset maintenance
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_MAINTAIN')
    dm.add_system_log('test_user', 'ASSET_MAINTENANCE', {'asset_id': asset.id})

    # 5. Maintenance complete, put back into use
    dm.update_asset_with_logging(asset.id, 'test_user', status='IN_USE')
    dm.add_system_log('test_user', 'ASSET_MAINTENANCE_COMPLETE', {'asset_id': asset.id})

    # 6. Asset retirement
    dm.update_asset_with_logging(asset.id, 'test_user', status='RETIRED')
    dm.add_system_log('test_user', 'ASSET_RETIRED', {'asset_id': asset.id})

    # Verify change history integrity
    change_history = dm.get_asset_change_history(asset.id)
    assert len(change_history) == 6  # Create + 5 changes (including description modification)

    # Verify operation order
    sorted_changes = sorted(change_history, key=lambda x: x.timestamp)
    operations = [log.operation for log in sorted_changes]
    assert operations[0] == 'CREATE'
    assert operations[-1] == 'UPDATE'  # Last one is retirement operation

    # Verify system log integrity
    user_logs = dm.get_system_logs_by_user('test_user')
    assert len(user_logs) == 6

    log_operations = [log.operation for log in user_logs]
    assert 'CREATE_ASSET' in log_operations
    assert 'ASSET_RETIRED' in log_operations

def test_log_timestamp_accuracy(logging_data_manager):
    """Test log timestamp accuracy"""
    dm = logging_data_manager

    # Record time before operation
    before_time = datetime.now()

    # Execute operation and record log
    log = dm.add_system_log('test_user', 'TEST_OPERATION')

    # Record time after operation
    after_time = datetime.now()

    # Verify timestamp is within reasonable range
    assert before_time <= log.timestamp <= after_time

    # Verify timestamp format is correct (can be serialized and deserialized)
    log_dict = log.to_dict()
    restored_log = SystemLog.from_dict(log_dict)
    assert restored_log.timestamp == log.timestamp

def test_log_details_preservation(logging_data_manager):
    """Test log details information preservation"""
    dm = logging_data_manager

    # Create log with complex details
    complex_details = {
        'old_values': {'name': 'Old Name', 'value': 1000, 'status': 'IDLE'},
        'new_values': {'name': 'New Name', 'value': 1500, 'status': 'IN_USE'},
        'user_ip': '192.168.1.100',
        'user_agent': 'Mozilla/5.0...',
        'additional_info': {
            'reason': 'Equipment upgrade',
            'approved_by': 'manager'
        }
    }

    log = dm.add_change_log('asset', 123, 'UPDATE', 'test_user', complex_details)

    # Verify details information is completely preserved
    assert log.details == complex_details
    assert log.details['old_values']['name'] == 'Old Name'
    assert log.details['new_values']['value'] == 1500
    assert log.details['additional_info']['reason'] == 'Equipment upgrade'

    # Verify details information is not lost after serialization and deserialization
    log_dict = log.to_dict()
    restored_log = ChangeLog.from_dict(log_dict)
    assert restored_log.details == complex_details