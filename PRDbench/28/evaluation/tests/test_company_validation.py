# -*- coding: utf-8 -*-
"""
Company Data Validation Unit Test
"""

import pytest
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from services.company_service import CompanyService


class TestCompanyValidation:
 """CompanyDataValidationTest class"""
 
 def setup_method(self):
 """Setup before test"""
 self.company_service = CompanyService()
 
 # Basic valid data
 self.valid_data = {
 'name': 'Test Company',
 'establishment_date': '2020-01-01',
 'registered_capital': 100,
 'company_type': 'Limited Liability Company',
 'main_business': 'Software Development', 
 'industry': 'Software and Information Technology Services',
 'employee_count': 50,
 'annual_revenue': 1000,
 'annual_profit': 100,
 'asset_liability_ratio': 0.6,
 'internal_control_score': 4,
 'financial_standard_score': 4,
 'compliance_training_score': 3,
 'employment_compliance_score': 4
 }
 
 def test_valid_numeric_fields(self):
 """Test valid number field validation"""
 is_valid, message = self.company_service.validate_company_data(self.valid_data)
 assert is_valid == True
 assert message == "Validation passed"

 def test_negative_registered_capital(self):
 """Test registered capital as negative number"""
 invalid_data = self.valid_data.copy()
 invalid_data['registered_capital'] = -100
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "registered_capital cannot be negative number" in message

 def test_negative_employee_count(self):
 """Test employee quantity as negative number"""
 invalid_data = self.valid_data.copy()
 invalid_data['employee_count'] = -5
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "employee_count cannot be negative number" in message

 def test_negative_annual_revenue(self):
 """Test annual revenue as negative number"""
 invalid_data = self.valid_data.copy()
 invalid_data['annual_revenue'] = -1000
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "annual_revenue cannot be negative number" in message

 def test_negative_annual_profit(self):
 """Test annual profit as negative number"""
 invalid_data = self.valid_data.copy()
 invalid_data['annual_profit'] = -100
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "annual_profit cannot be negative number" in message

 def test_invalid_ratio_field_above_one(self):
 """Test asset-liability ratio greater than 1"""
 invalid_data = self.valid_data.copy()
 invalid_data['asset_liability_ratio'] = 1.5
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "asset_liability_ratio must be between 0-1" in message

 def test_invalid_ratio_field_below_zero(self):
 """Test asset-liability ratio less than 0"""
 invalid_data = self.valid_data.copy()
 invalid_data['asset_liability_ratio'] = -0.1
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "asset_liability_ratio must be between 0-1" in message

 def test_invalid_score_field_above_five(self):
 """Test score field greater than 5"""
 invalid_data = self.valid_data.copy()
 invalid_data['internal_control_score'] = 6
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "internal_control_score must be between 1-5" in message

 def test_invalid_score_field_below_one(self):
 """Test score field less than 1"""
 invalid_data = self.valid_data.copy()
 invalid_data['financial_standard_score'] = 0
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "financial_standard_score must be between 1-5" in message

 def test_missing_required_field(self):
 """Test missing required field"""
 invalid_data = self.valid_data.copy()
 del invalid_data['name']
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "Required field name cannot be empty" in message

 def test_empty_string_field(self):
 """Test empty string field"""
 invalid_data = self.valid_data.copy()
 invalid_data['name'] = ' '
 is_valid, message = self.company_service.validate_company_data(invalid_data)
 assert is_valid == False
 assert "Field name cannot be empty string" in message


if __name__ == "__main__":
 pytest.main([__file__])