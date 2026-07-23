import pytest
import sys
import importlib
import os

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def test_python_version_compatibility():
    """Test Python version compatibility (3.6+)."""
    # Check Python version
    assert sys.version_info >= (3, 6), f"Python version {sys.version_info} is not supported. Requires Python 3.6+"
    
    # Test that required modules can be imported
    required_modules = [
        'cryptography',
        'datetime',
        'os',
        'hashlib'
    ]
    
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
        except ImportError:
            pytest.fail(f"Required module '{module_name}' is not available")
    
    # Test cryptography library specific imports
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa, padding
        from cryptography import x509
        from cryptography.x509.oid import NameOID
    except ImportError as e:
        pytest.fail(f"Failed to import cryptography components: {e}")
    
    # Test that the CA modules can be imported
    try:
        from ca_modules import certificate_authority, user_operations, config
    except ImportError as e:
        pytest.fail(f"Failed to import CA modules: {e}")