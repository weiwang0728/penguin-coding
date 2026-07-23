# Matrix Decomposition Toolkit

## Requirement Overview

Develop a matrix decomposition toolkit that supports invoking multiple matrix decomposition algorithms via the command line, achieving the following core capabilities:

- Modular design: Separation of algorithm implementation, data management, and utility functions
- Algorithm coverage: Supports 5 matrix decomposition methods
- Flexible invocation: Specify the algorithm and data source via command line arguments
- Testability: Each algorithm can independently verify correctness

## Core Features

### 2.1 Matrix Decomposition Computation Service

Supports 5 decomposition algorithms:
- LU: LU decomposition
- QR: QR decomposition based on Gram-Schmidt
- HR: Orthogonal reduction based on Householder Reduction
- GR: Orthogonal reduction based on Givens Reduction
- URV: URV decomposition

### 2.2 Data Management Functionality

- Read matrix data from TXT files (space-separated format)
- Default data storage path management

### 2.3 Auxiliary Computation Functionality

- Formatted matrix output (consistent decimal precision)
- Simultaneous support for matrix rank calculation

## Interface Specification

### Command-line invocation format:

```
python main.py [--model ALGORITHM] [--input FILE_PATH]
```

- `--model`: Specify the decomposition algorithm (optional values: LU, QR, HR, GR, URV)
- `--input`: Specify matrix data file path

## Non-functional Requirements

- Scalability: Adding new algorithms does not affect existing invocation interfaces
- Robustness: Return usage instructions for invalid parameters; give clear error messages for file exceptions