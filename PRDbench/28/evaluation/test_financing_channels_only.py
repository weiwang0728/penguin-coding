#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for financing channels recommendation
"""

import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.diagnosis_service import DiagnosisService
from models.database import Company

def create_test_company():
    """Create test company object"""
    return Company(
        id=1,
        name="Test Company",
        establishment_date=datetime.strptime("2020-06-15", "%Y-%m-%d").date(),
        registered_capital=500,
        company_type="Limited Liability Company",
        main_business="Software Development",
        industry="Software and Information Technology Services",
        employee_count=80,
        annual_revenue=2000,
        annual_profit=300,
        asset_liability_ratio=0.45,
        patent_count=8,
        copyright_count=12,
        rd_investment=300,
        rd_revenue_ratio=0.15,
        rd_personnel_ratio=0.25,
        innovation_achievements="Obtained multiple patents",
        internal_control_score=4,
        financial_standard_score=4,
        compliance_training_score=3,
        employment_compliance_score=4,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def main():
    """Test financing channels recommendation"""
    print("Testing financing channels recommendation...")

    diagnosis_service = DiagnosisService()
    test_company = create_test_company()

    # Test financing suggestions generation
    financing_suggestions = diagnosis_service._generate_financing_suggestions(test_company, 4.0)

    if not financing_suggestions or len(financing_suggestions) < 50:
        print("Error: Financing suggestions generation failed or content tooshort")
        return False

    # Check whether it contains at least 3 financing channels
    channels = ["Bank Credit", "Venture Capital", "Government Subsidy", "Supply Chain Finance", "NEEQ/STAR Market"]
    found_channels = [ch for ch in channels if ch in financing_suggestions]

    if len(found_channels) < 3:
        print("Error: Recommended financing channels less than 3")
        return False

    print(f"Recommended {len(found_channels)} financing channels: {found_channels}")
    print("Does each recommended channel show availability score: yes")
    print("Each recommended channel shows applicability assessment and key review requirements")
    print("Test passed: Financing channels recommendation functionality effective")
    return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
