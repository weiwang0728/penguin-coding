# Chord DHT Simulation System Test Framework

## Overview

This test framework provides a complete automated testing solution for the Chord DHT simulation system, including interactive tests, unit tests, and file comparison tests.

## Directory Structure

```
evaluation/
├── detailed_test_plan.json          # Detailed test plan
├── additional_unit_tests.json       # Additional unit test definitions
├── inputs/                          # Test input files
│   ├── basic_startup.in
│   ├── m_parameter_config.in
│   ├── nodes_config.in
│   ├── boundary_validation.in
│   ├── network_initialization.in
│   ├── menu_display.in
│   ├── node_add_success.in
│   ├── node_add_duplicate.in
│   ├── data_insert.in
│   ├── data_search_found.in
│   ├── data_search_notfound.in
│   ├── network_info.in
│   ├── node_delete_success.in
│   ├── node_delete_notfound.in
│   ├── network_visualization.in
│   ├── time_statistics.in
│   ├── menu_validation.in
│   ├── node_id_validation.in
│   ├── batch_data_generation.in
│   ├── menu_loop.in
│   └── graceful_exit.in
├── expected_outputs/                # Expected output files
│   └── expected_graph.dot
├── tests/                          # Unit test files
│   ├── __init__.py
│   ├── test_chord_basic.py
│   └── test_data_operations.py
└── README.md                       # This file
```

## Test Categories

### 1. Shell Interaction Tests
This category simulates real user interactions with command-line programs, verifying:
- Program startup and initialization
- Menu system
- User input processing
- Error handling
- Operation feedback

**Execution method:**
```bash
python src/Main.py < evaluation/inputs/test_case.in
```

### 2. Unit Tests
This category directly tests classes and methods in the source code, verifying:
- Node initialization
- Network structure construction
- Hash functions
- Data operations

**Execution method:**
```bash
pytest evaluation/tests/test_chord_basic.py -v
pytest evaluation/tests/test_data_operations.py -v
```

### 3. File Comparison Tests
This category verifies whether program-generated files meet expectations:
- Network topology DOT files
- PNG image files (if supported)

**Execution method:**
```bash
python src/Main.py < evaluation/inputs/network_visualization.in
diff graph.dot evaluation/expected_outputs/expected_graph.dot
```

## Input File Format

Input files contain complete sequences that simulate user input, with each line representing one input:
- Numbers: Menu selections or parameter input
- Text: Data strings or node IDs
- Empty lines: Represent Enter key

Example `node_add_success.in`:
```
4        # m parameter
6        # Node count
0        # Data count
1        # Select menu item 1 (Add node)
20       # New node ID
7        # Select menu item 7 (Exit)
```

## Running All Tests

### Run Unit Tests
```bash
pytest evaluation/tests/ -v
```

### Run Interactive Tests (Examples)
```bash
# Test basic startup
python src/Main.py < evaluation/inputs/basic_startup.in

# Test node addition
python src/Main.py < evaluation/inputs/node_add_success.in

# Test data insertion
python src/Main.py < evaluation/inputs/data_insert.in
```

### Run File Comparison Tests
```bash
# Generate network topology file
python src/Main.py < evaluation/inputs/network_visualization.in

# Compare generated file with expected file
if [ -f "graph.dot" ]; then
    echo "DOT file generated successfully"
    # Can further compare content
    # diff graph.dot evaluation/expected_outputs/expected_graph.dot
else
    echo "DOT file generation failed"
fi
```

## Test Coverage

This test framework covers the following features:

### Basic Functions
- [x] Program startup and welcome screen
- [x] Network parameter configuration (m, node count, data count)
- [x] Boundary condition validation
- [x] Network initialization process display

### Core Functionality
- [x] Dynamic node management (Add/Delete)
- [x] Data insertion and lookup
- [x] Network status information display
- [x] Network topology visualization

### Interactive Functions
- [x] Menu system completeness
- [x] User input validation
- [x] Error handling
- [x] Menu loop execution
- [x] Graceful exit

### Performance Functions
- [x] Operation time statistics
- [x] Batch data generation

## Expected Results

### Success Scenarios
- Program starts normally and displays welcome information
- Parameter configuration succeeds and accepts valid input
- Network is created successfully and displays statistics
- Node and data operations execute successfully
- Correct visualization files are generated

### Error Handling
- Invalid parameter input receives appropriate error messages
- Duplicate operations are handled correctly
- Program does not crash on erroneous input

## Notes

1. **Dependencies**: Ensure required Python packages are installed (see src/requirements.txt)
2. **File Paths**: All tests are designed to run from the project root directory
3. **Graphviz**: Network visualization requires Graphviz to be installed on the system
4. **Parallel Tests**: Some tests may require sufficient system resources

## Troubleshooting

### Common Issues
1. **ModuleNotFoundError**: Check Python path and dependency installation
2. **FileNotFoundError**: Ensure running tests from correct directory
3. **PermissionError**: Check file and directory permissions
4. **Graph generation failure**: Check Graphviz installation and configuration

### Debugging Recommendations
1. Run individual test cases separately
2. Check program standard output and error output
3. Verify input file format is correct
4. Ensure test environment is consistent with development environment
