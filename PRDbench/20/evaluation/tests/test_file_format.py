import pytest
import os
from cryptography.hazmat.primitives import serialization
from cryptography import x509

def test_file_format_standards():
    """Test that all generated files conform to standard formats."""
    
    # Test CA certificate format (X.509 standard)
    ca_cert_path = "data/certs/ca_certificate.pem"
    if os.path.exists(ca_cert_path):
        with open(ca_cert_path, "rb") as f:
            cert_data = f.read()
        
        # Test PEM format
        assert b"-----BEGIN CERTIFICATE-----" in cert_data
        assert b"-----END CERTIFICATE-----" in cert_data
        
        # Test X.509 compliance
        cert = x509.load_pem_x509_certificate(cert_data)
        assert cert.version == x509.Version.v3  # Should be X.509 v3
        assert cert.serial_number is not None
        assert cert.subject is not None
        assert cert.issuer is not None
        assert cert.not_valid_before is not None
        assert cert.not_valid_after is not None
    
    # Test CA private key format (PKCS#8 standard)
    ca_key_path = "data/keys/ca_private_key.pem"
    if os.path.exists(ca_key_path):
        with open(ca_key_path, "rb") as f:
            key_data = f.read()
        
        # Test PEM format
        assert (b"-----BEGIN PRIVATE KEY-----" in key_data or 
                b"-----BEGIN RSA PRIVATE KEY-----" in key_data)
        assert (b"-----END PRIVATE KEY-----" in key_data or 
                b"-----END RSA PRIVATE KEY-----" in key_data)
        
        # Test that it can be loaded as a valid private key
        private_key = serialization.load_pem_private_key(key_data, password=None)
        assert private_key is not None
    
    # Test user certificate format
    user_cert_path = "data/certs/test_user.pem"
    if os.path.exists(user_cert_path):
        with open(user_cert_path, "rb") as f:
            user_cert_data = f.read()
        
        # Test PEM format
        assert b"-----BEGIN CERTIFICATE-----" in user_cert_data
        assert b"-----END CERTIFICATE-----" in user_cert_data
        
        # Test X.509 compliance
        user_cert = x509.load_pem_x509_certificate(user_cert_data)
        assert user_cert.version == x509.Version.v3
        assert user_cert.serial_number is not None
    
    # Test CRL format
    crl_path = "data/crl/ca_crl.pem"
    if os.path.exists(crl_path):
        with open(crl_path, "rb") as f:
            crl_data = f.read()
        
        # Test PEM format
        assert b"-----BEGIN X509 CRL-----" in crl_data
        assert b"-----END X509 CRL-----" in crl_data
        
        # Test that it can be loaded as a valid CRL
        crl = x509.load_pem_x509_crl(crl_data)
        assert crl is not None
        assert crl.issuer is not None
        assert crl.last_update is not None
        assert crl.next_update is not None
    
    # Test user public key format
    user_pubkey_path = "data/user_keys/test_user_public_key.pem"
    if os.path.exists(user_pubkey_path):
        with open(user_pubkey_path, "rb") as f:
            pubkey_data = f.read()
        
        # Test PEM format
        assert b"-----BEGIN PUBLIC KEY-----" in pubkey_data
        assert b"-----END PUBLIC KEY-----" in pubkey_data
        
        # Test that it can be loaded as a valid public key
        public_key = serialization.load_pem_public_key(pubkey_data)
        assert public_key is not None