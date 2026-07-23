#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for matplotlibchart generationfunction
"""

import sys
import os
import tempfile
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.report_service import ReportService
from services.diagnosis_service import DiagnosisService
from models.database import Company
from models.schemas import DiagnosisResultSchema

def create_test_company():
 """Create test company object"""
 return Company(
 id=1,
 name="TestTechnologyCompany",
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

def create_test_diagnosis():
 """CreateTestdiagnosisresult"""
 return DiagnosisResultSchema(
 funding_gap_score=4.0,
 debt_capacity_score=4.2,
 innovation_score=4.5,
 management_score=3.8,
 overall_score=4.1,
 diagnosis_result="Good Financing Capability",
 financing_suggestions="Recommend Bank Credit and Venture Capital",
 improvement_suggestions="Recommendation to strengthen management standardization"
 )

def main():
 """Testchart generationfunction"""
 print("Testmatplotlibchart generationfunction...")
 
 try:
 # Check if matplotlib is available
 import matplotlib
 matplotlib.use('Agg') # use non-interactive backend
 print("matplotlibModule imported successfully")
 
 # Create ReportService instance
 report_service = ReportService()
 
 # CreateTestData
 test_company = create_test_company()
 test_diagnosis = create_test_diagnosis()
 
 # Testchart generation
 print("Start generating charts...")
 chart_paths = report_service._generate_charts(test_company, test_diagnosis)
 
 if not chart_paths:
 print("Error: chart generation returned empty result")
 return False
 
 print(f"Successfully generated {len(chart_paths)} charts:")
 for chart_name, chart_path in chart_paths.items():
 if os.path.exists(chart_path):
 file_size = os.path.getsize(chart_path)
 print(f" [OK] {chart_name}: {chart_path} ({file_size} bytes)")
 else:
 print(f" [ERROR] {chart_name}: {chart_path} (file does not exist)")
 return False
 
 # Check if radar chart was generated
 radar_files = [path for name, path in chart_paths.items() if "radar" in path]
 if radar_files:
 print("score radar chart generated successfully，Display dimensional scores")
 print("Test passed: matplotlib score radar chart generation functionality normal")
 return True
 else:
 print("Error: radar chart file not found")
 return False
 
 except ImportError as e:
 print(f"Error: matplotlibModule import failed: {e}")
 return False
 except Exception as e:
 print(f"Error: abnormality occurred during chart generation process: {e}")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)