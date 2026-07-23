# Test Plan Documentation

## Overview

This directory contains the complete test plan for the College Student Self-Control and Attention Stability Intelligent Analysis System, generated based on the functional evaluation metrics defined in `evaluation/metric.json`.

## File Structure

```
evaluation/
├── README.md                           # This documentation
├── metric.json                         # Functional evaluation metrics (input)
├── detailed_test_plan.json            # Detailed test plan (output)
├── pytest.ini                         # pytest configuration file
├── run_tests.py                       # Test execution script
│
├── tests/                             # Automated test script directory
│   ├── test_scale_creation.py         # Scale creation functional test
│   ├── test_scale_import_export.py    # Scale import/export test
│   ├── test_statistical_analysis.py   # Statistical analysis functional test
│   ├── test_data_management.py        # Data management functional test
│   ├── test_visualization.py          # Visualization functional test
│   └── test_data_export.py           # Data export functional test
│
├── Test Input Files/
│   ├── test_scale.csv                 # Test scale CSV file
│   ├── test_scale.json                # Test scale JSON file
│   ├── test_participants.csv          # Test participant information
│   ├── test_responses.csv             # Test questionnaire responses
│   └── test_responses_with_anomalies.csv  # Test data with anomalies
│
└── Expected Output Files/
    ├── expected_scale_export.csv      # Expected scale export CSV
    ├── expected_scale_export.json     # Expected scale export JSON
    ├── expected_comprehensive_report.html  # Expected comprehensive report
    └── expected_chart.txt             # Expected chart file placeholder
```

## Test Types

### 1. Shell Interaction Test (shell_interaction)
- **Purpose**: Test command-line interface user interaction functions
- **Characteristics**: Simulate real user operations, verify CLI commands and interaction flows
- **Examples**: Program start, help information display, module entry verification

### 2. Unit Test (unit_test)
- **Purpose**: Test specific functions or class functionality
- **Characteristics**: Directly call source code, verify internal logic
- **Examples**: Scale creation, statistical analysis algorithms, data processing functions

### 3. File Comparison Test (file_comparison)
- **Purpose**: Verify program-generated output files
- **Characteristics**: Compare actual output with expected output for consistency
- **Examples**: Scale export, report generation, chart creation

## Quick Start

### Environment Setup

1. **Install dependencies**:
   ```bash
   pip install -r src/requirements.txt
   ```

2. **Activate virtual environment** (if using):
   ```bash
   # Windows
   path\to\venv\Scripts\activate

   # Linux/Mac
   source path/to/venv/bin/activate
   ```

### Run Tests

1. **Run complete test suite**:
   ```bash
   python evaluation/run_tests.py
   ```

2. **Run specific types of tests**:
   ```bash
   # Run only unit tests
   cd evaluation
   pytest tests/ -v

   # Run specific test file
   pytest tests/test_scale_creation.py -v

   # Run specific test function
   pytest tests/test_scale_creation.py::test_create_scale_basic_info -v
   ```

3. **Run shell interaction tests**:
   ```bash
   # Program start test
   python src/main.py --help

   # System initialization
   python src/main.py init

   # View scale list
   python src/main.py scales list

   # Data summary
   python src/main.py data summary
   ```

## Test Coverage

### Functional Module Coverage

| Module | Test File | Covered Functions |
|------|----------|----------|
| Scale Management | test_scale_creation.py<br>test_scale_import_export.py | Scale creation, import/export, verification |
| Data Management | test_data_management.py | Participant management, data import, anomaly detection |
| Statistical Analysis | test_statistical_analysis.py | Descriptive statistics, reliability/validity, factor analysis, regression analysis |
| Visualization | test_visualization.py | Chart generation, format export, interactive dashboard |
| Data Export | test_data_export.py | Multi-format export, data integrity verification |

### Evaluation Metrics Coverage

According to the 29 evaluation points in `metric.json`, the test plan provides complete coverage:

- **0.1**: Program start and main menu ✅
- **1.1-1.4**: Module entry point verification ✅
- **2.1.1a-2.1.4b**: Scale management functions ✅
- **2.2.1a-2.2.3**: Data collection and management ✅
- **2.3.1-2.3.3**: Basic statistical analysis ✅
- **2.4.1a-2.4.3b**: Advanced analysis functions ✅
- **2.5.1-2.5.2e**: Report generation and export ✅

## Test Results Interpretation

### Success Indicators
- ✅ **PASSED**: Test passed, function normal
- 🎉 **ALL PASSED**: All tests passed

### Failure Indicators
- ❌ **FAILED**: Test failed, needs fixing
- ⚠️ **WARNING**: Warning present, check recommended
- ⏰ **TIMEOUT**: Execution timeout, possible performance issue

### Test Reports
After test completion, the following files are generated:
- `test_results.xml`: JUnit format test results
- `TEST_REPORT.md`: Detailed test report

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   ```
   Solution: Check Python path and dependency installation
   pip install -r src/requirements.txt
   ```

2. **Database connection error**
   ```
   Solution: Run system initialization
   python src/main.py init
   ```

3. **File permission error**
   ```
   Solution: Check directory write permissions, or run as administrator
   ```

4. **Test timeout**
   ```
   Solution: Check system resources, or increase timeout duration
   ```

### Debugging Tips

1. **Verbose output**:
   ```bash
   pytest tests/ -v -s
   ```

2. **Run only failed tests**:
   ```bash
   pytest tests/ --lf
   ```

3. **Stop at first failure**:
   ```bash
   pytest tests/ -x
   ```

4. **Generate coverage report**:
   ```bash
   pytest tests/ --cov=src --cov-report=html
   ```

## Extending Tests

### Adding New Tests

1. **Create test file**:
   ```python
   # evaluation/tests/test_new_feature.py
   import pytest

   def test_new_functionality():
       # Test code
       assert True
   ```

2. **Update test plan**:
   Add new test entry in `detailed_test_plan.json`

3. **Run new tests**:
   ```bash
   pytest tests/test_new_feature.py -v
   ```

### Performance Testing

```python
import time

def test_performance():
    start_time = time.time()
    # Execute function
    execution_time = time.time() - start_time
    assert execution_time < 5.0  # Complete within 5 seconds
```

### Stress Testing

```python
def test_large_dataset():
    # Create large amount of data
    for i in range(1000):
        # Execute operation
        pass
    # Verify results
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r src/requirements.txt
    - name: Run tests
      run: python evaluation/run_tests.py
```

## Contribution Guidelines

1. **Add tests**: Write corresponding test cases for new functions
2. **Update documentation**: Synchronize test documentation when modifying functions
3. **Follow conventions**: Use unified test naming and structure
4. **Verify completeness**: Ensure tests cover all critical paths

## Contact Information

For test-related issues, please:
1. Review test output and error information
2. Refer to the troubleshooting section of this document
3. Check the relevant implementation in source code
4. Submit an issue or contact the development team

---

*This test plan is designed based on Software Quality Assurance (QA) best practices to ensure the reliability and stability of system functionality.*