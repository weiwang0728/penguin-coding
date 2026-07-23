# Evaluation Test Standard and Test Interface Description

## Overview

This directory contains the complete evaluation test standard and automated test interface for the IoT Environmental Data Collection and Intelligent Prediction System, used to objectively, comprehensively, and reproducibly assess the implementation quality of the system.

## File Description

### 1. metric.json
Manual evaluation test standard file, containing 19 scoring items, totaling 100 points.

**Scoring Dimensions:**
- System Basic Functions (25 points)
- MQTT Communication Functions (30 points)
- Data Management Functions (20 points)
- Machine Learning Functions (15 points)
- System Monitoring Functions (5 points)
- User Experience (5 points)

**Scoring Rules:**
- Each scoring item: 0 points (not functional), 1 point (partially functional), 2 points (fully functional)
- Weight values: 1-5 points, reflecting function importance
- Final Score = Σ(Scoring Item Score × Weight Value)

### 2. detailed_test_plan.json
Detailed test plan file, containing complete test case definitions and execution steps.

**Included Content:**
- Test environment requirements
- Pre-test setup steps
- 19 detailed test cases
- Scoring rules and grade mapping
- Test execution instructions

### 3. agent_test_interface.py
Agent automated test interface, providing programmatic test execution capabilities.

**Main Functionality:**
- Automatically execute all test cases
- Command-line operations and file checks
- Data format verification
- Interactive CLI test simulation
- Automatically generate test reports

## Usage

### Manual Evaluation Test

1. Refer to the scoring standard in `metric.json`
2. Test each item according to "Verification Method"
3. Give scores based on "Scoring Range"
4. Calculate weighted total score

### Agent Automated Evaluation Test

```bash
# Run automated test
cd evaluation
python agent_test_interface.py

# View test report
cat test_report.json
```

### Test Individual Functions

```bash
# Test MQTT function
cd ../src
python main.py mqtt publish --random

# Test data analysis
python main.py data analyze

# Test machine learning
python main.py ml train --data-file samples/environmental_sample.csv --epochs 10
python main.py ml predict --temperature 25.0 --humidity 60.0 --pressure 1013.25

# Test system monitoring
python main.py system status

# Test web interface
python main.py web
```

## Evaluation Focus

### 1. User Experience Priority
- Is the CLI interface user-friendly and easy to use
- Are error messages clear and understandable
- Is the operation process intuitive

### 2. Functional Completeness
- Each function point in the PRD should be implemented
- Core business processes are fully functional
- Data processing pipeline is smooth

### 3. System Stability
- Error handling mechanism is sound
- Abnormal situations do not cause crashes
- Log records are detailed and complete

### 4. Technical Specification Compliance
- Data format complies with PRD specification
- Technology stack usage is correct
- Performance indicators are met

## Scoring Standard Explanation

### High-Weight Functions (Weight 4-5)
- **System Start and Help** (Weight 5): Basic function, must be fully functional
- **MQTT Communication** (Weight 4): Core business function
- **Machine Learning Training** (Weight 5): System core value
- **Data Analysis** (Weight 4): Important data processing function

### Medium-Weight Functions (Weight 3)
- **Data Cleaning and Merging**: Data preprocessing function
- **Model Evaluation**: ML auxiliary function
- **System Monitoring**: Operational support function
- **Configuration Management**: System management function

### Low-Weight Functions (Weight 1-2)
- **Log Recording**: Basic support function
- **Error Handling**: System robustness

## Test Execution Recommendations

### 1. Environment Preparation
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Verify installation
python run.py test
```

### 2. Function Test Sequence
1. Basic function test (System start, Help information)
2. Data management test (Analysis, Cleaning, Merging)
3. MQTT communication test (Publishing, Subscription)
4. Machine learning test (Training, Prediction, Evaluation)
5. System monitoring test (Status, Real-time monitoring)
6. Web interface test (Service startup)
7. Configuration management test (Setup wizard)

### 3. Score Calculation
```
Final Score = Σ(Each Scoring Item Score × Its Weight) / Σ(All Weights × 2) × 100
```

### 4. Grade Division
- A Level (90-100 points): Excellent, complete functions, great user experience
- B Level (80-89 points): Good, main functions working
- C Level (70-79 points): Average, basic functions working but with defects
- D Level (60-69 points): Passing, partial functions working
- F Level (0-59 points): Failing, serious function defects

## Notes

1. **Test Environment**: Ensure testing in a clean Python environment
2. **Dependency Installation**: All dependencies must be correctly installed
3. **File Permissions**: Ensure sufficient file read/write permissions
4. **Network Connection**: MQTT function requires network connection (may fail due to lack of configuration, but does not affect basic function score)
5. **Test Data**: Use provided sample data for testing

## Troubleshooting

### Common Issues
1. **ImportError**: Check Python path and module structure
2. **Dependency Missing**: Reinstall packages in requirements.txt
3. **Permission Issues**: Ensure data, logs, models directories have write permissions
4. **MQTT Connection Failure**: Normal phenomenon, due to lack of configured Alibaba Cloud credentials

### Debugging Recommendations
1. View log files in logs directory
2. Use `python run.py test` for basic function verification
3. Test each function module one by one
4. Check configuration file config.yaml settings
