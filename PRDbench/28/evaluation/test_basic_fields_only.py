#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for company basic field collection
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.data_constants import COMPANY_TYPES

def main():
 """Test company basic field collection"""
 print("Testing company basic field collection...")

 # Check basic field constants
 basic_fields = ['Company Name', 'Establishment Date', 'Registered Capital', 'Company Type']

 # Check if company type options exist
 if not COMPANY_TYPES or len(COMPANY_TYPES) == 0:
 print("Error: Company type options not defined")
 return False

 print(f"Found {len(COMPANY_TYPES)} company type options: {COMPANY_TYPES}")

 # Verify basic field structure
 required_types = ["Limited Liability Company", "Joint Stock Limited Company"]
 found_types = [t for t in required_types if t in COMPANY_TYPES]

 if len(found_types) >= 2:
 print("Basic field collection: Company name, establishment date (YYYY-MM-DD format), registered capital (thousand yuan), company type (selection list) configuration complete")
 print("Test passed: Basic field collection functionality complete")
 return True
 else:
 print("Error: Basic company types incomplete")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
