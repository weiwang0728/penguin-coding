import pytest
import os
from cryptography.hazmat.primitives import serialization
from cryptography import x509

def test_ca_pem_format():
    """Test that CA key and certificate files are in proper PEM format."""
    ca_key_path = "data/keys/ca_private_key.pem"
    ca_cert_path = "data/certs/ca_certificate.pem"
    
    # Test CA private key PEM format
    if os.path.exists(ca_key_path):
        with open(ca_key_path, "rb") as f:
            key_data = f.read()
            # Check PEM format headers
            assert b"-----BEGIN PRIVATE KEY-----" in key_data or b"-----BEGIN RSA PRIVATE KEY-----" in key_data
            assert b"-----END PRIVATE KEY-----" in key_data or b"-----END RSA PRIVATE KEY-----" in key_data
            
            # Verify it can be loaded as a private key
            private_key = serialization.load_pem_private_key(key_data, password=None)
            assert private_key is not None
    
    # Test CA certificate PEM format
    if os.path.exists(ca_cert_path):
        with open(ca_cert_path, "rb") as f:
            cert_data = f.read()
            # Check PEM format headers
            assert b"-----BEGIN CERTIFICATE-----" in cert_data
            assert b"-----END CERTIFICATE-----" in cert_data
            
            # Verify it can be loaded as a certificate
            certificate = x509.load_pem_x509_certificate(cert_data)
            assert certificate is not None