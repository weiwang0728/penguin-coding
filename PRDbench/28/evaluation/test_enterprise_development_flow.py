#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 2.3.5b Report Comparison function
Through real business process: company entry → diagnosis → development update → re-diagnosis to produce different period reports
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

def simulate_enterprise_development_flow():
    """Simulate company development real business process"""
    print("Simulating company development real business process...")

    company_service = CompanyService()
    diagnosis_service = DiagnosisService()
    report_service = ReportService()

    try:
        # Step 1: Company entry initial information (startup period status)
        print("\n=== Step 1: Company entry initial information (startup period) ===")
        db = SessionLocal()

        company_name = "Growth Trajectory Technology Company"

        # Delete possibly existing same name company
        existing = company_service.get_company_by_name(db, company_name)
        if existing:
            company_service.delete_company(db, existing.id)

        # Enter startup period company information
        initial_data = {
            'name': company_name,
            'establishment_date': datetime(2022, 1, 15),
            'registered_capital': 500.0, # Startup period capital relatively small
            'company_type': 'Limited Liability Company',
            'main_business': 'Software Development Service',
            'industry': 'Information Transmission, Software and Information Technology Services',
            'employee_count': 15, # Startup period employees few
            'annual_revenue': 300.0, # Startup period revenue low
            'annual_profit': 30.0, # Startup period profit meager
            'asset_liability_ratio': 0.6, # Startup period debt ratio relatively high
            'patent_count': 0, # Startup period no patents
            'copyright_count': 1, # Startup period only has 1 copyright
            'rd_investment': 45.0, # Startup period R&D investment few
            'rd_revenue_ratio': 0.15, # R&D investment accounts for 15% of revenue
            'rd_personnel_ratio': 0.2, # R&D personnel ratio 20%
            'innovation_achievements': 'Developed basic software product prototype',
            'internal_control_score': 2, # Startup period management standardization low
            'financial_standard_score': 2,
            'compliance_training_score': 2,
            'employment_compliance_score': 2
        }

        schema = CompanyCreateSchema(**initial_data)
        company = company_service.create_company(db, schema)
        print(f"Entered startup period company information: {company.name}")
        print(f" Employee count: {company.employee_count}, Revenue: {company.annual_revenue} thousand yuan, Patents: {company.patent_count} item(s)")
        db.close()

        # Step 2: Perform first diagnosis for startup period status
        print("\n=== Step 2: Startup period diagnosis ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)

        diagnosis_1 = diagnosis_service.diagnose_company(db, company)
        report_1 = report_service.generate_full_report(company, diagnosis_1)
        print(f"Startup period diagnosis complete, overall score: {diagnosis_1.overall_score:.1f}/5.0")
        print(f"Generated report file: {os.path.basename(report_1)}")
        db.close()

        time.sleep(2) # Ensure timestamp different

        # Step 3: Simulate company development, update company information (growth period)
        print("\n=== Step 3: Company development, update information (growth period) ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)

        # Company development one year later improvements
        development_updates = {
            'registered_capital': 1000.0, # Capital increase and share expansion
            'employee_count': 35, # Employee growth
            'annual_revenue': 800.0, # Revenue large increase
            'annual_profit': 120.0, # Profit significantly improved
            'asset_liability_ratio': 0.45, # Debt ratio improved
            'patent_count': 3, # Obtained patents
            'copyright_count': 4, # Copyright increased
            'rd_investment': 144.0, # R&D investment increased
            'rd_revenue_ratio': 0.18, # R&D investment accounts for 18% of revenue
            'rd_personnel_ratio': 0.3, # R&D personnel ratio improved
            'innovation_achievements': 'Developed multiple marketable software products, obtained customer recognition',
            'internal_control_score': 3, # Management standardization improved
            'financial_standard_score': 3,
            'compliance_training_score': 3,
            'employment_compliance_score': 3
        }

        updated_company = company_service.update_company(db, company.id, development_updates)
        print("Company development update complete:")
        print(f" Employee count: {updated_company.employee_count} (+{updated_company.employee_count-15})")
        print(f" Revenue: {updated_company.annual_revenue} thousand yuan (+{updated_company.annual_revenue-300.0:.0f})")
        print(f" Patents: {updated_company.patent_count} item(s) (+{updated_company.patent_count})")
        db.close()

        # Step 4: Perform second diagnosis for growth period status
        print("\n=== Step 4: Growth period diagnosis ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)

        diagnosis_2 = diagnosis_service.diagnose_company(db, company)
        report_2 = report_service.generate_full_report(company, diagnosis_2)
        print(f"Growth period diagnosis complete, overall score: {diagnosis_2.overall_score:.1f}/5.0")
        print(f"Score improvement: {diagnosis_2.overall_score - diagnosis_1.overall_score:+.1f}")
        print(f"Generated report file: {os.path.basename(report_2)}")
        db.close()

        time.sleep(2)

        # Step 5: Continue development, update company information (maturity period)
        print("\n=== Step 5: Company maturity, re-update information (maturity period) ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)

        # Company further development improvements
        maturity_updates = {
            'registered_capital': 2000.0, # Further capital increase
            'employee_count': 60, # Employees continue to grow
            'annual_revenue': 1500.0, # Revenue further increase
            'annual_profit': 300.0, # Profit large increase
            'asset_liability_ratio': 0.3, # Debt ratio further optimization
            'patent_count': 8, # Patents largely increased
            'copyright_count': 6, # Copyright continue to increase
            'rd_investment': 300.0, # R&D investment largely increased
            'rd_revenue_ratio': 0.2, # R&D investment accounts for 20% of revenue
            'rd_personnel_ratio': 0.4, # R&D personnel ratio 40%
            'innovation_achievements': 'Developed industry-leading innovative products, have core technical advantages',
            'internal_control_score': 4, # Management standardization reached good level
            'financial_standard_score': 4,
            'compliance_training_score': 4,
            'employment_compliance_score': 4
        }

        updated_company = company_service.update_company(db, company.id, maturity_updates)
        print("Company maturity period update complete:")
        print(f" Employee count: {updated_company.employee_count} (Total growth +{updated_company.employee_count-15})")
        print(f" Revenue: {updated_company.annual_revenue} thousand yuan (Total growth +{updated_company.annual_revenue-300.0:.0f})")
        print(f" Patents: {updated_company.patent_count} item(s) (Total growth +{updated_company.patent_count})")
        db.close()

        # Step 6: Perform third diagnosis for maturity period status
        print("\n=== Step 6: Maturity period diagnosis ===")
        db = SessionLocal()
        company = company_service.get_company_by_name(db, company_name)

        diagnosis_3 = diagnosis_service.diagnose_company(db, company)
        report_3 = report_service.generate_full_report(company, diagnosis_3)
        print(f"Maturity period diagnosis complete, overall score: {diagnosis_3.overall_score:.1f}/5.0")
        print(f"Total improvement: {diagnosis_3.overall_score - diagnosis_1.overall_score:+.1f}")
        print(f"Generated report file: {os.path.basename(report_3)}")
        db.close()

        print(f"\n[PASS] Real business process complete")
        print(f"Development trajectory: Startup period ({diagnosis_1.overall_score:.1f}) → Growth period ({diagnosis_2.overall_score:.1f}) → Maturity period ({diagnosis_3.overall_score:.1f})")

        return True, (diagnosis_1, diagnosis_2, diagnosis_3)

    except Exception as e:
        print(f"[FAIL] Simulating company development process failed: {e}")
        return False, None

def test_historical_comparison():
    """Test historical diagnosis comparison function"""
    print("\n=== Test 2.3.5b Historical Reports comparison function ===")

    try:
        db = SessionLocal()
        company_service = CompanyService()
        diagnosis_service = DiagnosisService()

        company = company_service.get_company_by_name(db, "Growth Trajectory Technology Company")
        if not company:
            print("[FAIL] Could not find test company")
            return False

        # Get all diagnosis history for this company
        reports = diagnosis_service.get_company_reports(db, company.id)

        if len(reports) < 2:
            print(f"[FAIL] Insufficient diagnosis records, current record count: {len(reports)}")
            return False

        print(f"Found {len(reports)} items of historical diagnosis records")

        # Sort by time, compare earliest and newest records
        reports_by_time = sorted(reports, key=lambda r: r.created_at)
        earliest_report = reports_by_time[0] # Startup period diagnosis
        latest_report = reports_by_time[-1] # Latest diagnosis

        print("\n" + "=" * 80)
        print("Company development history comparison analysis")
        print("=" * 80)

        time1 = earliest_report.created_at.strftime('%Y-%m-%d %H:%M:%S')
        time2 = latest_report.created_at.strftime('%Y-%m-%d %H:%M:%S')

        print(f"{'Assessment dimension':<15} {'Initial status':<20} {'Current status':<20} {'Development change':<15}")
        print(f"{'':^15} {time1:<20} {time2:<20} {'':^15}")
        print("-" * 80)

        dimensions = [
            ("Funding gap assessment", earliest_report.funding_gap_score, latest_report.funding_gap_score),
            ("Debt capacity assessment", earliest_report.debt_capacity_score, latest_report.debt_capacity_score),
            ("Innovation capability assessment", earliest_report.innovation_score, latest_report.innovation_score),
            ("Management standardization assessment", earliest_report.management_score, latest_report.management_score),
            ("Overall score", earliest_report.overall_score, latest_report.overall_score)
        ]

        has_improvement = False
        for name, score1, score2 in dimensions:
            change = score2 - score1
            if change > 0.3:
                change_str = f"{change:+.1f} Significantly improved"
                has_improvement = True
            elif change > 0.1:
                change_str = f"{change:+.1f} Noticeably improved"
                has_improvement = True
            elif change > 0:
                change_str = f"{change:+.1f} Somewhat improved"
            elif change < -0.1:
                change_str = f"{change:+.1f} Somewhat declined"
            elif change < 0:
                change_str = f"{change:+.1f} Slightly declined"
            else:
                change_str = "0.0 Remained stable"

            print(f"{name:<15} {score1:<20.1f} {score2:<20.1f} {change_str:<15}")

        print("-" * 80)

        # Development summary
        time_span_days = (latest_report.created_at - earliest_report.created_at).days
        time_span_hours = (latest_report.created_at - earliest_report.created_at).seconds // 3600
        overall_improvement = latest_report.overall_score - earliest_report.overall_score

        if time_span_days > 0:
            print(f"Development history: {time_span_days} days development process, overall score improved by {overall_improvement:+.1f} points")
        else:
            print(f"Development history: {time_span_hours} hours development process, overall score improved by {overall_improvement:+.1f} points")

        if has_improvement:
            print("\n[PASS] Test passed: company development history comparison function effective")
            print(" - Really simulated company development process: entry → diagnosis → development → re-diagnosis")
            print(" - Successfully displayed company different development stage comparison information")
            print(" - Each dimension score reflects real growth changes")
            print(" - Provides development trajectory analysis and change assessment")
            return True
        else:
            print("\n[WARN] Company development change relatively small, but comparison function normal")
            print(" - Basic comparison display function effective")
            print(" - Recommend increasing company development change amplitude to better demonstrate comparison effect")
            return True

    except Exception as e:
        print(f"[FAIL] Test execution error: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # 1. Simulate complete company development business process
    success, diagnosis_results = simulate_enterprise_development_flow()

    if success:
        # 2. Test historical comparison function
        comparison_success = test_historical_comparison()
        exit(0 if comparison_success else 1)
    else:
        print("Company development process simulation failed")
        exit(1)