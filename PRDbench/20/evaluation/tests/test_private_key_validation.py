import pytest
import os
from cryptography.hazmat.primitives import serialization

def test_private_key_validation():
    """Test private key file reading and validation."""
    # Test with existing user private key
    test_key_path = "data/user_keys/test_user_private_key.pem"
    
    if os.path.exists(test_key_path):
        with open(test_key_path, "rb") as f:
            key_data = f.read()
        
        # Check PEM format
        assert b"-----BEGIN PRIVATE KEY-----" in key_data or b"-----BEGIN RSA PRIVATE KEY-----" in key_data
        assert b"-----END PRIVATE KEY-----" in key_data or b"-----END RSA PRIVATE KEY-----" in key_data
        
        # Verify it can be loaded as a private key
        private_key = serialization.load_pem_private_key(key_data, password=None)
        assert private_key is not None
        
        # Check key size (should be 4096 bits based on config)
        key_size = private_key.key_size
        assert key_size >= 2048  # At least 2048 bits for security
        
        # Verify we can get the public key from private key
        public_key = private_key.public_key()
        assert public_key is not None
    
    # Test CA private key validation
    ca_key_path = "data/keys/ca_private_key.pem"
    if os.path.exists(ca_key_path):
        with open(ca_key_path, "rb") as f:
            ca_key_data = f.read()
        
        # Verify CA private key can be loaded
        ca_private_key = serialization.load_pem_private_key(ca_key_data, password=None)
        assert ca_private_key is not None
        assert ca_private_key.key_size >= 2048