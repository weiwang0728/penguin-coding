# Family Tree System Automation Test Plan

## Overview

This test plan is based on 55 functional test items defined in `evaluation/metric.json` and generates a complete automated test suite.

## File Structure

```
evaluation/
├── metric.json                    # Function evaluation metrics file (pre-validation removed)
├── detailed_test_plan.json        # Detailed test plan (55 test items)
├── run_tests.py                   # Main test execution script
├── README.md                      # This documentation file
├── test_inputs/                   # Test input file directory
│   ├── test_startup.in            # Program startup test input
│   ├── test_002.in                # Name required field validation test
│   ├── test_003.in                # Gender required field validation test
│   └── ...                        # Other test input files
├── test_data/                     # Test data files
│   └── existing_data.csv          # Existing data for incremental storage tests
├── expected_outputs/              # Expected output files (for file comparison tests)
│   ├── expected_001.csv           # Expected CSV output
│   └── ...                        # Other expected output files
└── tests/                         # Unit test file directory
    ├── test_tree_structure.py     # Tree structure related tests
    ├── test_data_processing.py    # Data processing related tests
    ├── test_file_format.py        # File format related tests
    └── ...                        # Other unit test files
```

## Test Types

### 1. Shell Interaction Tests (shell_interaction)
- Used to test functions that require simulating real user interaction with the command line
- Uses `main_automated.py` and `.in` input files for automated interaction
- Main tests: required field validation, format validation, query functions, etc.

### 2. Unit Tests (unit_test)
- Used to directly call specific functions or classes in the source code for verification
- Executed using the pytest framework
- Main tests: class definitions, data processing, structural consistency, etc.

### 3. File Comparison Tests (file_comparison)
- Used to verify whether the program generates correct output files
- Compares the content of generated files with expected files
- Main tests: CSV file creation, data storage, file format, etc.

## Usage

### Run All Tests
```bash
python evaluation/run_tests.py
```

### Run Single Unit Test
```bash
pytest evaluation/tests/test_tree_structure.py
```

### Run Specific Shell Interaction Test
```bash
python src/main_automated.py evaluation/test_inputs/test_002.in
```

## Test Input File Format

Test input files (.in files) contain command sequences simulating user input, for example:

```
add
Zhang San
Beijing
19900101
0
175.5
Bachelor
Software Engineer
Senior Engineer

0
1
Male
```

## Test Reports

After execution, test results will be saved in:
- `evaluation/test_report.json` - Detailed JSON format test report
- Console output - Real-time test progress and summary

## Notes

1. Ensure that the Python environment has pandas and other dependency libraries installed
2. Data files such as data.csv will be automatically cleaned before testing
3. Some tests may require specific data preparation, please ensure relevant test data files exist
4. If tests fail, please check error information and confirm whether program functions are correctly implemented

## Extending Tests

To add new test items:
1. Add new test metrics in `metric.json`
2. Add corresponding test plan in `detailed_test_plan.json`
3. Create corresponding test input files and expected output files
4. If it's a unit test, create corresponding test file in the `tests/` directory
