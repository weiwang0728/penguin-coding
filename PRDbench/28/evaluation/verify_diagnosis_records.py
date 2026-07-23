#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VerifydiagnosisRecordDatadatabase connect  and Content
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal, DATABASE_URL
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService

def verify_database_records():
 """VerifyDatadatabasediagnosisRecord"""
 print(f"DatadatabaseURL: {DATABASE_URL}")
 print(f"currentWorkDirectory: {os.getcwd()}")
 
 # CheckDatadatabasefilewhetherexist in 
 db_paths_to_check = [
 "src/data/sme_financing.db",
 "data/sme_financing.db", 
 "../src/data/sme_financing.db"
 ]
 
 for path in db_paths_to_check:
 if os.path.exists(path):
 print(f"find/found to Datadatabasefile: {path} ( large  small : {os.path.getsize(path)} bytes)")
 
 try:
 db = SessionLocal()
 company_service = CompanyService()
 diagnosis_service = DiagnosisService()
 
 # Checkcompany
 companies = company_service.get_all_companies(db)
 print(f"\nDatadatabasecompanyquantity: {len(companies)}")
 for company in companies:
 print(f" - {company.name} (ID: {company.id})")
 
 # CheckthecompanydiagnosisRecord
 reports = diagnosis_service.get_company_reports(db, company.id)
 print(f" diagnosisRecorddecimal: {len(reports)}")
 
 for i, report in enumerate(reports, 1):
 create_time = report.created_at.strftime('%Y-%m-%d %H:%M:%S')
 print(f" {i}. {create_time} - score: {report.overall_score:.1f}")
 
 db.close()
 return True
 
 except Exception as e:
 print(f"VerifyDatadatabaseRecordFailure: {e}")
 return False

if __name__ == "__main__":
 verify_database_records()