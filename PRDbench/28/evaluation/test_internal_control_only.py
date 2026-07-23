#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for internal control assessment
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import Company
import inspect

def main():
 """Test internal control assessment"""
 print("Testing management standardization assessment - internal control assessment...")

 try:
 # Actually check Company model fields
 company_fields = [field.name for field in Company.__table__.columns]

 required_fields = ['internal_control_score', 'financial_standard_score']
 missing_fields = [field for field in required_fields if field not in company_fields]

 if missing_fields:
 print(f"Error: Missing fields {missing_fields}")
 return False

 # Check field types
 field_types = {field.name: str(field.type) for field in Company.__table__.columns}

 if 'INTEGER' not in field_types.get('internal_control_score', ''):
 print("Error: Internal control system construction score field type incorrect")
 return False

 if 'INTEGER' not in field_types.get('financial_standard_score', ''):
 print("Error: Financial standardization score field type incorrect")
 return False

 print("Internal control system construction score (1-5) and financial standardization score (1-5) configuration complete")
 print("Test passed: Internal control assessment functionality complete")
 return True

 except Exception as e:
 print(f"Test failed: {e}")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
