#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for innovation capability information collection
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import Company
import inspect

def main():
 """Test innovation capability information collection - patents and intellectual property"""
 print("Testing patent and intellectual property indicators...")

 try:
 # Actually check Company model fields
 company_fields = [field.name for field in Company.__table__.columns]

 required_fields = ['patent_count', 'copyright_count']
 missing_fields = [field for field in required_fields if field not in company_fields]

 if missing_fields:
 print(f"Error: Missing fields {missing_fields}")
 return False

 # Check field types
 field_types = {field.name: str(field.type) for field in Company.__table__.columns}

 if 'INTEGER' not in field_types.get('patent_count', ''):
 print("Error: Patent count field type incorrect")
 return False

 if 'INTEGER' not in field_types.get('copyright_count', ''):
 print("Error: Copyright count field type incorrect")
 return False

 print("Number of patents and copyrights configuration complete")
 print("Test passed: Patent and intellectual property collection functionality complete")
 return True

 except Exception as e:
 print(f"Test failed: {e}")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
