#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 set TestData
"""

import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import SessionLocal, init_database
from services.company_service import CompanyService
from models.schemas import CompanyCreateSchema

def setup_test_companies():
 """CreateTest CompanyData"""
 # initializeDatadatabase
 init_database()
 
 db = SessionLocal()
 company_service = CompanyService()
 
 try:
 # Checkcompanywhether already exist in 
 existing_company = company_service.get_company_by_name(db, "Innovation Technology Company")
 if existing_company:
 print("Test Company'Innovation Technology Company' already exist in ")
 return existing_company
 
 # CreateTest CompanyData
 test_company_data = {
 'name': 'Innovation Technology Company',
 'establishment_date': datetime.strptime('2020-06-15', '%Y-%m-%d').date(),
 'registered_capital': 500.0,
 'company_type': 'Limited Liability Company',
 'main_business': 'Software Development and Technical Services',
 'industry': 'Software and Information Technology Services',
 'employee_count': 80,
 'annual_revenue': 2000.0,
 'annual_profit': 300.0,
 'asset_liability_ratio': 0.45,
 'patent_count': 8,
 'copyright_count': 12,
 'rd_investment': 300.0,
 'rd_revenue_ratio': 0.15,
 'rd_personnel_ratio': 0.25,
 'innovation_achievements': 'Obtained many item(s)Softwarecopyright and Technicalpatent',
 'internal_control_score': 4,
 'financial_standard_score': 4,
 'compliance_training_score': 3,
 'employment_compliance_score': 4,
 'last_financing_date': None,
 'last_financing_amount': None,
 'last_financing_channel': None
 }
 
 # CreateCompanyCreateSchema for Object
 company_schema = CompanyCreateSchema(**test_company_data)
 
 # Createcompany
 company = company_service.create_company(db, company_schema)
 print(f"SuccessCreateTest Company: {company.name}")
 
 return company
 
 except Exception as e:
 print(f"CreateTest CompanyFailure: {e}")
 db.rollback()
 return None
 finally:
 db.close()

def setup_test_diagnosis(company):
 """ as Test CompanyCreatediagnosisRecord"""
 if not company:
 print("company not exist in ， no MethodCreatediagnosisRecord")
 return None
 
 db = SessionLocal()
 
 try:
 from services.diagnosis_service import DiagnosisService
 diagnosis_service = DiagnosisService()
 
 # Executediagnosis
 diagnosis_result = diagnosis_service.diagnose_company(db, company)
 print(f"Success as company'{company.name}'CreatediagnosisRecord")
 
 return diagnosis_result
 
 except Exception as e:
 print(f"CreatediagnosisRecordFailure: {e}")
 db.rollback()
 return None
 finally:
 db.close()

def main():
 """Mainfunction"""
 print("start set TestData...")
 
 # CreateTest Company
 company = setup_test_companies()
 
 # CreatediagnosisRecord
 if company:
 diagnosis_result = setup_test_diagnosis(company)
 if diagnosis_result:
 print("TestData set complete！")
 return True
 
 print("TestData set Failure")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)