#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.1.3progress feedbackDisplayfunction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch
from io import StringIO
from cli.company_cli import add_company
from models.database import SessionLocal, Company
from services.company_service import CompanyService

def test_progress_feedback():
 """Testprogress feedbackDisplayfunction"""
 print("Test2.1.3progress feedbackDisplay...")
 
 # prepareTestInputData
 test_inputs = [
 "TestProgresscompany2", # Company Name（avoidduplicate names）
 "2021-03-15", # Establishment Date
 "200", # Registered Capital
 "1", # Company Type select 
 "Software DevelopmentService", # Main Business
 "1", # Industry select 
 "50", # Number of Employees
 "1000", # Annual Revenue
 "150", # Annual Profit
 "0.4", # asset-liability ratio
 "y", # whetherfill ininnovation capability
 "5", # Number of patents
 "3", # Number of copyrights
 "250", # R&D investment
 "0.3", # R&D personnel ratio
 "excellentSoftwareProduct", # Innovation achievements description
 "y", # whetherto performmanagement standardizationassessment
 "4", # internal controlscore
 "4", # Financial standardization score
 "3", # compliance trainingscore
 "4", # Employment compliance score
 "n", # whether have Financinghistorical
 "y" #  confirm add
 ]
 
 # CreateInputFlow
 input_stream = StringIO('\n'.join(test_inputs))
 
 # CaptureOutput
 output_stream = StringIO()
 
 try:
 with patch('builtins.input', lambda prompt='': input_stream.readline().strip()):
 with patch('sys.stdout', output_stream):
 # Delete can  can exist in  same Namecompany
 db = SessionLocal()
 company_service = CompanyService()
 existing = company_service.get_company_by_name(db, "TestProgresscompany2")
 if existing:
 company_service.delete_company(db, existing.id)
 db.close()
 
 # ExecuteaddcompanyCommand
 add_company()
 
 # CheckOutputProgressinformation
 output = output_stream.getvalue()
 print("OutputContent:")
 print(output)
 
 # Verifyprogress feedbackwhetherexist in 
 progress_indicators = [
 "Progress：1/8",
 "Progress：2/8", 
 "Progress：3/8",
 "Progress：4/8",
 "Progress：5/8",
 "Progress：6/8",
 "Progress：7/8",
 "Progress：8/8"
 ]
 
 found_progress = []
 for indicator in progress_indicators:
 if indicator in output:
 found_progress.append(indicator)
 
 print(f"\nfind/found to ProgressIndicator: {found_progress}")
 
 if len(found_progress) >= 6: # To/Atshortfind/found to 6ProgressIndicator
 print("Test passed: progress feedbackDisplayfunctionality normal")
 return True
 else:
 print(f"Test failed: Onlyfind/found to  {len(found_progress)} ProgressIndicator，Preview/Expect/PreperiodTo/Atshort6")
 return False
 
 except Exception as e:
 print(f"TestExecuteError occurred: {e}")
 return False

if __name__ == "__main__":
 test_progress_feedback()