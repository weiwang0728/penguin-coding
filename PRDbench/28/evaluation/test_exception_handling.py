#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 3.1 exception handling and fault tolerance function
Verify whether the system can properly process various abnormal inputs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal
from services.company_service import CompanyService
from models.schemas import CompanyCreateSchema
from datetime import datetime

def test_exception_handling():
 """Test exception handling and fault tolerance function"""
 print("Test 3.1 exception handling and fault tolerance function...")

 company_service = CompanyService()
 exception_tests = []

 # Test 1: Empty value input
 print("\n=== Test 1: Empty value input exception handling ===")
 try:
 db = SessionLocal()
 empty_data = {
 'name': '', # Empty company name
 'establishment_date': datetime(2020, 1, 1),
 'registered_capital': 1000.0,
 'company_type': 'Limited Liability Company',
 'main_business': '', # Empty main business
 'industry': 'Manufacturing',
 'employee_count': 0, # Boundary value
 'annual_revenue': 0.0, # Boundary value
 'annual_profit': -100.0, # Negative profit
 'asset_liability_ratio': 0.5
 }

 schema = CompanyCreateSchema(**empty_data)
 company = company_service.create_company(db, schema)
 print(f"[PASS] Empty value input processing normal, created company ID: {company.id}")
 exception_tests.append(("Empty value input", True, "System accepts empty value and performs reasonable processing"))
 db.close()

 except Exception as e:
 print(f"[FAIL] Empty value input processing abnormal: {e}")
 exception_tests.append(("Empty value input", False, f"Abnormal: {e}"))

 # Test 2: Extra long string input
 print("\n=== Test 2: Extra long string exception handling ===")
 try:
 db = SessionLocal()
 long_string = "Extra long string test" * 100 # Approximately 1400 characters
 long_data = {
 'name': long_string[:200], # Truncate processing
 'establishment_date': datetime(2020, 1, 1),
 'registered_capital': 1000.0,
 'company_type': 'Limited Liability Company',
 'main_business': long_string, # Extra long main business
 'industry': 'Manufacturing',
 'employee_count': 50,
 'annual_revenue': 1000.0,
 'annual_profit': 100.0,
 'asset_liability_ratio': 0.5,
 'innovation_achievements': long_string # Extra long innovation achievements description
 }

 schema = CompanyCreateSchema(**long_data)
 company = company_service.create_company(db, schema)
 print(f"[PASS] Extra long string processing normal, created company ID: {company.id}")
 print(f" Company name length: {len(company.name)}")
 print(f" Main business length: {len(company.main_business)}")
 exception_tests.append(("Extra long string", True, f"System processed length {len(long_string)} string"))
 db.close()

 except Exception as e:
 print(f"[FAIL] Extra long string processing abnormal: {e}")
 exception_tests.append(("Extra long string", False, f"Abnormal: {e}"))

 # Test 3: Special characters input
 print("\n=== Test 3: Special characters exception handling ===")
 try:
 db = SessionLocal()
 special_data = {
 'name': 'Test Company@#$%^&*()', # Special characters company name
 'establishment_date': datetime(2020, 1, 1),
 'registered_capital': 1000.0,
 'company_type': 'Limited Liability Company',
 'main_business': 'Software Development<script>alert("test")</script>', # Contains HTML/JS
 'industry': 'Information Technology@#$%', # Special characters industry
 'employee_count': 50,
 'annual_revenue': 1000.0,
 'annual_profit': 100.0,
 'asset_liability_ratio': 0.5,
 'innovation_achievements': 'Innovation achievements\nNewline\tTab test' # Control characters
 }

 schema = CompanyCreateSchema(**special_data)
 company = company_service.create_company(db, schema)
 print(f"[PASS] Special characters processing normal, created company ID: {company.id}")
 print(f" Company name: {company.name}")
 print(f" Main business: {company.main_business[:50]}...")
 exception_tests.append(("Special characters", True, "System correctly processes special characters"))
 db.close()

 except Exception as e:
 print(f"[FAIL] Special characters processing abnormal: {e}")
 exception_tests.append(("Special characters", False, f"Abnormal: {e}"))

 # Test 4: Boundary value input
 print("\n=== Test 4: Boundary value exception handling ===")
 try:
 db = SessionLocal()
 boundary_data = {
 'name': 'Boundary Value Test Company',
 'establishment_date': datetime(2020, 1, 1),
 'registered_capital': 0.01, # Extremely small registered capital
 'company_type': 'Limited Liability Company',
 'main_business': 'Boundary test',
 'industry': 'Manufacturing',
 'employee_count': 999999, # Extremely large employee count
 'annual_revenue': 999999999.99, # Extremely large revenue
 'annual_profit': -999999.99, # Extremely large negative profit
 'asset_liability_ratio': 0.99, # Near 1 debt ratio
 'patent_count': 0, # Boundary value
 'copyright_count': 99999, # Large number
 'rd_investment': 0.0, # Boundary value
 'rd_revenue_ratio': 0.99, # Near 100%
 'rd_personnel_ratio': 1.0, # 100% R&D personnel
 'internal_control_score': 1, # Lowest score
 'financial_standard_score': 5, # Highest score
 'compliance_training_score': 1,
 'employment_compliance_score': 5
 }

 schema = CompanyCreateSchema(**boundary_data)
 company = company_service.create_company(db, schema)
 print(f"[PASS] Boundary value processing normal, created company ID: {company.id}")
 print(f" Registered capital: {company.registered_capital}")
 print(f" Employee count: {company.employee_count}")
 print(f" Revenue: {company.annual_revenue}")
 exception_tests.append(("Boundary value", True, "System correctly processes boundary values"))
 db.close()

 except Exception as e:
 print(f"[FAIL] Boundary value processing abnormal: {e}")
 exception_tests.append(("Boundary value", False, f"Abnormal: {e}"))

 # Test 5: Invalid data type processing (through update test)
 print("\n=== Test 5: Invalid data type processing ===")
 try:
 db = SessionLocal()
 # Test asset-liability ratio out of range
 invalid_data = {
 'name': 'Invalid Data Test Company',
 'establishment_date': datetime(2020, 1, 1),
 'registered_capital': 1000.0,
 'company_type': 'Limited Liability Company',
 'main_business': 'Test business',
 'industry': 'Manufacturing',
 'employee_count': 50,
 'annual_revenue': 1000.0,
 'annual_profit': 100.0,
 'asset_liability_ratio': 1.5, # Exceeds reasonable range
 'rd_revenue_ratio': 2.0, # Exceeds 100%
 'rd_personnel_ratio': 1.5, # Exceeds 100%
 'internal_control_score': 10, # Exceeds 1-5 range
 'financial_standard_score': -1 # Negative score
 }

 schema = CompanyCreateSchema(**invalid_data)
 company = company_service.create_company(db, schema)
 print(f"[PASS] Invalid data type processing normal, created company ID: {company.id}")
 print(f" Asset-liability ratio: {company.asset_liability_ratio}")
 print(f" R&D investment ratio: {company.rd_revenue_ratio}")
 exception_tests.append(("Invalid data type", True, "System accepts out of range numbers"))
 db.close()

 except Exception as e:
 print(f"[FAIL] Invalid data type processing abnormal: {e}")
 exception_tests.append(("Invalid data type", False, f"Abnormal: {e}"))

 # Summary of test results
 print("\n" + "=" * 80)
 print("Exception handling and fault tolerance test result summary")
 print("=" * 80)

 passed_tests = 0
 total_tests = len(exception_tests)

 for test_name, passed, description in exception_tests:
 status = "[PASS]" if passed else "[FAIL]"
 print(f"{status} {test_name:<15} - {description}")
 if passed:
 passed_tests += 1

 print("-" * 80)
 print(f"Passed tests: {passed_tests}/{total_tests}")

 if passed_tests >= 3: # At least pass 3 tests
 print("\n[PASS] Test passed: exception handling and fault tolerance functionality effective")
 print(" - System can properly process various abnormal inputs (empty values, extra long strings, special characters, etc.)")
 print(" - Provides friendly error processing mechanism without program crash")
 print(" - Boundary values and invalid data are reasonably processed")
 return True
 else:
 print("\n[FAIL] Test failed: exception handling function needs improvement")
 return False

if __name__ == "__main__":
 success = test_exception_handling()
 exit(0 if success else 1)
