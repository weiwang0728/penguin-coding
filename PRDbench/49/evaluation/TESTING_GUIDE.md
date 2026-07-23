# IoT Environmental Data Collection System - Testing Guide

## Overview

This guide provides a complete testing methodology for assessing the implementation quality of the IoT Environmental Data Collection and Intelligent Prediction System. The testing methodology includes manual evaluation test standards, automated test interface, and detailed test plan.

## File Structure

```
evaluation/
├── metric.json                      # Manual evaluation test standard (19 scoring items)
├── detailed_test_plan.json          # Detailed test plan (structured test cases)
├── agent_test_interface.py          # Agent automated test interface
├── run_tests.py                     # Comprehensive test execution script
├── README.md                        # Evaluation test description file
├── EVALUATION_SUMMARY.md            # Evaluation test summary report
├── TESTING_GUIDE.md                 # This testing guide
├── pytest.ini                      # Pytest configuration file
├── test_environmental_data.csv      # Test environmental data
├── test_data_with_anomalies.csv     # Test data with anomalies
├── setup_inputs.in                  # Configuration wizard input file
├── user_interaction.in              # User interaction input file
├── expected_data_format.csv         # Expected data format file
└── tests/                           # Unit test directory
    ├── __init__.py                  # Test package initialization
    ├── test_data_quality.py         # Data quality control test
    ├── test_error_handling.py       # Error handling test
    ├── test_logging.py              # Logging function test
    └── test_functionality_completeness.py  # Functional completeness test
```

## Test Category Description

### 1. Shell Interaction Tests (shell_interaction)
Used to test functions that need to simulate actual user and command-line interaction.

**Features:**
- Execute complete CLI commands
- Can include standard input simulation
- Verify command output and behavior

**Example:**
```json
{
  "type": "shell_interaction",
  "testcases": [
    {
      "test_command": "cd src && python main.py mqtt publish --random",
      "test_input": null
    }
  ]
}
```

### 2. Unit Tests (unit_test)
Used to verify that specific functions, classes, or modules can be tested directly through interface calls to the source code.

**Features:**
- Directly test source code logic
- Can test boundary conditions
- Provide detailed assertion verification

**Example:**
```json
{
  "type": "unit_test",
  "testcases": [
    {
      "test_command": "python tests/test_data_quality.py",
      "test_input": null
    }
  ]
}
```

### 3. File Comparison Tests (file_comparison)
Used to verify whether the program generates correct output files.

**Features:**
- Verify file generation
- Compare output with expected results
- Check file format and content

**Example:**
```json
{
  "type": "file_comparison",
  "expected_output_files": ["evaluation/expected_data_format.csv"]
}
```

## Usage

### 1. Quick Evaluation Test

```bash
# Use comprehensive test script
cd evaluation
python run_tests.py
```

### 2. Use Agent Automated Test Interface

```bash
# Run agent test interface
cd evaluation
python agent_test_interface.py
```

### 3. Run Individual Unit Tests

```bash
# Test functional completeness
python tests/test_functionality_completeness.py

# Test error handling
python tests/test_error_handling.py

# Test log function
python tests/test_logging.py

# Test data quality
python tests/test_data_quality.py
```

### 4. Manually Test Specific Functions

```bash
# Test MQTT function
cd ../src
python main.py mqtt publish --random
python main.py mqtt subscribe --duration 10

# Test data management
python main.py data analyze
python main.py data clean

# Test machine learning
python main.py ml train --data-file samples/environmental_sample.csv --epochs 10
python main.py ml predict --temperature 25.0 --humidity 60.0 --pressure 1013.25

# Test system monitoring
python main.py system status
python main.py system monitor --duration 15

# Test web interface
python test_web.py  # Then access http://localhost:8080
```

## Scoring Standard

### Scoring Item Weight Distribution
- **Weight 5** (Critical functions): System start, ML training, Functional completeness
- **Weight 4** (Important functions): MQTT communication, Data analysis, System monitoring, Web interface, User experience
- **Weight 3** (Auxiliary functions): Data cleaning, Data merging, Configuration wizard, Data format verification, Error handling
- **Weight 2** (Support functions): Log recording

### Scoring Rules
- **2 points**: Function fully functional, complies with PRD requirements
- **1 point**: Function partially functional, has minor issues but does not affect basic use
- **0 points**: Function not functional or has serious errors

### Total Score Calculation
```
Final Score = Σ(Each Scoring Item Score × Its Weight) / Σ(All Weights × 2) × 100
```

## Test Environment Requirements

### System Requirements
- Python 3.9+
- Operating System: Windows/Linux/macOS
- Memory: ≥4GB
- Storage: ≥1GB available space

### Dependency Package Requirements
```bash
pip install -r requirements.txt
```

Main dependencies:
- pyyaml, pandas, numpy, scikit-learn
- torch, matplotlib, seaborn
- psutil, click, rich
- paho-mqtt, flask, tqdm

## Test Execution Process

### 1. Environment Preparation
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Verify basic functions
python run.py test
```

### 2. Execute Evaluation Test
```bash
# Method 1: Use comprehensive test script
cd evaluation
python run_tests.py

# Method 2: Use agent interface
python agent_test_interface.py

# Method 3: Manually test one by one
# Refer to verification method in metric.json
```

### 3. View Results
```bash
# View test report
cat test_execution_results.json

# View evaluation test summary
cat EVALUATION_SUMMARY.md
```

## Common Issues and Solutions

### 1. MQTT Connection Failure
**Phenomenon**: MQTT publishing/subscription function reports connection error
**Cause**: Alibaba Cloud IoT platform credentials not configured
**Solution**: This is normal, does not affect function score. System will show connection attempt and error handling.

### 2. Model Training Failure
**Phenomenon**: ML training command execution fails
**Cause**: Could be data file path or format issue
**Solution**: Check if environmental_sample.csv file exists in samples directory

### 3. Web Interface Inaccessible
**Phenomenon**: Web service cannot be accessed after startup
**Solution**:
```bash
cd src
python test_web.py  # Use test version web interface
```

### 4. Data Merging Failure
**Phenomenon**: data merge command fails
**Cause**: Missing separate sensor data files
**Solution**: Run data publishing command first to generate test data

### 5. Unit Test Import Error
**Phenomenon**: Test file cannot import module
**Solution**: Ensure running test from evaluation directory, Python path will be set automatically

## Test Results Interpretation

### Success Rate Grades
- **90-100%**: A Level - Excellent implementation
- **80-89%**: B Level - Good implementation
- **70-79%**: C Level - Average implementation
- **60-69%**: D Level - Passing implementation
- **<60%**: F Level - Failing

### Key Indicators
1. **System Start Success Rate**: Must be 100%
2. **Core Function Availability**: Should be ≥80%
3. **User Experience Quality**: Should be ≥75%
4. **Error Handling Completeness**: Should be ≥70%

## Testing Best Practices

### 1. Test Sequence
1. Basic function test (System start, Help information)
2. Core business function test (MQTT, Data management, ML)
3. System support function test (Monitoring, Log, Configuration)
4. User experience test (Interface friendliness, Error handling)

### 2. Test Data Preparation
- Use provided test data files
- Ensure data format complies with PRD specification
- Include normal data and anomalous data

### 3. Result Verification
- Check command execution status
- Verify output content completeness
- Confirm log recording correctness
- Test error handling mechanism

### 4. Report Generation
- Record detailed test process
- Count success/failure rates
- Provide improvement recommendations
- Generate scoring report

## Test Extension

### Add New Test Cases
1. Add new scoring items in `metric.json`
2. Add corresponding test cases in `detailed_test_plan.json`
3. Create corresponding unit test files if needed
4. Update test documentation

### Custom Test Scripts
You can create custom test scripts based on `agent_test_interface.py`, suitable for specific testing needs.

## Contact and Support

For test-related issues, please refer to:
1. Project main documentation: `../README.md`
2. Detailed usage documentation: `../src/docs/README.md`
3. Product requirements document: `../src/docs/PRD.md`

The testing methodology ensures objective, comprehensive, and reproducible assessment of system implementation quality.
