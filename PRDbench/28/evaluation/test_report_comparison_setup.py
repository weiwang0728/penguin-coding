#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare test data for 2.3.5b report comparison function
Ensure sufficient historical reports to perform comparison test
"""

import sys
import os
import time
from datetime import datetime, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch
from io import StringIO
from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService
from models.schemas import CompanyCreateSchema

def setup_test_company_and_reports():
 """Set up test company and generate multiple historical reports"""
 print("Preparing test data for 2.3.5b report comparison function...")

 db = SessionLocal()
 company_service = CompanyService()
 diagnosis_service = DiagnosisService()
 report_service = ReportService()

 try:
 # Prepare company basic data
 company_name = "Innovation Technology Company"

 # Delete existing company with same name if exists
 existing = company_service.get_company_by_name(db, company_name)
 if existing:
 company_service.delete_company(db, existing.id)
 print(f"Deleted existing company: {company_name}")

 # Create first version of company information
 company_data_v1 = {
 'name': company_name,
 'establishment_date': datetime(2020, 1, 15),
 'registered_capital': 1000.0,
 'company_type': 'Limited Liability Company',
 'main_business': 'Software Development and Technical Services',
 'industry': 'Information transmission, Software and Information Technology Services',
 'employee_count': 80,
 'annual_revenue': 2000.0,
 'annual_profit': 300.0,
 'asset_liability_ratio': 0.4,
 'patent_count': 3,
 'copyright_count': 2,
 'rd_investment': 200.0,
 'rd_revenue_ratio': 0.1,
 'rd_personnel_ratio': 0.3,
 'innovation_achievements': 'Developed multiple innovative software products',
 'internal_control_score': 3,
 'financial_standard_score': 3,
 'compliance_training_score': 3,
 'employment_compliance_score': 3
 }

 # Create first company version
 schema_v1 = CompanyCreateSchema(**company_data_v1)
 company_v1 = company_service.create_company(db, schema_v1)
 print(f"Created first version of company information: {company_v1.name} (ID: {company_v1.id})")

 # Generate first diagnosis report
 diagnosis_result_v1 = diagnosis_service.diagnose_company(db, company_v1)
 report_v1 = report_service.generate_full_report(company_v1, diagnosis_result_v1)
 print(f"Generated first report: {report_v1}")

 # Wait one second to ensure different timestamps
 time.sleep(1)

 # Update company information (improve various indicators)
 update_data_v2 = {
 'annual_revenue': 3000.0, # Revenue increase
 'annual_profit': 500.0, # Profit increase
 'asset_liability_ratio': 0.3, # Debt ratio decrease
 'patent_count': 8, # Patent increase
 'copyright_count': 5, # Copyright increase
 'rd_investment': 400.0, # R&D investment increase
 'rd_personnel_ratio': 0.4, # R&D personnel ratio improvement
 'internal_control_score': 4, # Internal control score improvement
 'financial_standard_score': 4, # Financial standard improvement
 'compliance_training_score': 4, # Compliance training improvement
 'employment_compliance_score': 4 # Employment compliance improvement
 }

 # Recalculate R&D investment to revenue ratio
 update_data_v2['rd_revenue_ratio'] = update_data_v2['rd_investment'] / update_data_v2['annual_revenue']

 # Update company information
 company_v2 = company_service.update_company(db, company_v1.id, update_data_v2)
 print(f"Updated company information: {company_v2.name}")

 # Generate second diagnosis report
 diagnosis_result_v2 = diagnosis_service.diagnose_company(db, company_v2)
 report_v2 = report_service.generate_full_report(company_v2, diagnosis_result_v2)
 print(f"Generated second report: {report_v2}")

 # Wait one second
 time.sleep(1)

 # Update company information again (further improvement)
 update_data_v3 = {
 'annual_revenue': 4500.0, # Revenue further increase
 'annual_profit': 800.0, # Profit large increase
 'asset_liability_ratio': 0.25, # Debt ratio further decrease
 'patent_count': 12, # Patent large increase
 'copyright_count': 8, # Copyright increase
 'rd_investment': 600.0, # R&D investment increase
 'rd_personnel_ratio': 0.45, # R&D personnel ratio further improvement
 'internal_control_score': 5, # Internal control score reaches excellent
 'financial_standard_score': 5, # Financial standard reaches excellent
 'compliance_training_score': 5, # Compliance training reaches excellent
 'employment_compliance_score': 5 # Employment compliance reaches excellent
 }

 # Recalculate R&D investment to revenue ratio
 update_data_v3['rd_revenue_ratio'] = update_data_v3['rd_investment'] / update_data_v3['annual_revenue']

 # Update company information again
 company_v3 = company_service.update_company(db, company_v2.id, update_data_v3)
 print(f"Updated company information again: {company_v3.name}")

 # Generate third diagnosis report
 diagnosis_result_v3 = diagnosis_service.diagnose_company(db, company_v3)
 report_v3 = report_service.generate_full_report(company_v3, diagnosis_result_v3)
 print(f"Generated third report: {report_v3}")

 print(f"\nSuccessfully generated 3 historical reports for company '{company_name}'")
 print("Now you can execute 2.3.5a and 2.3.5b test points")

 return True

 except Exception as e:
 print(f"Test data preparation failure: {e}")
 return False
 finally:
 db.close()

def test_report_list():
 """Test report list function"""
 print("\nTest 2.3.5a historical reports management - report archiving...")

 # Here you can call actual report list command
 import subprocess
 try:
 result = subprocess.run(
 ['python', 'main.py', 'report', 'list'],
 cwd='../src',
 capture_output=True,
 text=True,
 encoding='utf-8'
 )

 print("Report list output:")
 print(result.stdout)

 if "Innovation Technology Company" in result.stdout and "Report file" in result.stdout:
 print("Test passed: historical reports archiving functionality normal")
 return True
 else:
 print("Test failed: did not find expected report list content")
 return False

 except Exception as e:
 print(f"Test report list failure: {e}")
 return False

def test_report_comparison():
 """Test report comparison function"""
 print("\nTest 2.3.5b historical reports management - report comparison...")

 # Here you can call actual report comparison command
 import subprocess
 try:
 result = subprocess.run(
 ['python', 'main.py', 'diagnosis', 'compare', '--name', 'Innovation Technology Company'],
 cwd='../src',
 capture_output=True,
 text=True,
 encoding='utf-8'
 )

 print("Report comparison output:")
 print(result.stdout)

 if "comparison" in result.stdout and "change" in result.stdout:
 print("Test passed: report comparison functionality effective")
 return True
 else:
 print("Test failed: did not find expected comparison result")
 return False

 except Exception as e:
 print(f"Test report comparison failure: {e}")
 return False

if __name__ == "__main__":
 # Prepare test data
 if setup_test_company_and_reports():
 # Test report archiving
 test_report_list()

 # Test report comparison
 test_report_comparison()
 else:
 print("Test data preparation failure, cannot execute subsequent tests")