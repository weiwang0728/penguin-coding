# Qingdao District 1 Lottery System - Test Plan Documentation

## Test Plan Overview

This test plan provides comprehensive quality assurance verification for the Qingdao District 1 Lottery System, including 24 test points covering all PRD functional requirements.

## Test Plan Structure

```
evaluation/
├── detailed_test_plan.json    # Detailed test plan (24 test points)
├── metric.json               # Functional evaluation metrics
├── run_tests.py             # Automated test runner script
├── README.md                # This file
├── inputs/                  # Test input files directory
│   ├── startup_test.in      # Program startup test input
│   ├── csv_import_test.in   # CSV import test input
│   ├── full_workflow_test.in # Full workflow test input
│   └── ...                  # Other test input files
├── test_data/              # Test data files directory
│   ├── employees_5.csv     # 5 employee data
│   ├── employees_10.csv    # 10 employee data
│   ├── employees_missing_field.csv  # Missing field test data
│   └── ...                 # Other test data files
├── tests/                  # Unit test directory
│   ├── test_weighted_sampling.py   # Weighted sampling test
│   ├── test_no_duplicate.py        # Duplicate winning test
│   ├── test_fairness_report.py     # Fairness report test
│   └── test_file_operations.py     # File operations test
└── expected_outputs/       # Expected output files directory
    └── sample_result.txt   # Sample result file
```

## Test Type Description

### 1. Shell Interaction Test (shell_interaction)
**Purpose**: Test features requiring real user interaction with command line
**Quantity**: 18 test points
**Execution Method**: Manual execution, using input files to simulate user interaction

**Example**:
```bash
python src/main.py < evaluation/inputs/csv_import_test.in
```

### 2. Unit Test (unit_test)
**Purpose**: Directly call source code functions for verification
**Quantity**: 6 test points
**Execution Method**: Automated execution using pytest

**Example**:
```bash
python -m pytest evaluation/tests/test_weighted_sampling.py::test_score_weighted_lottery -v
```

### 3. File Comparison Test (file_comparison)
**Purpose**: Verify program-generated output files
**Quantity**: 2 test points
**Execution Method**: Compare generated files with expected files after program execution

## Test Data Description

### Standard Test Data
- **employees_5.csv**: 5 employees, for basic functionality testing
- **employees_10.csv**: 10 employees, for statistical functionality testing
- **employees_missing_field.csv**: Missing employee ID field, for error handling verification
- **employees_invalid_format.csv**: Contains format errors, for data validation verification

### Special Test Data
- **employees_score_extreme.csv**: Extreme score differences, for weighted testing
- **employees_multi_dept.csv**: Multi-department distribution, for chi-square test
- **employees_large.csv**: Large number of employees, for performance testing

## Running Tests

### Automated Testing
```bash
# Run all automated tests
python evaluation/run_tests.py

# Run specific unit tests
python -m pytest evaluation/tests/test_weighted_sampling.py -v
python -m pytest evaluation/tests/test_fairness_report.py -v
```

### Manual Interaction Testing
```bash
# Program startup test
python src/main.py < evaluation/inputs/startup_test.in

# CSV import test
python src/main.py < evaluation/inputs/csv_import_test.in

# Full workflow test
python src/main.py < evaluation/inputs/full_workflow_test.in
```

## Test Verification Standards

### Functional Completeness Verification
- ✅ Program starts normally and displays main menu
- ✅ Supports CSV and TXT format employee list import
- ✅ Comprehensive data validation and error handling
- ✅ Accurate statistical information calculation
- ✅ Three weight rules correctly implemented
- ✅ Duplicate winning rules correctly executed
- ✅ A-Res algorithm weighted sampling effective
- ✅ Colorful result display correct
- ✅ Statistical fairness report complete

### User Experience Verification
- ✅ Clear and intuitive interaction interface
- ✅ Friendly and accurate error messages
- ✅ Smooth and coherent operation flow
- ✅ Timely and accurate progress indicators

### Data Accuracy Verification
- ✅ Correct mathematical calculation results
- ✅ Accurate statistical test implementation
- ✅ Standard file format specifications
- ✅ Correct encoding handling

## Test Coverage

| Functional Module | Test Points | Coverage |
|-------------------|-------------|----------|
| Program Startup | 1 | 100% |
| List Management | 8 | 100% |
| Lottery Configuration | 8 | 100% |
| Lottery Execution | 5 | 100% |
| Result Display | 9 | 100% |
| User Experience | 2 | 100% |
| **Total** | **24** | **100%** |

## Test Execution Recommendations

### 1. Environment Preparation
```bash
# Install dependencies
pip install -r src/requirements.txt

# Install test dependencies
pip install pytest
```

### 2. Testing Order
1. First run automated tests to verify core logic
2. Then conduct manual interaction tests to verify user experience
3. Finally perform full workflow testing

### 3. Troubleshooting
- If unit tests fail, check dependency package installation
- If interaction tests are abnormal, check input file format
- If file tests fail, check file permissions

## Quality Standards

### Passing Criteria
- All unit tests pass rate ≥ 95%
- All interaction test functions are reachable
- All file comparison test content matches
- No program crashes or abnormal exits

### Performance Standards
- Program startup time < 3 seconds
- List import time < 5 seconds (within 100 people)
- Lottery execution time < 10 seconds (100 people, 10 prizes)
- Report generation time < 2 seconds

---

**Test Plan Version**: v1.0
**Applicable System Version**: Qingdao District 1 Lottery System v1.0
**Update Date**: August 20, 2025