import pytest
import sys
import os

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ca_modules import user_operations
from ca_modules.certificate_authority import CertificateAuthority

def test_user_operations():
    """Test UserOperations class functionality."""
    ca = CertificateAuthority()
    
    # Test that user operations functions exist and are callable
    assert callable(user_operations.generate_user_keys_flow)
    assert callable(user_operations.issue_certificate_flow)
    assert callable(user_operations.authenticate_user_flow)
    assert callable(user_operations.revoke_certificate_flow)
    assert callable(user_operations.encrypt_file_flow)
    assert callable(user_operations.decrypt_file_flow)
    
    # Test CA integration
    assert ca is not None
    assert hasattr(ca, 'issue_certificate')
    assert hasattr(ca, 'is_revoked')
    assert hasattr(ca, 'revoke_certificate')