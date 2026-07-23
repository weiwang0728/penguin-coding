#!/usr/bin/env python3
"""
pytest Configuration File
"""

import pytest
import sys
import os
import tempfile
import shutil

# Add source code path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

@pytest.fixture(scope="session")
def temp_db():
    """Create temporary database"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')

    yield db_path

    # Clean up temporary files
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_app_config():
    """Mock application configuration"""
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    }

# Set test environment variable
os.environ['FLASK_ENV'] = 'testing'