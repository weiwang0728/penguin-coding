import pytest
import sys
import os

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ca_modules.certificate_authority import CertificateAuthority

def test_ca_initialization():
    """Test CertificateAuthority class initialization."""
    ca = CertificateAuthority()
    assert ca.private_key is not None
    assert ca.certificate is not None
    assert ca.crl is not None

def test_certificate_generation():
    """Test certificate generation algorithm correctness."""
    ca = CertificateAuthority()
    assert ca.certificate.subject == ca.certificate.issuer  # Self-signed
    assert ca.private_key.key_size >= 2048  # Secure key size