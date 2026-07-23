# Logistics Center Site Selection System Test Plan

## Overview
This test plan provides a complete automated testing framework for the logistics center site selection system, including functional tests, unit tests, and file comparison tests.

## File Structure
```
evaluation/
├── metric.json                    # Scoring criteria definition
├── detailed_test_plan.json       # Detailed test plan
├── expected_cluster_points.xlsx  # Expected clustering result file (golden standard)
├── pytest.ini                    # pytest configuration file
├── tests/                         # Unit test directory
│   ├── __init__.py
│   ├── test_centroid_coordinates.py    # Centroid coordinate tests
│   ├── test_cluster_coordinates.py     # Cluster coordinate tests
│   ├── test_code_analysis.py           # Code analysis tests
│   └── test_consistency.py             # Consistency tests
└── README.md                      # This file
```

## Test Type Description

### 1. Shell Interaction Tests
Execute Python scripts directly and verify console output and chart display:
- Environment dependency check
- Excel file reading
- Data validation
- Algorithm execution and visualization
- System stability

### 2. Unit Tests
Use pytest framework for unit testing:
- Centroid coordinate rationality verification
- Cluster center coordinate verification
- Code implementation check
- Result consistency testing

### 3. File Comparison Tests
Verify consistency between generated files and expected files:
- Excel file generation verification

## Running Tests

### Prerequisites
1. Ensure the following files exist in AHAU-logistics-GM/src directory:
   - mdl4.xlsx
   - AfterClustering.xlsx
   - HarmonyOS_Sans_SC_Black.ttf
   - SingleCentroidMethod.py
   - ClusteringAlgorithm.py
   - SilhouetteCoefficient.py

2. Install dependencies:
   ```bash
   pip install pandas numpy scikit-learn matplotlib openpyxl pytest
   ```

### Run All Unit Tests
```bash
cd evaluation
pytest tests/ -v
```

### Run Specific Tests
```bash
# Test centroid coordinates
pytest tests/test_centroid_coordinates.py::test_centroid_in_anhui_range -v

# Test cluster coordinates
pytest tests/test_cluster_coordinates.py::test_cluster_centers_in_anhui_range -v

# Test code analysis
pytest tests/test_code_analysis.py::test_standard_scaler_usage -v
pytest tests/test_code_analysis.py::test_weight_normalization -v

# Test consistency
pytest tests/test_consistency.py::test_centroid_consistency -v
```

### Manually Execute Shell Interaction Tests
```bash
cd src

# Test environment dependencies
python -c "import pandas, numpy, sklearn, matplotlib, openpyxl; print('All dependencies imported successfully')"

# Test Excel file reading
python -c "import pandas as pd; data1=pd.read_excel('mdl4.xlsx'); data2=pd.read_excel('AfterClustering.xlsx'); print(f'mdl4 data rows: {len(data1)}, columns: {len(data1.columns)}'); print(f'clustered data rows: {len(data2)}, columns: {len(data2.columns)}')"

# Run algorithm scripts
python SilhouetteCoefficient.py
python ClusteringAlgorithm.py
python SingleCentroidMethod.py
```

## Scoring Criteria
Each test point has corresponding scoring criteria (0-2 points) and weight (1-5 points). For detailed scoring rules, please refer to the `metric.json` file.

## Notes
1. Ensure all required data files exist before running tests
2. Chart display tests require a matplotlib GUI environment
3. Chinese font tests require proper font file support
4. Some tests may require closing chart windows before continuing execution