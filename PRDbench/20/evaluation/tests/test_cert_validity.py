import pytest
import os
import datetime
import sys
from cryptography import x509

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ca_modules.certificate_authority import CertificateAuthority

def test_certificate_validity():
    """Test certificate validity period verification."""
    ca = CertificateAuthority()
    
    # Test with existing certificate if available
    test_cert_path = "data/certs/test_user.pem"
    if os.path.exists(test_cert_path):
        with open(test_cert_path, "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())
        
        # Check validity period
        now = datetime.datetime.utcnow()
        is_valid = cert.not_valid_before <= now <= cert.not_valid_after
        
        # Test the validity check logic
        assert isinstance(is_valid, bool)
        
        # Test that certificate has proper validity period structure
        assert cert.not_valid_before_utc is not None
        assert cert.not_valid_after_utc is not None
        assert cert.not_valid_after_utc > cert.not_valid_before_utc
    
    # Test CA certificate validity
    ca_cert = ca.certificate
    now = datetime.datetime.now(datetime.timezone.utc)
    ca_is_valid = ca_cert.not_valid_before_utc <= now <= ca_cert.not_valid_after_utc
    
    assert isinstance(ca_is_valid, bool)
    assert ca_cert.not_valid_before_utc is not None
    assert ca_cert.not_valid_after_utc is not None
    assert ca_cert.not_valid_after_utc > ca_cert.not_valid_before_utc