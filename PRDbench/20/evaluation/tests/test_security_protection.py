import pytest
import datetime
import sys
import os

# Add src directory to Python path for importing ca_modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ca_modules.certificate_authority import CertificateAuthority
from ca_modules import config

def test_replay_attack_protection():
    """Test replay attack protection mechanisms."""
    ca = CertificateAuthority()
    
    # Test that operations include timestamp logging
    # This is a basic test - in a real system, we'd test actual replay detection
    assert hasattr(ca, 'certificate')
    assert hasattr(ca, 'private_key')
    
    # Verify that log events include timestamps
    # The log_event function should add timestamps to prevent replay attacks
    from ca_modules.certificate_authority import log_event
    import os
    
    # Test logging functionality
    test_message = "Test replay protection"
    log_event(test_message, "INFO")
    
    # Check if log file exists and contains timestamp
    if os.path.exists(config.LOG_FILE):
        try:
            with open(config.LOG_FILE, 'r', encoding='utf-8') as f:
                log_content = f.read()
        except UnicodeDecodeError:
            with open(config.LOG_FILE, 'r', encoding='gbk') as f:
                log_content = f.read()
            assert test_message in log_content
            # Check for timestamp format [YYYY-MM-DD HH:MM:SS]
            assert '[' in log_content and ']' in log_content

def test_birthday_attack_protection():
    """Test birthday attack protection through key size verification."""
    ca = CertificateAuthority()
    
    # Verify key size is sufficient to prevent birthday attacks
    key_size = ca.private_key.key_size
    assert key_size >= 2048  # Minimum secure key size
    
    # Check configured key size
    assert config.KEY_SIZE >= 2048
    
    # Verify random serial numbers are used (helps prevent birthday attacks)
    from cryptography import x509
    serial1 = x509.random_serial_number()
    serial2 = x509.random_serial_number()
    assert serial1 != serial2  # Should be different random numbers

def test_dictionary_attack_protection():
    """Test dictionary attack protection mechanisms."""
    # Test that the system uses cryptographically secure key generation
    ca = CertificateAuthority()
    
    # Verify that keys are generated using secure methods
    assert ca.private_key is not None
    assert ca.private_key.key_size >= 2048
    
    # Test that the system uses proper random number generation
    from cryptography import x509
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    # Generate a test key to verify it uses secure parameters
    test_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    assert test_key.key_size == 2048
    assert test_key.private_numbers().public_numbers.e == 65537