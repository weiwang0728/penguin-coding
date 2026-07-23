#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test yearly diagnosis records and 2.3.5b report comparison function
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import SessionLocal
from services.company_service import CompanyService
from services.diagnosis_service import DiagnosisService
from services.report_service import ReportService
from models.schemas import CompanyCreateSchema
from datetime import datetime

def create_yearly_diagnosis_records():
    """Create company diagnosis records for different years"""
    print("Creating company diagnosis records for different years...")

    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()

    try:
        # Create or get test company
        db = SessionLocal()
        company_name = "Annual Development Technology Company"

        # Delete existing company and recreate
        existing = company_service.get_company_by_name(db, company_name)
        if existing:
            company_service.delete_company(db, existing.id)

        # Create company basic information (current status)
        company_data = {
            'name': company_name,
            'establishment_date': datetime(2020, 6, 1),
            'registered_capital': 1000.0,
            'company_type': 'Limited Liability Company',
            'main_business': 'Software Development and Technical Services',
            'industry': 'Information Transmission, Software and Information Technology Services',
            'employee_count': 50, # Current employee count
            'annual_revenue': 1500.0, # Current revenue
            'annual_profit': 200.0, # Current profit
            'asset_liability_ratio': 0.4, # Current asset-liability ratio
            'patent_count': 5, # Current patent count
            'copyright_count': 3, # Current copyright count
            'rd_investment': 300.0, # Current R&D investment
            'rd_revenue_ratio': 0.2, # R&D investment ratio to revenue
            'rd_personnel_ratio': 0.3, # R&D personnel ratio
            'innovation_achievements': 'Developed innovative software products',
            'internal_control_score': 4, # Current internal control score
            'financial_standard_score': 4, # Current financial standardization score
            'compliance_training_score': 3, # Current compliance training score
            'employment_compliance_score': 4 # Current employment compliance score
        }

        schema = CompanyCreateSchema(**company_data)
        company = company_service.create_company(db, schema)
        print(f"Created company: {company.name}")
        db.close()

        # Simulate 2022 year diagnosis (company early development)
        print("\n=== 2022 Year diagnosis ===")
        db_2022 = SessionLocal()
        company_2022 = company_service.get_company_by_name(db_2022, company_name)

        # Update company data to 2022 year status (relatively weak)
        updates_2022 = {
            'employee_count': 25, # Fewer employees
            'annual_revenue': 600.0, # Low revenue
            'annual_profit': 60.0, # Low profit
            'asset_liability_ratio': 0.6, # Higher debt ratio
            'patent_count': 1, # Fewer patents
            'copyright_count': 1, # Fewer copyrights
            'rd_investment': 90.0, # Less R&D investment
            'rd_revenue_ratio': 0.15, # R&D investment ratio
            'internal_control_score': 2, # Low internal control score
            'financial_standard_score': 2, # Low financial regulation
            'compliance_training_score': 2, # Low compliance
            'employment_compliance_score': 2 # Low employment compliance
        }

        company_service.update_company(db_2022, company_2022.id, updates_2022)
        updated_company_2022 = company_service.get_company_by_name(db_2022, company_name)

        diagnosis_2022 = diagnosis_service.diagnose_company(db_2022, updated_company_2022, 2022)
        print(f"2022 year diagnosis complete, overall score: {diagnosis_2022.overall_score:.1f}")
        db_2022.close()

        time.sleep(1)

        # Simulate 2023 year diagnosis (company growth period)
        print("\n=== 2023 Year diagnosis ===")
        db_2023 = SessionLocal()
        company_2023 = company_service.get_company_by_name(db_2023, company_name)

        # Update company data to 2023 year status (some development)
        updates_2023 = {
            'employee_count': 35, # Employee increase
            'annual_revenue': 1000.0, # Revenue growth
            'annual_profit': 130.0, # Profit improvement
            'asset_liability_ratio': 0.5, # Debt ratio improved
            'patent_count': 3, # Patent increase
            'copyright_count': 2, # Copyright increase
            'rd_investment': 180.0, # R&D investment increase
            'rd_revenue_ratio': 0.18, # R&D investment ratio improved
            'internal_control_score': 3, # Internal control score improved
            'financial_standard_score': 3, # Financial regulation improved
            'compliance_training_score': 3, # Compliance improved
            'employment_compliance_score': 3 # Employment compliance improved
        }

        company_service.update_company(db_2023, company_2023.id, updates_2023)
        updated_company_2023 = company_service.get_company_by_name(db_2023, company_name)

        diagnosis_2023 = diagnosis_service.diagnose_company(db_2023, updated_company_2023, 2023)
        print(f"2023 year diagnosis complete, overall score: {diagnosis_2023.overall_score:.1f}")
        db_2023.close()

        time.sleep(1)

        # Simulate 2024 year diagnosis (company maturity period)
        print("\n=== 2024 Year diagnosis ===")
        db_2024 = SessionLocal()
        company_2024 = company_service.get_company_by_name(db_2024, company_name)

        # Update company data to 2024 year status (current best status)
        updates_2024 = {
            'employee_count': 50, # Employees reached current level
            'annual_revenue': 1500.0, # Revenue reached current level
            'annual_profit': 200.0, # Profit reached current level
            'asset_liability_ratio': 0.4, # Debt ratio optimized
            'patent_count': 5, # Patents reached current level
            'copyright_count': 3, # Copyrights reached current level
            'rd_investment': 300.0, # R&D investment reached current level
            'rd_revenue_ratio': 0.2, # R&D investment ratio optimized
            'internal_control_score': 4, # Internal control score reached excellent
            'financial_standard_score': 4, # Financial regulation excellent
            'compliance_training_score': 3, # Compliance good
            'employment_compliance_score': 4 # Employment compliance excellent
        }

        company_service.update_company(db_2024, company_2024.id, updates_2024)
        updated_company_2024 = company_service.get_company_by_name(db_2024, company_name)

        diagnosis_2024 = diagnosis_service.diagnose_company(db_2024, updated_company_2024, 2024)
        print(f"2024 year diagnosis complete, overall score: {diagnosis_2024.overall_score:.1f}")
        db_2024.close()

        print(f"\n[PASS] Successfully created 3 years of diagnosis records")
        print(f"Development trajectory: 2022 year ({diagnosis_2022.overall_score:.1f}) → 2023 year ({diagnosis_2023.overall_score:.1f}) → 2024 year ({diagnosis_2024.overall_score:.1f})")

        return True

    except Exception as e:
        print(f"[FAIL] Creating yearly diagnosis records failed: {e}")
        return False

def test_yearly_comparison():
    """Test yearly comparison analysis"""
    print("\nTesting company yearly development comparison analysis...")

    try:
        db = SessionLocal()
        company_service = CompanyService()
        diagnosis_service = DiagnosisService()

        company = company_service.get_company_by_name(db, "Annual Development Technology Company")
        if not company:
            print("[FAIL] Could not find test company")
            return False

        # Get diagnosis history (sorted by year)
        reports = diagnosis_service.get_company_reports(db, company.id)

        if len(reports) < 2:
            print(f"[FAIL] Insufficient company yearly diagnosis records, current record count: {len(reports)}")
            return False

        print(f"[INFO] Found {len(reports)} items of yearly diagnosis records")

        # Sort by year, find earliest and newest records
        reports_by_year = sorted(reports, key=lambda r: r.report_year)
        earliest_report = reports_by_year[0] # Earliest year
        latest_report = reports_by_year[-1] # Newest year

        print("\n" + "=" * 80)
        print("Company yearly development comparison analysis")
        print("=" * 80)

        print(f"{'Assessment dimension':<15} {f'{earliest_report.report_year} Year':<20} {f'{latest_report.report_year} Year':<20} {'Yearly change':<15}")
        print("-" * 80)

        dimensions = [
            ("Funding gap assessment", earliest_report.funding_gap_score, latest_report.funding_gap_score),
            ("Debt capacity assessment", earliest_report.debt_capacity_score, latest_report.debt_capacity_score),
            ("Innovation capability assessment", earliest_report.innovation_score, latest_report.innovation_score),
            ("Management standardization assessment", earliest_report.management_score, latest_report.management_score),
            ("Overall score", earliest_report.overall_score, latest_report.overall_score)
        ]

        significant_growth = False
        for name, score1, score2 in dimensions:
            change = score2 - score1
            change_str = f"{change:+.1f}"
            if change > 0.5:
                change_str += " Significantly improved"
                significant_growth = True
            elif change > 0.2:
                change_str += " Noticeably improved"
                significant_growth = True
            elif change > 0:
                change_str += " Somewhat improved"
            elif change < -0.2:
                change_str += " Noticeably declined"
            elif change < 0:
                change_str += " Slightly declined"
            else:
                change_str = "0.0 Remained stable"

            print(f"{name:<15} {score1:<20.1f} {score2:<20.1f} {change_str:<15}")

        print("-" * 80)

        # Yearly development assessment
        years_span = latest_report.report_year - earliest_report.report_year
        overall_change = latest_report.overall_score - earliest_report.overall_score

        if overall_change > 1.0:
            print(f"Yearly development assessment: Company achieved leapfrog development in {years_span} years, financing capability greatly improved")
        elif overall_change > 0.5:
            print(f"Yearly development assessment: Company developed well in {years_span} years, financing capability significantly improved")
        elif overall_change > 0.2:
            print(f"Yearly development assessment: Company developed steadily in {years_span} years, financing capability somewhat improved")
        else:
            print(f"Yearly development assessment: Company development relatively stable in {years_span} years")

        if significant_growth:
            print("\n[PASS] Test passed: Yearly comparison analysis function effective")
            print(" - Successfully displayed company different year development comparison")
            print(" - Each dimension score change clear, reflects yearly development trajectory")
            print(" - Provides yearly development assessment and trend analysis")
            return True
        else:
            print("\n[FAIL] Test failed: No obvious yearly development change found")
            return False

    except Exception as e:
        print(f"[FAIL] Test execution error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # 1. Create diagnosis records for different years
    if create_yearly_diagnosis_records():
        # 2. Test yearly comparison analysis
        success = test_yearly_comparison()
        exit(0 if success else 1)
    else:
        print("Yearly diagnosis record creation failed")
        exit(1)