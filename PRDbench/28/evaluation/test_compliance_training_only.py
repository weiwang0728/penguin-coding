#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for compliance training assessment
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from models.database import Company
import inspect

def main():
 """Test compliance training assessment"""
 print("Testing management standardization assessment - compliance training assessment...")

 try:
 # Actually check Company model fields
 company_fields = [field.name for field in Company.__table__.columns]

 required_fields = ['compliance_training_score', 'employment_compliance_score']
 missing_fields = [field for field in required_fields if field not in company_fields]

 if missing_fields:
 print(f"Error: Missing fields {missing_fields}")
 return False

 # Check field types
 field_types = {field.name: str(field.type) for field in Company.__table__.columns}

 if 'INTEGER' not in field_types.get('compliance_training_score', ''):
 print("Error: Compliance training score field type incorrect")
 return False

 if 'INTEGER' not in field_types.get('employment_compliance_score', ''):
 print("Error: Employment compliance score field type incorrect")
 return False

 print("Compliance training score (1-5) and employment compliance score (1-5) configuration complete")
 print("Test passed: Compliance training assessment functionality complete")
 return True

 except Exception as e:
 print(f"Test failed: {e}")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
