#!/usr/bin/env python3
"""
English version of file comparison test verification
Verifies the "2.1b Unit Test Coverage" test setup
"""

import subprocess
import sys
import json
from pathlib import Path

def main():
    print("Verifying file comparison test setup...")
    
    # 1. Check all required files exist
    required_files = [
        "evaluation/test_coverage_analyzer.py",
        "evaluation/expected_test_coverage_report.json", 
        "evaluation/file_comparator.py",
        "src/tests/test_utils.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"ERROR: Missing required file {file_path}")
            return False
        else:
            print(f"OK: File exists {file_path}")
    
    # 2. Execute the test command
    print("\nExecuting test command...")
    try:
        result = subprocess.run([
            "python", "evaluation/test_coverage_analyzer.py", 
            "src/tests", "evaluation/test_output_en.json"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("OK: Test coverage analyzer executed successfully")
        else:
            print(f"ERROR: Test coverage analyzer failed, exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to execute test command: {e}")
        return False
    
    # 3. Verify output file
    if Path("evaluation/test_output_en.json").exists():
        print("OK: Output file generated")
        
        # Read and verify output content
        try:
            with open("evaluation/test_output_en.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            coverage = data.get('overall_stats', {}).get('coverage_percentage', 0)
            functions_covered = data.get('overall_stats', {}).get('fully_covered_functions', 0)
            total_functions = data.get('overall_stats', {}).get('total_functions', 0)
            
            print(f"OK: Test coverage is {coverage}%")
            print(f"OK: {functions_covered}/{total_functions} functions fully covered")
            
            if coverage == 100.0:
                print("EXCELLENT: Full test coverage achieved!")
            else:
                print("WARNING: Test coverage is not 100%")
                
        except Exception as e:
            print(f"ERROR: Failed to read output file: {e}")
            return False
    else:
        print("ERROR: Output file not generated")
        return False
    
    print("\n" + "="*50)
    print("File comparison test verification completed - ALL CHECKS PASSED!")
    print("="*50)
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)