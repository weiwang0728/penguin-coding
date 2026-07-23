#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare comparison test data for existing company
Through real business process to produce diagnosis records for different periods
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService

def prepare_comparison_data_for_existing_company():
    """Prepare comparison data for existing Innovation Technology Company"""
    print("Preparing comparison test data for existing company...")

    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()

    try:
        db = SessionLocal()

        # Get existing company
        company = company_service.get_company_by_name(db, "Innovation Technology Company")
        if not company:
            print("[FAIL] Could not find Innovation Technology Company")
            return False

        print(f"Found company: {company.name}")
        print(f"Current status - Employees: {company.employee_count}, Revenue: {company.annual_revenue} thousand yuan, Patents: {company.patent_count} item(s)")

        # Simulate company development process, first "revert back" to early status, then gradually develop

        # Step 1: Simulate early status (reduce various indicators)
        print("\n=== Simulating company early development status ===")
        early_stage_data = {
            'employee_count': 30, # Early stage fewer employees
            'annual_revenue': 800.0, # Early stage low revenue
            'annual_profit': 100.0, # Early stage less profit
            'asset_liability_ratio': 0.6, # Early stage higher debt ratio
            'patent_count': 2, # Early stage fewer patents
            'copyright_count': 1, # Early stage fewer copyrights
            'rd_investment': 120.0, # Early stage less R&D investment
            'rd_revenue_ratio': 0.15, # Early stage R&D investment ratio
            'rd_personnel_ratio': 0.25, # Early stage R&D personnel ratio
            'innovation_achievements': 'Developed preliminary software products',
            'internal_control_score': 3, # Early stage management standardization average
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 3
        }

        company_service.update_company(db, company.id, early_stage_data)
        updated_company = company_service.get_company_by_name(db, "Innovation Technology Company")

        # Perform diagnosis for early status
        diagnosis_early = diagnosis_service.diagnose_company(db, updated_company)
        report_early = report_service.generate_full_report(updated_company, diagnosis_early)
        print(f"Early status diagnosis complete, overall score: {diagnosis_early.overall_score:.1f}")

        time.sleep(2) # Ensure timestamp different

        # Step 2: Simulate mid-stage development status
        print("\n=== Simulating company mid-stage development status ===")
        mid_stage_data = {
            'employee_count': 55, # Mid-stage employee growth
            'annual_revenue': 1400.0, # Mid-stage revenue growth
            'annual_profit': 210.0, # Mid-stage profit improvement
            'asset_liability_ratio': 0.45, # Mid-stage debt ratio improved
            'patent_count': 5, # Mid-stage patent increase
            'copyright_count': 3, # Mid-stage copyright increase
            'rd_investment': 250.0, # Mid-stage R&D investment increase
            'rd_revenue_ratio': 0.18, # Mid-stage R&D investment ratio improved
            'rd_personnel_ratio': 0.32, # Mid-stage R&D personnel ratio improved
            'innovation_achievements': 'Developed multiple market-recognized innovative products',
            'internal_control_score': 4, # Mid-stage management standardization improved
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 4
        }

        company_service.update_company(db, company.id, mid_stage_data)
        updated_company = company_service.get_company_by_name(db, "Innovation Technology Company")

        # Perform diagnosis for mid-stage status
        diagnosis_mid = diagnosis_service.diagnose_company(db, updated_company)
        report_mid = report_service.generate_full_report(updated_company, diagnosis_mid)
        print(f"Mid-stage status diagnosis complete, overall score: {diagnosis_mid.overall_score:.1f}")

        time.sleep(2)

        # Step 3: Restore to current best status
        print("\n=== Restoring to current best status ===")
        current_best_data = {
            'employee_count': 80, # Current employee level
            'annual_revenue': 2000.0, # Current revenue level
            'annual_profit': 400.0, # Current profit level
            'asset_liability_ratio': 0.3, # Current debt ratio
            'patent_count': 8, # Current number of patents
            'copyright_count': 5, # Current number of copyrights
            'rd_investment': 400.0, # Current R&D investment
            'rd_revenue_ratio': 0.2, # Current R&D investment ratio
            'rd_personnel_ratio': 0.4, # Current R&D personnel ratio
            'innovation_achievements': 'Developed industry-leading innovative products, have core technical advantages',
            'internal_control_score': 4, # Current internal control level
            'financial_standard_score': 4, # Current financial regulation level
            'compliance_training_score': 4, # Current compliance level
            'employment_compliance_score': 4 # Current employment compliance level
        }

        company_service.update_company(db, company.id, current_best_data)
        updated_company = company_service.get_company_by_name(db, "Innovation Technology Company")

        # Perform diagnosis for current status
        diagnosis_current = diagnosis_service.diagnose_company(db, updated_company)
        report_current = report_service.generate_full_report(updated_company, diagnosis_current)
        print(f"Current status diagnosis complete, overall score: {diagnosis_current.overall_score:.1f}")

        print(f"\n[PASS] Successfully prepared comparison data for Innovation Technology Company")
        print(f"Development trajectory: Early ({diagnosis_early.overall_score:.1f}) → Mid ({diagnosis_mid.overall_score:.1f}) → Current ({diagnosis_current.overall_score:.1f})")

        db.close()
        return True

    except Exception as e:
        print(f"[FAIL] Preparing comparison data failed: {e}")
        return False

if __name__ == "__main__":
    success = prepare_comparison_data_for_existing_company()
    if success:
        print("\nComparison data preparation complete, now can test 2.3.5b Report Comparison function")
    else:
        print("\nComparison data preparation failed")
    exit(0 if success else 1)