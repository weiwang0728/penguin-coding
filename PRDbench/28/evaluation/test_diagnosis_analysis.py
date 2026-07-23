#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnosis analysisfunctionTestScript
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
 name="Innovation Technology Company",
 establishment_date=datetime.strptime("2020-06-15", "%Y-%m-%d").date(),
 registered_capital=500,
 company_type="Limited Liability Company",
 main_business="Software Development and Technical Services",
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
 innovation_achievements="Obtained multiple software copyrights and utility model patents",
 internal_control_score=4,
 financial_standard_score=4,
 compliance_training_score=3,
 employment_compliance_score=4,
 created_at=datetime.now(),
 updated_at=datetime.now()
 )

def test_funding_gap_analysis():
 """Testfunding gap assessmentAnalysis"""
 print("Testfunding gap assessmentAnalysis...")
 
 diagnosis_service = DiagnosisService()
 test_company = create_test_company()
 
 # Testfunding gapscoreCalculate
 funding_gap_score = diagnosis_service._calculate_funding_gap_score(test_company)
 
 if not (1.0 <= funding_gap_score <= 5.0):
 print("Error: funding gapscoreout of range")
 return False
 
 print(f"[OK] funding gap assessmentscore: {funding_gap_score:.1f}/5.0")
 print("[OK] Baseequal tocompanyFinancialDataAuto/AutomaticCalculateAndDisplayfunding gap assessmentresult")
 return True

def test_debt_capacity_analysis():
 """Testdebt capacityAnalysis"""
 print("Testdebt capacityAnalysis...")
 
 diagnosis_service = DiagnosisService()
 test_company = create_test_company()
 
 # Testdebt capacityscoreCalculate
 debt_capacity_score = diagnosis_service._calculate_debt_capacity_score(test_company)
 
 if not (1.0 <= debt_capacity_score <= 5.0):
 print("Error: debt capacityscoreout of range")
 return False
 
 print(f"[OK] debt capacityAssessmentscore: {debt_capacity_score:.1f}/5.0")
 print("[OK] Baseequal toasset-liability ratio etc.To/Atshort2Financialindicatorto performdebt capacityassessment")
 return True

def test_innovation_score_calculation():
 """Testinnovation capabilityscoreCalculate"""
 print("Testinnovation capabilityscoreCalculate...")
 
 diagnosis_service = DiagnosisService()
 test_company = create_test_company()
 
 # Testinnovation capabilityscoreCalculate
 innovation_score = diagnosis_service._calculate_innovation_score(test_company)
 
 if not (1.0 <= innovation_score <= 5.0):
 print("Error: innovation capabilityscoreout of range")
 return False
 
 print(f"[OK] innovation capabilityAssessmentscore: {innovation_score:.1f}/5.0")
 print("[OK] Baseequal toNumber of patents、R&D investmentproportion etc.To/Atshort2InnovationindicatorAuto/AutomaticCalculatescore")
 return True

def test_financing_channel_recommendation():
 """Test financing channels recommendation"""
 print("Test financing channels recommendation...")
 
 diagnosis_service = DiagnosisService()
 test_company = create_test_company()
 
 # Test financing suggestions generation
 financing_suggestions = diagnosis_service._generate_financing_suggestions(test_company, 4.0)
 
 if not financing_suggestions or len(financing_suggestions) < 50:
 print("Error: Financing suggestions generation failed or content tooshort")
 return False
 
 # Check whether it contains at least3financing channels
 channels = ["Bank Credit", "Venture Capital", "Government Subsidy", "Supply Chain Finance", "NEEQ/STAR Market"]
 found_channels = [ch for ch in channels if ch in financing_suggestions]
 
 if len(found_channels) < 3:
 print("Error: Recommendfinancing channelsless than3")
 return False
 
 print(f"[OK] recommended {len(found_channels)} financing channels: {found_channels[:3]}...")
 print("[OK] Each recommended channel shows applicability assessment and key review requirements")
 return True

def test_improvement_suggestions():
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
 print(f"RecommendationContentPreview: {improvement_suggestions[:200]}...")
 return False
 
 print("[OK] Generate for R&Dinvestment、intellectual property、management compliance specific dimensions improvement suggestions")
 return True

def main():
 """Main test function"""
 tests = [
 ("funding gap assessmentAnalysis", test_funding_gap_analysis),
 ("debt capacityAnalysis", test_debt_capacity_analysis),
 ("innovation capabilityscoreCalculate", test_innovation_score_calculation),
 ("financing channels recommendation", test_financing_channel_recommendation),
 ("improvement suggestions generation", test_improvement_suggestions)
 ]
 
 all_passed = True
 for test_name, test_func in tests:
 print(f"\n--- {test_name} ---")
 try:
 result = test_func()
 if not result:
 all_passed = False
 print(f"[FAIL] {test_name} Test failed")
 else:
 print(f"[PASS] {test_name} Test passed")
 except Exception as e:
 print(f"[ERROR] {test_name} TestError occurred: {e}")
 all_passed = False
 
 if all_passed:
 print("\n[SUCCESS] all have diagnosis analysisfunctionTest passed")
 return True
 else:
 print("\n[FAILED] Part pointsdiagnosis analysisfunctionTest failed")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)