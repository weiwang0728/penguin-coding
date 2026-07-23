#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report file generation test script
"""

import os
import sys
import subprocess
import tempfile
import time

def run_command_with_input(command, input_data=None):
 """Run command and provide input"""
 try:
 if input_data:
 process = subprocess.Popen(
 command,
 shell=True,
 stdin=subprocess.PIPE,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True,
 cwd='src'
 )
 stdout, stderr = process.communicate(input=input_data)
 else:
 process = subprocess.Popen(
 command,
 shell=True,
 stdout=subprocess.PIPE,
 stderr=subprocess.PIPE,
 text=True,
 cwd='src'
 )
 stdout, stderr = process.communicate()

 return process.returncode, stdout, stderr
 except Exception as e:
 return -1, "", str(e)

def main():
 """Main test process"""
 print("Starting report file generation test...")

 # Company creation input data
 company_input = """TestTechnologyCompany
2020-06-15
500
1
Software Development and Technical Services
6
80
2000
300
0.45
y
8
12
300
0.25
Obtained multiple software copyrights and utility model patents
y
4
4
3
4
n
"""

 # Step 1: Create company
 print("1. Creating test company...")
 returncode, stdout, stderr = run_command_with_input(
 "python main.py company add",
 company_input
 )

 if returncode != 0:
 print(f"Company creation failure: {stderr}")
 return False

 print("Company created successfully")

 # Step 2: Generate report
 print("2. Generating diagnosis report...")
 report_input = "y\nn\n" # Execute diagnosis: yes, view report: no

 returncode, stdout, stderr = run_command_with_input(
 "python main.py report generate --name TestTechnologyCompany",
 report_input
 )

 if returncode != 0:
 print(f"Report generation failure: {stderr}")
 return False

 print("Report generated successfully")

 # Step 3: Check whether file exists
 print("3. Checking report file...")

 # ReportService creates reports folder in src directory
 os.chdir('src')
 reports_dir = "reports"

 if not os.path.exists(reports_dir):
 print("Report directory does not exist")
 os.chdir('..') # Return to original directory
 return False

 # Search for matching report files
 import glob
 pattern = os.path.join(reports_dir, "Financing diagnosis report_TestTechnologyCompany_*.txt")
 report_files = glob.glob(pattern)

 if not report_files:
 print("Report files not found")
 # List all files to see
 print("Reports directory content:")
 for item in os.listdir(reports_dir):
 item_path = os.path.join(reports_dir, item)
 if os.path.isfile(item_path):
 print(f" File: {item}")
 else:
 print(f" Directory: {item}")
 os.chdir('..') # Return to original directory
 return False

 report_file = report_files[0] # Take first matching file

 # Check file size
 file_size = os.path.getsize(report_file)
 if file_size == 0:
 print("Report file is empty")
 return False

 print(f"Found report file: {os.path.basename(report_file)}")
 print(f"File size: {file_size} bytes")

 # Check file content structure
 try:
 with open(report_file, 'r', encoding='utf-8') as f:
 content = f.read()

 # Check required content
 required_sections = [
 "Small and Medium Enterprise Financing Intelligent Diagnosis and Optimization Recommendation Report",
 "1. Company Profile",
 "2. Financing Capability Score",
 "3. Detailed Analysis",
 "4. Financing Suggestions",
 "5. Improvement Suggestions",
 "6. Chart Analysis"
 ]

 missing_sections = []
 for section in required_sections:
 if section not in content:
 missing_sections.append(section)

 if missing_sections:
 print(f"Report missing required sections: {missing_sections}")
 return False

 print("Report file content structure complete")
 print("Test passed: Report file save functionality normal")
 os.chdir('..') # Return to original directory
 return True

 except Exception as e:
 print(f"Reading report file failure: {e}")
 os.chdir('..') # Return to original directory
 return False

if __name__ == "__main__":
 success = main()
 sys.exit(0 if success else 1)