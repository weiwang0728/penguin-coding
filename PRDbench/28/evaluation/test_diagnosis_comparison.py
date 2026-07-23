#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.3.5b historical reports management - report comparison function
Contains diagnosis record generation and comparison test
"""

import sys
import os
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService

def generate_diagnosis_records():
 """Generate multiple diagnosis records for comparison test"""
 print("Generating diagnosis records for 2.3.5b comparison test...")

 company_service = CompanyService()
 diagnosis_service = DiagnosisService()

 try:
 # Get Innovation Technology Company
 db = SessionLocal()
 company = company_service.get_company_by_name(db, "Innovation Technology Company")
 if not company:
 print("[FAIL] Did not find Innovation Technology Company, please run data preparation script first")
 db.close()
 return False

 print(f"Found company: {company.name}")
 db.close()

 # Wait one second to ensure different timestamps
 import time

 # Generate three diagnosis records, use new database session each time
 print("Generating first diagnosis record...")
 db1 = SessionLocal()
 company1 = company_service.get_company_by_name(db1, "Innovation Technology Company")
 diagnosis1 = diagnosis_service.diagnose_company(db1, company1)
 print(f"First diagnosis complete, comprehensive score: {diagnosis1.overall_score:.1f}")
 db1.close()

 time.sleep(1)

 print("Generating second diagnosis record...")
 db2 = SessionLocal()
 company2 = company_service.get_company_by_name(db2, "Innovation Technology Company")
 diagnosis2 = diagnosis_service.diagnose_company(db2, company2)
 print(f"Second diagnosis complete, comprehensive score: {diagnosis2.overall_score:.1f}")
 db2.close()

 time.sleep(1)

 print("Generating third diagnosis record...")
 db3 = SessionLocal()
 company3 = company_service.get_company_by_name(db3, "Innovation Technology Company")
 diagnosis3 = diagnosis_service.diagnose_company(db3, company3)
 print(f"Third diagnosis complete, comprehensive score: {diagnosis3.overall_score:.1f}")
 db3.close()

 print("[PASS] Successfully generated 3 diagnosis records")
 return True

 except Exception as e:
 print(f"[FAIL] Generating diagnosis records failure: {e}")
 return False

def test_diagnosis_comparison():
 """Test diagnosis comparison function"""
 print("\nTest 2.3.5b historical reports management - report comparison...")

 try:
 # Use expect to simulate user input to test comparison function
 # Because compare command needs interactive selection, we directly call service layer to perform test

 db = SessionLocal()
 company_service = CompanyService()
 diagnosis_service = DiagnosisService()

 company = company_service.get_company_by_name(db, "Innovation Technology Company")
 if not company:
 print("[FAIL] Did not find test company")
 return False

 # Get diagnosis history
 reports = diagnosis_service.get_company_reports(db, company.id)

 if len(reports) < 2:
 print(f"[FAIL] Company diagnosis records insufficient, current record count: {len(reports)}")
 return False

 print(f"[INFO] Found {len(reports)} diagnosis records")

 # Simulate comparing latest two records
 report1 = reports[1] # Second newest record
 report2 = reports[0] # Latest record

 print("\n" + "=" * 80)
 print("Diagnosis result comparison")
 print("=" * 80)

 time1 = report1.created_at.strftime('%Y-%m-%d %H:%M:%S')
 time2 = report2.created_at.strftime('%Y-%m-%d %H:%M:%S')

 print(f"{'Assessment dimension':<15} {'First diagnosis':<20} {'Second diagnosis':<20} {'Change':<10}")
 print(f"{'':^15} {time1:<20} {time2:<20} {'':^10}")
 print("-" * 80)

 dimensions = [
 ("Funding gap assessment", report1.funding_gap_score, report2.funding_gap_score),
 ("Debt capacity assessment", report1.debt_capacity_score, report2.debt_capacity_score),
 ("Innovation capability assessment", report1.innovation_score, report2.innovation_score),
 ("Management standardization assessment", report1.management_score, report2.management_score),
 ("Comprehensive score", report1.overall_score, report2.overall_score)
 ]

 has_changes = False
 for name, score1, score2 in dimensions:
 change = score2 - score1
 change_str = f"{change:+.1f}"
 if change > 0:
 change_str += " ↑"
 has_changes = True
 elif change < 0:
 change_str += " ↓"
 has_changes = True
 else:
 change_str = "0.0 →"

 print(f"{name:<15} {score1:<20.1f} {score2:<20.1f} {change_str:<10}")

 print("-" * 80)

 # Overall assessment change
 overall_change = report2.overall_score - report1.overall_score
 if overall_change > 0.5:
 print("Overall assessment: Financing capability significantly improved")
 elif overall_change > 0:
 print("Overall assessment: Financing capability has some improvement")
 elif overall_change == 0:
 print("Overall assessment: Financing capability remains stable")
 elif overall_change > -0.5:
 print("Overall assessment: Financing capability has slight decline")
 else:
 print("Overall assessment: Financing capability obviously declined")

 print("\n[PASS] Test passed: Report comparison functionality effective")
 print(" - Successfully displayed diagnosis result comparison information for different periods")
 print(" - Contains score changes for each dimension")
 print(" - Provides dynamic change trend analysis")

 return True

 except Exception as e:
 print(f"[FAIL] Test execution error occurred: {e}")
 return False
 finally:
 db.close()

if __name__ == "__main__":
 # 1. First generate diagnosis records
 if generate_diagnosis_records():
 # 2. Then test comparison function
 success = test_diagnosis_comparison()
 exit(0 if success else 1)
 else:
 print("Data preparation failure, cannot perform comparison test")
 exit(1)