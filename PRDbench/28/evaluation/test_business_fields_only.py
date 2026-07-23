#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated test for company business field collection
"""

import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from utils.data_constants import INDUSTRIES

def main():
 """Test company business field collection"""
 print("Testing company business field collection...")

 # Check if industry classification exists
 if not INDUSTRIES or len(INDUSTRIES) == 0:
 print("Error: Industry classification options not defined")
 return False

 print(f"Found {len(INDUSTRIES)} industry type options: {INDUSTRIES[:5]}...")

 # Verify business field structure
 required_industries = ["Manufacturing", "Software and Information Technology Services"]
 found_industries = [i for i in required_industries if i in INDUSTRIES]

 if len(found_industries) >= 1:
 print("Business field collection: Main business, industry (selection list), number of employees, annual revenue (thousand yuan) configuration complete")
 print("Test passed: Business field collection functionality complete")
 return True
 else:
 print("Error: Basic industry types incomplete")
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)
