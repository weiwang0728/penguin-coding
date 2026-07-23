"""
Test Execution Script
Used to run all test cases and generate test reports
"""
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_pytest_tests():
    """Run pytest tests"""
    print("=" * 60)
    print("Starting automated tests...")
    print("=" * 60)

    # Switch to evaluation directory
    evaluation_dir = Path(__file__).parent

    # Run pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        str(evaluation_dir / "tests"),
        "-v",
        "--tb=short",
        "--color=yes",
        f"--junitxml={evaluation_dir}/test_results.xml"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=evaluation_dir)

        print("Test Output:")
        print("-" * 40)
        print(result.stdout)

        if result.stderr:
            print("Error Output:")
            print("-" * 40)
            print(result.stderr)

        print("=" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed, exit code: {result.returncode}")
        print("=" * 60)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_shell_tests():
    """Run shell interaction tests"""
    print("\n" + "=" * 60)
    print("Starting shell interaction tests...")
    print("=" * 60)

    # Read test plan
    test_plan_file = Path(__file__).parent / "detailed_test_plan.json"

    if not test_plan_file.exists():
        print("❌ Test plan file does not exist")
        return False

    with open(test_plan_file, 'r', encoding='utf-8') as f:
        test_plan = json.load(f)

    shell_tests = [test for test in test_plan if test['type'] == 'shell_interaction']

    print(f"Found {len(shell_tests)} shell interaction tests")

    passed_tests = 0
    failed_tests = 0

    for i, test in enumerate(shell_tests, 1):
        print(f"\n[{i}/{len(shell_tests)}] Test: {test['metric']}")
        print("-" * 40)

        success = True
        for j, testcase in enumerate(test['testcases']):
            cmd = testcase['test_command']
            print(f"  Executing command: {cmd}")

            try:
                # Switch to project root directory to execute command
                project_root = Path(__file__).parent.parent
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"  ✅ Command execution succeeded")
                    if result.stdout.strip():
                        # Only display first few lines of output
                        output_lines = result.stdout.strip().split('\n')[:3]
                        for line in output_lines:
                            print(f"     {line}")
                        if len(result.stdout.strip().split('\n')) > 3:
                            print("     ...")
                else:
                    print(f"  ❌ Command execution failed (exit code: {result.returncode})")
                    if result.stderr:
                        error_lines = result.stderr.strip().split('\n')[:2]
                        for line in error_lines:
                            print(f"     Error: {line}")
                    success = False

            except subprocess.TimeoutExpired:
                print(f"  ⏰ Command execution timeout")
                success = False
            except Exception as e:
                print(f"  ❌ Execution error: {e}")
                success = False

        if success:
            passed_tests += 1
            print(f"  ✅ Test passed")
        else:
            failed_tests += 1
            print(f"  ❌ Test failed")

    print("\n" + "=" * 60)
    print(f"Shell interaction test results: {passed_tests} passed, {failed_tests} failed")
    print("=" * 60)

    return failed_tests == 0

def generate_test_report():
    """Generate test report"""
    print("\n" + "=" * 60)
    print("Generating test report...")
    print("=" * 60)

    report_content = f"""
# Test Execution Report

**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Overview

This report contains complete test results for the College Student Self-Control and Attention Stability Intelligent Analysis System.

## Test Types

### 1. Unit Tests
- **Test files:** evaluation/tests/test_*.py
- **Test framework:** pytest
- **Coverage:**
  - Scale creation and management
  - Data import/export
  - Statistical analysis functions
  - Data management functions
  - Visualization functions

### 2. Shell Interaction Tests
- **Test plan:** evaluation/detailed_test_plan.json
- **Test type:** Command line interface functional verification
- **Coverage:**
  - Program startup and help information
  - Module entry point verification
  - Data import/export commands
  - Analysis command execution

### 3. File Comparison Tests
- **Test content:** Comparison of output files with expected files
- **Coverage:**
  - Scale export file format
  - Report generation file content
  - Chart export file quality

## Test File Structure

```
evaluation/
├── detailed_test_plan.json     # Detailed test plan
├── pytest.ini                  # pytest configuration
├── run_tests.py                # Test execution script
├── tests/                      # Unit test directory
│   ├── test_scale_creation.py
│   ├── test_scale_import_export.py
│   ├── test_statistical_analysis.py
│   ├── test_data_management.py
│   ├── test_visualization.py
│   └── test_data_export.py
├── test_*.csv                  # Test input files
├── expected_*.csv              # Expected output files
└── temp_*                      # Temporary test files
```

## Running Tests

### Run all tests
```bash
python evaluation/run_tests.py
```

### Run specific tests
```bash
cd evaluation
pytest tests/test_scale_creation.py -v
```

### Run shell interaction tests
```bash
python src/main.py --help
python src/main.py init
python src/main.py scales list
```

## Test Results Interpretation

- ✅ **Passed:** Function works normally, meets expectations
- ❌ **Failed:** Function has issues, needs fixing
- ⏰ **Timeout:** Execution time too long, possible performance issue
- ⚠️ **Warning:** Function basically normal, but has room for improvement

## Notes

1. Please ensure all dependencies are installed before testing
2. Some tests need to create temporary files, which will be cleaned up automatically after testing
3. Large dataset tests may take a long time
4. Network-related functional tests require network connection

## Troubleshooting

If tests fail, please check:
1. Whether Python environment and dependencies are correctly installed
2. Whether database connection is normal
3. Whether file permissions are sufficient
4. Whether system resources are adequate

---

*This report was generated by the automated testing system*
"""

    report_file = Path(__file__).parent / "TEST_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content.strip())

    print(f"✅ Test report generated: {report_file}")

def main():
    """Main function"""
    print("College Student Self-Control and Attention Stability Intelligent Analysis System - Automated Testing")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run unit tests
    unit_test_success = run_pytest_tests()

    # Run shell interaction tests
    shell_test_success = run_shell_tests()

    # Generate test report
    generate_test_report()

    # Summary
    print("\n" + "=" * 60)
    print("Test execution completed!")
    print("=" * 60)

    if unit_test_success and shell_test_success:
        print("All tests passed! System functionality is normal.")
        return 0
    else:
        print("Some tests failed, please check the output above and fix the issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)