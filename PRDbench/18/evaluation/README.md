# MatrixAnalysisFinal Testing System

## Overview

This is a complete automated testing system designed for the MatrixAnalysisFinal matrix factorization project, used to verify the correctness of five matrix factorization algorithms, output format compliance, and numerical computation accuracy.

## Project Structure

```
evaluation/
├── detailed_test_plan.json    # Detailed test plan (JSON format)
├── metric.json                # Functional evaluation metrics
├── run_tests.py              # Test execution script
├── README.md                 # This file
└── tests/                    # Test files directory
    ├── test_lu_correctness.py     # LU factorization correctness test
    ├── test_qr_correctness.py     # QR factorization correctness test
    ├── test_hr_correctness.py     # Householder reflection correctness test
    ├── test_gr_correctness.py     # Givens rotation correctness test
    ├── test_urv_correctness.py    # URV factorization correctness test
    ├── test_output_format.py      # Output format compliance test
    └── test_matrix_rank.py        # Matrix rank calculation test
```

## Test Coverage

### 1. Command Line Interface Tests
- **1.1** Display help information when no parameters or invalid parameters
- **1.2** Error handling for invalid model parameters
- **1.3** Error handling for invalid file paths

### 2. Core Algorithm Tests

#### 2.1 LU Factorization
- **2.1a** Correctness of calculation results (P×L×U = A)
- **2.1b** Output format compliance (4 decimal precision)
- **2.1c** Matrix rank calculation correctness

#### 2.2 QR Factorization (Gram-Schmidt)
- **2.2a** Correctness of calculation results (Q×R = A, Q orthogonality)
- **2.2b** Output format compliance
- **2.2c** Matrix rank calculation correctness

#### 2.3 Householder Reflection Factorization
- **2.3a** Correctness of calculation results (Q×R = A, Q orthogonality)
- **2.3b** Output format compliance
- **2.3c** Matrix rank calculation correctness

#### 2.4 Givens Rotation Factorization
- **2.4a** Correctness of calculation results (Q×R = A, Q orthogonality)
- **2.4b** Output format compliance
- **2.4c** Matrix rank calculation correctness

#### 2.5 URV Factorization
- **2.5a** Correctness of calculation results (U×R×V^T = A, U, V orthogonality)
- **2.5b** Output format compliance
- **2.5c** Matrix rank calculation correctness

## Usage

### Run All Tests
```bash
# Method 1: Use test execution script
python evaluation/run_tests.py

# Method 2: Run directly with pytest
pytest evaluation/tests/ -v
```

### Run Specific Tests
```bash
# Run LU factorization correctness test
pytest evaluation/tests/test_lu_correctness.py::test_lu_factorization_correctness -v

# Run all output format tests
pytest evaluation/tests/test_output_format.py -v

# Run all matrix rank calculation tests
pytest evaluation/tests/test_matrix_rank.py -v
```

### Command Line Interface Tests (Manual)
```powershell
# Test help information
cd src; python main.py
cd src; python main.py --unknown-arg

# Test invalid model parameter
cd src; python main.py --model INVALIDMODEL --input data/LU.txt

# Test invalid file path
cd src; python main.py --model LU --input non_existent_file.txt
```

## Test Data

Tests use standard test matrices from the src/data/ directory:
- `LU.txt` - LU factorization test matrix
- `GramSchmidt.txt` - QR factorization test matrix
- `Household.txt` - Householder reflection test matrix
- `Givens.txt` - Givens rotation test matrix
- `URV.txt` - URV factorization test matrix

## Validation Criteria

### Numerical Precision
- Matrix reconstruction error < 1e-10
- Orthogonality verification error < 1e-10
- Matrix rank calculation consistent with numpy.linalg.matrix_rank

### Output Format
- All numerical outputs strictly follow 8.4f format (8 characters width, 4 decimal places)
- Matrix elements displayed aligned

### Matrix Property Verification
- LU factorization: L is lower triangular, U is upper triangular, P is permutation matrix
- QR factorization: Q is orthogonal matrix, R is upper triangular matrix
- URV factorization: U, V are orthogonal matrices

## Dependencies

```bash
pip install pytest numpy
```

## Notes

1. Tests will not modify any source code in the src/ directory
2. All tests directly call existing functions in src/model/
3. Test data uses standard test files in src/data/
4. Test results consider floating-point precision of numerical computations