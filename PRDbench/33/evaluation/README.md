# Federated Learning System Test Plan

This directory contains the complete test plan for the federated learning training system, based on the function evaluation metrics defined in `evaluation/metric.json`.

## File Structure

```
evaluation/
├── detailed_test_plan.json     # Detailed test plan (main artifact)
├── run_tests.py               # Test run script
├── README.md                  # This documentation file
├── tests/                     # Unit test directory
│   ├── __init__.py
│   ├── test_interrupt_handling.py
│   ├── test_error_handling.py
│   ├── test_log_content.py
│   ├── test_online_fl.py
│   └── test_file_naming.py
├── *.in                       # Input files (for shell interaction tests)
├── expected_*.log             # Expected output files (for file comparison tests)
└── expected_result_file.txt   # Expected result file
```

## Test Type Description

### 1. Shell Interaction Test
- **Purpose**: Test functions that require real user interaction with the command line
- **Execution Method**: Start the program via `python main.py`, using predefined input files to simulate user interaction
- **Input Files**: `*.in` files contain simulated user input sequences

### 2. Unit Test
- **Purpose**: Test functions that can be verified by directly calling source code functions
- **Execution Method**: Run test files using the pytest framework
- **Test Files**: `tests/test_*.py` files

### 3. File Comparison Test
- **Purpose**: Verify whether the program generates correct output files
- **Execution Method**: Run the program to generate files, then compare with expected files
- **Expected Files**: `expected_*.log` and `expected_*.txt` files

## Running Tests

### Method 1: Run All Tests
```bash
cd evaluation
python run_tests.py
```

### Method 2: Run Single Test Type
```bash
# Run unit tests
pytest tests/

# Run specific test file
pytest tests/test_interrupt_handling.py

# Run specific test function
pytest tests/test_interrupt_handling.py::test_ctrl_c_interrupt
```

### Method 3: Manually Run Shell Interaction Tests
```bash
# Run program using input file
python main.py < evaluation/main_menu_display.in
```

## Test Coverage

This test plan covers all 33 evaluation metrics defined in `metric.json`:

### 1. Program Startup and Menu System (3 tests)
- 1.1 Program startup and main menu display
- 1.2a Menu input validation - invalid number handling
- 1.2b Menu input validation - non-numeric character handling

### 2. Offline Federated Learning (15 tests)
- 2.1a-e Menu accessibility and parameter configuration
- 2.2a-b Training mode selection
- 2.3a-b Progress display
- 2.4 Interrupt support
- 2.5a-b Status return
- 2.6a-b Log generation

### 3. Online Federated Learning (5 tests)
- 3.1a-c Menu accessibility and configuration
- 3.2a-b Connection status display

### 4. Parameter Sweep Experiment (4 tests)
- 4.1a-b Menu accessibility and one-click execution
- 4.2a-b Log file generation and naming
- 4.3 Status query

### 5. Log Viewing and Model Evaluation (4 tests)
- 5.1a-c Log viewing functions
- 5.2a-b Model evaluation functions

### 6. Result Saving and Display (2 tests)
- 6.1a-b Result file saving
- 6.2 Text-based table display

### 7. Program Exit (1 test)
- 7.1 Program normal exit

## Input File Description

Each `.in` file contains a sequence of simulated user inputs for testing specific functions:

- `main_menu_display.in`: Test main menu display (input 6 to exit)
- `invalid_number_input.in`: Test invalid number input handling
- `offline_fl_*.in`: Test various offline federated learning functions
- `online_fl_*.in`: Test online federated learning functions
- `param_sweep_*.in`: Test parameter sweep experiment functions
- etc...

## Expected Output File Description

- `expected_training_log.log`: Expected training log format
- `expected_result_*.log`: Expected parameter sweep experiment logs
- `expected_result_file.txt`: Expected result file format

## Notes

1. **Dependencies**: Ensure pytest and other necessary dependencies are installed
2. **Main Program**: Tests depend on the `main.py` file in the project root directory
3. **Timeout Settings**: Tests are configured with reasonable timeout values to avoid long waits
4. **Resource Cleanup**: Tests automatically clean up temporary files and processes
5. **Concurrency Issues**: Some tests may involve network ports, be careful to avoid conflicts

## Extending Tests

To add new test cases:

1. Add new test definition in `detailed_test_plan.json`
2. Create corresponding input file (if shell_interaction type)
3. Create corresponding test file (if unit_test type)
4. Create expected output file (if file_comparison type)
5. Run `python run_tests.py` to verify the new test

## Troubleshooting

If tests fail, please check:

1. Whether the main program `main.py` exists and is executable
2. Whether the input file format is correct
3. Whether dependency packages are installed
4. Whether file permissions are correct
5. Whether ports are occupied (for network-related tests)
