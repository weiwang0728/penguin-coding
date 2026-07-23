import pytest
import sys
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography import x509

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ca_modules.certificate_authority import CertificateAuthority
from ca_modules import config

def test_crypto_library_usage():
    """Test that the system correctly uses standard cryptography libraries."""
    ca = CertificateAuthority()
    
    # Test RSA key generation
    assert ca.private_key is not None
    assert isinstance(ca.private_key, rsa.RSAPrivateKey)
    
    # Test certificate generation
    assert ca.certificate is not None
    assert isinstance(ca.certificate, x509.Certificate)
    
    # Test that proper hash algorithm is used
    expected_hash = getattr(hashes, config.HASH_ALGORITHM)
    assert expected_hash == hashes.SHA256
    
    # Test RSA encryption/decryption functionality
    test_data = b"Test encryption data"
    public_key = ca.private_key.public_key()
    
    # Test encryption
    encrypted_data = public_key.encrypt(
        test_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    assert encrypted_data != test_data
    assert len(encrypted_data) > 0
    
    # Test decryption
    decrypted_data = ca.private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    assert decrypted_data == test_data
    
    # Test certificate signature verification
    try:
        public_key.verify(
            ca.certificate.signature,
            ca.certificate.tbs_certificate_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        # If no exception is raised, signature is valid
        signature_valid = True
    except Exception:
        signature_valid = False
    
    assert signature_valid, "Certificate signature verification failed"
    
    # Test PEM serialization
    pem_private = ca.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    assert b"-----BEGIN PRIVATE KEY-----" in pem_private
    
    pem_cert = ca.certificate.public_bytes(serialization.Encoding.PEM)
    assert b"-----BEGIN CERTIFICATE-----" in pem_cert