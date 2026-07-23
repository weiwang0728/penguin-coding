import pytest
import os
import sys

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ca_modules import config

def test_file_structure_organization():
    """Test that the system follows proper file structure organization."""
    
    # Test that required directories exist or can be created
    required_dirs = [
        config.DATA_DIR,
        config.CERT_DIR,
        config.CRL_DIR,
        config.KEY_DIR,
        config.LOG_DIR,
        config.USER_KEY_DIR
    ]
    
    for dir_path in required_dirs:
        # Check if directory exists or can be created
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                dir_created = True
            except Exception:
                dir_created = False
        else:
            dir_created = True
        
        assert dir_created, f"Required directory {dir_path} cannot be created or accessed"
    
    # Test file path configurations
    assert config.CA_KEY_PATH.endswith('.pem')
    assert config.CA_CERT_PATH.endswith('.pem')
    assert config.CA_CRL_PATH.endswith('.pem')
    assert config.LOG_FILE.endswith('.log')
    
    # Test that paths are properly organized
    assert 'keys' in config.CA_KEY_PATH
    assert 'certs' in config.CA_CERT_PATH
    assert 'crl' in config.CA_CRL_PATH
    assert 'logs' in config.LOG_FILE
    assert 'user_keys' in config.USER_KEY_DIR
    
    # Test that data directory structure is logical
    assert config.CERT_DIR.startswith(config.DATA_DIR)
    assert config.CRL_DIR.startswith(config.DATA_DIR)
    assert config.KEY_DIR.startswith(config.DATA_DIR)
    assert config.USER_KEY_DIR.startswith(config.DATA_DIR)
    
    # Test that log directory is separate from data
    assert not config.LOG_DIR.startswith(config.DATA_DIR)