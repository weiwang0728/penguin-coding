#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for funding gap assessment analysis
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
 """Test funding gap assessment analysis"""
 print("Testing funding gap assessment analysis...")

 diagnosis_service = DiagnosisService()
 test_company = create_test_company()

 # Test funding gap score calculation
 funding_gap_score = diagnosis_service._calculate_funding_gap_score(test_company)

 if not (1.0 <= funding_gap_score <= 5.0):
 print("Error: Funding gap score out of range")
 return False

 print(f"Funding gap assessment score: {funding_gap_score:.1f}/5.0")
 print("Automatically calculate and display funding gap assessment results based on company financial data")
 print("Test passed: Funding gap assessment analysis functionality normal")
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
