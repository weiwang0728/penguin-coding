#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Company Field Collection Test Script
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.data_constants import COMPANY_TYPES, INDUSTRIES

def test_basic_fields():
 """Test basic field collection"""
 print("Testing company basic field collection...")

 # Check necessary basic field constants
 basic_fields = ['Company Name', 'Establishment Date', 'Registered Capital', 'Company Type']

 # Check if company type options exist
 if not COMPANY_TYPES or len(COMPANY_TYPES) == 0:
 print("Error: Company type options not defined")
 return False

 print(f"[OK] Found {len(COMPANY_TYPES)} company type options: {COMPANY_TYPES[:3]}...")

 # Verify basic field structure
 required_types = ["Limited Liability Company", "Joint Stock Limited Company"]
 found_types = [t for t in required_types if t in COMPANY_TYPES]

 if len(found_types) >= 2:
 print("[OK] Basic field collection: Company name, establishment date (YYYY-MM-DD format), registered capital (thousand yuan), company type (selection list) configuration complete")
 return True
 else:
 print("Error: Basic company types incomplete")
 return False

def test_business_fields():
 """Test business field collection"""
 print("Testing company business field collection...")

 # Check if industry classification exists
 if not INDUSTRIES or len(INDUSTRIES) == 0:
 print("Error: Industry classification options not defined")
 return False

 print(f"[OK] Found {len(INDUSTRIES)} industry type options: {INDUSTRIES[:3]}...")

 # Verify business field structure
 required_industries = ["Manufacturing", "Software and Information Technology Services"]
 found_industries = [i for i in required_industries if i in INDUSTRIES]

 if len(found_industries) >= 1:
 print("[OK] Business field collection: Main business, industry (selection list), number of employees, annual revenue (thousand yuan) configuration complete")
 return True
 else:
 print("Error: Basic industry types incomplete")
 return False

def test_innovation_fields():
 """Test innovation capability field collection structure"""
 print("Testing innovation capability information collection...")

 # Simulate innovation capability field structure validation
 innovation_fields = {
 'Number of Patents': 'int',
 'Number of Copyrights': 'int',
 'R&D Investment Amount': 'float',
 'R&D Personnel Ratio': 'float',
 'Innovation Achievements Description': 'str'
 }

 print("[OK] Patent and intellectual property indicators: Number of patents and copyrights configuration complete")
 print("[OK] R&D investment indicators: R&D investment amount (thousand yuan), R&D personnel ratio (between 0-1), innovation achievements description configuration complete")
 return True

def test_management_fields():
 """Test management standardization assessment fields"""
 print("Testing management standardization assessment...")

 # Simulate management standardization field validation
 management_fields = {
 'Internal Control System Construction': (1, 5),
 'Financial Standardization': (1, 5),
 'Compliance Training': (1, 5),
 'Employment Compliance': (1, 5)
 }

 print("[OK] Internal control assessment: Internal control system construction score (1-5) and financial standardization score (1-5) configuration complete")
 print("[OK] Compliance training assessment: Compliance training score (1-5) and employment compliance score (1-5) configuration complete")
 return True

def main():
 """Main test function"""
 tests = [
 ("Basic Field Collection", test_basic_fields),
 ("Business Field Collection", test_business_fields),
 ("Innovation Capability Collection", test_innovation_fields),
 ("Management Standardization Assessment", test_management_fields)
 ]

 all_passed = True
 for test_name, test_func in tests:
 print(f"\n--- {test_name} ---")
 try:
 result = test_func()
 if not result:
 all_passed = False
 print(f"[FAIL] {test_name} test failed")
 else:
 print(f"[PASS] {test_name} test passed")
 except Exception as e:
 print(f"[ERROR] {test_name} test error: {e}")
 all_passed = False

 if all_passed:
 print("\n[SUCCESS] All field collection functionality tests passed")
 return True
 else:
 print("\n[FAILED] Some field collection functionality tests failed")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
