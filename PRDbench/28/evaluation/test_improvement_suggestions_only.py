#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for improvement suggestions generation
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
 patent_count=2, # low value triggers improvement suggestions
 copyright_count=1,
 rd_investment=100,
 rd_revenue_ratio=0.05,
 rd_personnel_ratio=0.15,
 innovation_achievements="short patents",
 internal_control_score=2, # low value triggers improvement suggestions
 financial_standard_score=2,
 compliance_training_score=2,
 employment_compliance_score=2,
 created_at=datetime.now(),
 updated_at=datetime.now()
 )

def main():
 """Test improvement suggestions generation"""
 print("Test improvement suggestions generation...")
 
 diagnosis_service = DiagnosisService()
 test_company = create_test_company()
 
 # Test improvement suggestions generation - using lowscore trigger specific suggestions
 improvement_suggestions = diagnosis_service._generate_improvement_suggestions(
 test_company, 2.5, 2.5, 2.5, 2.5
 )
 
 if not improvement_suggestions or len(improvement_suggestions) < 50:
 print("Error: improvement suggestions generationfailed or content too short")
 return False
 
 # Check whethercontainsthree dimension suggestions
 keywords_found = []
 if "R&D" in improvement_suggestions or "R&D" in improvement_suggestions:
 keywords_found.append("R&D investment")
 if "patent" in improvement_suggestions or "intellectual property" in improvement_suggestions:
 keywords_found.append("intellectual property") 
 if "management" in improvement_suggestions or "compliance" in improvement_suggestions:
 keywords_found.append("management compliance")
 
 if len(keywords_found) < 2:
 print(f"Error: improvement suggestionsinsufficient dimension coverage，only found: {keywords_found}")
 return False
 
 print("Generate for R&Dinvestment、intellectual property、management compliance specific dimensions improvement suggestions")
 print("Test passed: improvement suggestions generation functionality effective")
 return True

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)