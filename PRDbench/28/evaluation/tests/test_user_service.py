# -*- coding: utf-8 -*-
"""
UserServiceunitTest
"""

import pytest
import sys
import os
import hashlib

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.user_service import UserService


class TestUserService:
 """UserServiceTestclass"""
 
 def setup_method(self):
 """Setup before test"""
 self.user_service = UserService()
 
 def test_hash_password_consistency(self):
 """Test password hash consistency"""
 password = "test123456"
 hash1 = self.user_service.hash_password(password)
 hash2 = self.user_service.hash_password(password)

 # Same password should produce same hash
 assert hash1 == hash2
 assert len(hash1) == 64 # SHA256 produces 64 character hexadecimal string

 def test_hash_password_different_inputs(self):
 """Test different passwords produce different hashes"""
 password1 = "password123"
 password2 = "password456"

 hash1 = self.user_service.hash_password(password1)
 hash2 = self.user_service.hash_password(password2)

 # Different passwords should produce different hashes
 assert hash1 != hash2

 def test_hash_password_empty_string(self):
 """Test empty string password hash"""
 empty_password = ""
 hash_result = self.user_service.hash_password(empty_password)

 # Empty string should also be able to hash normally
 assert len(hash_result) == 64
 assert isinstance(hash_result, str)

 def test_hash_password_special_characters(self):
 """Test password with special characters hash"""
 special_password = "p@ssw0rd!@#$%^&*()"
 hash_result = self.user_service.hash_password(special_password)

 # Password with special characters should be able to hash normally
 assert len(hash_result) == 64
 assert isinstance(hash_result, str)

 def test_hash_password_chinese_characters(self):
 """Test password with Chinese characters hash"""
 chinese_password = "password123Chinese"
 hash_result = self.user_service.hash_password(chinese_password)

 # Chinese password should be able to hash normally
 assert len(hash_result) == 64
 assert isinstance(hash_result, str)

 def test_hash_password_long_string(self):
 """Test long password string hash"""
 long_password = "a" * 1000 # 1000 character password
 hash_result = self.user_service.hash_password(long_password)

 # Long password should be able to hash normally
 assert len(hash_result) == 64
 assert isinstance(hash_result, str)

 def test_hash_password_correctness(self):
 """Test password hash correctness"""
 password = "test123"
 expected_hash = hashlib.sha256(password.encode()).hexdigest()
 actual_hash = self.user_service.hash_password(password)

 # Hash result should be consistent with expected
 assert actual_hash == expected_hash

 def test_hash_password_case_sensitivity(self):
 """Test password hash case sensitivity"""
 password_lower = "password"
 password_upper = "PASSWORD"
 password_mixed = "Password"

 hash_lower = self.user_service.hash_password(password_lower)
 hash_upper = self.user_service.hash_password(password_upper)
 hash_mixed = self.user_service.hash_password(password_mixed)

 # Different cases should produce different hashes
 assert hash_lower != hash_upper
 assert hash_lower != hash_mixed
 assert hash_upper != hash_mixed

 def test_hash_password_numeric_strings(self):
 """Test pure numeric password hash"""
 numeric_passwords = ["123456", "0000", "999999999"]

 for password in numeric_passwords:
 hash_result = self.user_service.hash_password(password)
 assert len(hash_result) == 64
 assert isinstance(hash_result, str)

 # Verify each numeric password produces different hash
 for other_password in numeric_passwords:
 if password != other_password:
 other_hash = self.user_service.hash_password(other_password)
 assert hash_result != other_hash

 def test_hash_password_whitespace_handling(self):
 """Test password with whitespace characters processing"""
 password_with_spaces = "pass word"
 password_with_tabs = "pass\tword"
 password_with_newlines = "pass\nword"

 hash_spaces = self.user_service.hash_password(password_with_spaces)
 hash_tabs = self.user_service.hash_password(password_with_tabs)
 hash_newlines = self.user_service.hash_password(password_with_newlines)

 # Different whitespace characters should produce different hashes
 assert hash_spaces != hash_tabs
 assert hash_spaces != hash_newlines
 assert hash_tabs != hash_newlines

 # All hashes should be valid
 assert len(hash_spaces) == 64
 assert len(hash_tabs) == 64
 assert len(hash_newlines) == 64


if __name__ == "__main__":
 pytest.main([__file__])