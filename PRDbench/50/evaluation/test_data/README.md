# Test Data Documentation

This directory contains all independent test data files required for testing, ensuring each test point can run independently without relying on the crawler steps.

## Directory Structure

```
test_data/
├── raw_data/              # Raw crawled data (simulated)
│   ├── music_list.csv
│   └── music_detail.csv
├── cleaned_data/          # Cleaned data
│   ├── cleaned_music_list.csv
│   └── cleaned_music_detail.csv
└── models/                # Pre-trained model files
    └── play_count_prediction_model_detail.pkl
```

## Usage

In the test plan (`detailed_test_plan.json`), each test case that requires data includes data preparation steps at the beginning of the `testcases` array:

1. **Create directories**: `mkdir -p src/music_data src/music_image` or `mkdir -p src/models`
2. **Copy test data**: Copy corresponding test data files from `evaluation/test_data/` directory to target locations
3. **Execute test**: Run the actual test command

### Data Copy Mapping

- `raw_data/music_list.csv` → `src/music_data/music_list.csv`
- `raw_data/music_detail.csv` → `src/music_data/music_detail.csv`
- `cleaned_data/cleaned_music_list.csv` → `src/music_data/cleaned_music_list.csv`
- `cleaned_data/cleaned_music_detail.csv` → `src/music_data/cleaned_music_detail.csv`
- `models/play_count_prediction_model_detail.pkl` → `src/models/play_count_prediction_model_detail.pkl`

## Advantages

This design ensures:
1. **Test Independence**: Each test is independent and does not rely on the execution results of other tests
2. **No Crawler Dependency**: Even if the crawler step fails, other tests can still run normally
3. **Reproducibility**: Test data is fixed, ensuring consistent test results each time
4. **Quick Reset**: Test environment can be quickly reset for debugging and verification
5. **Parallel Testing**: Supports parallel execution of multiple tests without interference


