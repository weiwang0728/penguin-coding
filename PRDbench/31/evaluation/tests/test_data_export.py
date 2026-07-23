"""
Data Export Functional Test
"""
import pytest
import sys
import pandas as pd
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_manager import DataManager
from scale_manager import ScaleManager
from models import create_tables

@pytest.fixture
def setup_export_test():
    """Set up data export test environment"""
    create_tables()

    scale_manager = ScaleManager()
    data_manager = DataManager()

    # Create default scales
    scale_manager.create_default_scales()

    # Create test data
    participants_data = [
        {'participant_id': 'EXPORT_001', 'name': 'Export Test 1', 'gender': 'Male', 'age': 20, 'grade': 'Sophomore', 'major': 'Psychology'},
        {'participant_id': 'EXPORT_002', 'name': 'Export Test 2', 'gender': 'Female', 'age': 19, 'grade': 'Freshman', 'major': 'Education'},
        {'participant_id': 'EXPORT_003', 'name': 'Export Test 3', 'gender': 'Male', 'age': 21, 'grade': 'Junior', 'major': 'Psychology'},
    ]

    for p_data in participants_data:
        data_manager.create_participant(**p_data)

    # Create questionnaire responses
    responses_data = [
        {'participant_id': 'EXPORT_001', 'scale_id': 1, 'responses_data': {str(i): i % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'EXPORT_002', 'scale_id': 1, 'responses_data': {str(i): (i + 2) % 5 + 3 for i in range(1, 9)}},
        {'participant_id': 'EXPORT_003', 'scale_id': 1, 'responses_data': {str(i): (i + 4) % 5 + 3 for i in range(1, 9)}},
    ]

    for r_data in responses_data:
        data_manager.create_response(**r_data)

    return data_manager, scale_manager

def test_export_data_csv(setup_export_test):
    """Test export data in CSV format"""
    data_manager, scale_manager = setup_export_test

    # Export participant data
    participants_file = Path("evaluation/temp_exported_participants.csv")
    success = data_manager.export_participants_to_csv(participants_file)

    try:
        # Assert
        assert success == True, "Participant data CSV export failed"
        assert participants_file.exists(), "Participant CSV file does not exist"

        # Verify CSV content
        df = pd.read_csv(participants_file)
        assert len(df) >= 3, f"Exported participant quantity insufficient, expected at least 3, actual: {len(df)}"

        # Verify required columns
        required_columns = ['participant_id', 'name', 'gender', 'age', 'grade', 'major']
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"

        # Verify data content
        assert 'EXPORT_001' in df['participant_id'].values, "Missing test participant EXPORT_001"
        assert 'Export Test 1' in df['name'].values, "Missing test participant name"

    finally:
        # Clean up file
        if participants_file.exists():
            participants_file.unlink()

    # Export questionnaire response data
    responses_file = Path("evaluation/temp_exported_responses.csv")
    success = data_manager.export_responses_to_csv(responses_file, scale_id=1)

    try:
        # Assert
        assert success == True, "Questionnaire response data CSV export failed"
        assert responses_file.exists(), "Questionnaire response CSV file does not exist"

        # Verify CSV content
        df = pd.read_csv(responses_file)
        assert len(df) >= 3, f"Exported response quantity insufficient, expected at least 3, actual: {len(df)}"

        # Verify required columns
        required_columns = ['participant_id', 'total_score', 'completed_at']
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"

        # Verify item columns
        item_columns = [col for col in df.columns if col.startswith('item_')]
        assert len(item_columns) >= 8, f"Item column quantity insufficient, expected at least 8, actual: {len(item_columns)}"

        # Verify data content
        assert 'EXPORT_001' in df['participant_id'].values, "Missing test participant's response"

        # Verify total score calculation
        for _, row in df.iterrows():
            assert pd.notna(row['total_score']), "Total score should not be empty"
            assert isinstance(row['total_score'], (int, float)), "Total score should be numeric type"
            assert 1 <= row['total_score'] <= 7, f"Total score out of reasonable range: {row['total_score']}"

    finally:
        # Clean up file
        if responses_file.exists():
            responses_file.unlink()

def test_export_data_excel(setup_export_test):
    """Test export data in Excel format"""
    data_manager, scale_manager = setup_export_test

    # Export participant data to Excel
    participants_file = Path("evaluation/temp_exported_participants.xlsx")
    success = data_manager.export_participants_to_excel(participants_file)

    try:
        # Assert
        assert success == True, "Participant data Excel export failed"
        assert participants_file.exists(), "Participant Excel file does not exist"

        # Verify Excel content
        df = pd.read_excel(participants_file)
        assert len(df) >= 3, f"Exported participant quantity insufficient, expected at least 3, actual: {len(df)}"

        # Verify required columns
        required_columns = ['participant_id', 'name', 'gender', 'age', 'grade', 'major']
        for col in required_columns:
            assert col in df.columns, f"Missing required column: {col}"

        # Verify data types
        assert df['age'].dtype in ['int64', 'float64'], "Age column should be numeric type"
        assert df['participant_id'].dtype == 'object', "Participant ID column should be string type"

    finally:
        # Clean up file
        if participants_file.exists():
            participants_file.unlink()

    # Export questionnaire response data to Excel
    responses_file = Path("evaluation/temp_exported_responses.xlsx")
    success = data_manager.export_responses_to_excel(responses_file, scale_id=1)

    try:
        # Assert
        assert success == True, "Questionnaire response data Excel export failed"
        assert responses_file.exists(), "Questionnaire response Excel file does not exist"

        # Verify Excel content
        df = pd.read_excel(responses_file)
        assert len(df) >= 3, f"Exported response quantity insufficient, expected at least 3, actual: {len(df)}"

        # Verify data types
        assert df['total_score'].dtype in ['int64', 'float64'], "Total score column should be numeric type"

        # Verify item data types
        item_columns = [col for col in df.columns if col.startswith('item_')]
        for col in item_columns:
            assert df[col].dtype in ['int64', 'float64'], f"Item column {col} should be numeric type"

    finally:
        # Clean up file
        if responses_file.exists():
            responses_file.unlink()

def test_export_analysis_results(setup_export_test):
    """Test export analysis results"""
    data_manager, scale_manager = setup_export_test

    # Perform descriptive statistical analysis
    from statistical_analysis import StatisticalAnalyzer
    analyzer = StatisticalAnalyzer()

    descriptive_results = analyzer.descriptive_statistics(scale_id=1)

    # Export descriptive statistical results
    desc_file = Path("evaluation/temp_descriptive_results.csv")
    success = data_manager.export_analysis_results_to_csv(descriptive_results, desc_file)

    try:
        # Assert
        assert success == True, "Descriptive statistical result CSV export failed"
        assert desc_file.exists(), "Descriptive statistical result file does not exist"

        # Verify file content
        df = pd.read_csv(desc_file)
        assert len(df) > 0, "Descriptive statistical result file is empty"

        # Verify statistical metric columns
        expected_columns = ['metric', 'value']
        for col in expected_columns:
            assert col in df.columns, f"Missing required column: {col}"

        # Verify statistical metric content
        metrics = df['metric'].values
        expected_metrics = ['count', 'mean', 'std', 'min', 'max']
        for metric in expected_metrics:
            assert any(metric in m for m in metrics), f"Missing statistical metric: {metric}"

    finally:
        # Clean up file
        if desc_file.exists():
            desc_file.unlink()

def test_export_with_filters(setup_export_test):
    """Test data export with filter conditions"""
    data_manager, scale_manager = setup_export_test

    # Filter export by gender
    male_file = Path("evaluation/temp_male_participants.csv")
    success = data_manager.export_participants_to_csv(male_file, filters={'gender': 'Male'})

    try:
        # Assert
        assert success == True, "Export by gender filter failed"
        assert male_file.exists(), "Filter export file does not exist"

        # Verify filter result
        df = pd.read_csv(male_file)
        assert len(df) >= 2, f"Male participant quantity insufficient, expected at least 2, actual: {len(df)}"
        assert all(df['gender'] == 'Male'), "Filter result contains non-male participants"

    finally:
        # Clean up file
        if male_file.exists():
            male_file.unlink()

    # Filter export by grade
    grade_file = Path("evaluation/temp_grade_participants.csv")
    success = data_manager.export_participants_to_csv(grade_file, filters={'grade': 'Sophomore'})

    try:
        # Assert
        assert success == True, "Export by grade filter failed"
        assert grade_file.exists(), "Grade filter export file does not exist"

        # Verify filter result
        df = pd.read_csv(grade_file)
        assert len(df) >= 1, f"Sophomore participant quantity insufficient, expected at least 1, actual: {len(df)}"
        assert all(df['grade'] == 'Sophomore'), "Filter result contains non-sophomore participants"

    finally:
        # Clean up file
        if grade_file.exists():
            grade_file.unlink()

def test_export_with_custom_columns(setup_export_test):
    """Test data export with custom columns"""
    data_manager, scale_manager = setup_export_test

    # Specify export columns
    custom_columns = ['participant_id', 'name', 'gender', 'age']
    custom_file = Path("evaluation/temp_custom_participants.csv")

    success = data_manager.export_participants_to_csv(custom_file, columns=custom_columns)

    try:
        # Assert
        assert success == True, "Custom column export failed"
        assert custom_file.exists(), "Custom column export file does not exist"

        # Verify columns
        df = pd.read_csv(custom_file)
        assert list(df.columns) == custom_columns, f"Export columns do not match, expected: {custom_columns}, actual: {list(df.columns)}"
        assert len(df) >= 3, "Export data row count insufficient"

        # Verify unspecified columns not included
        assert 'grade' not in df.columns, "Should not include unspecified grade column"
        assert 'major' not in df.columns, "Should not include unspecified major column"

    finally:
        # Clean up file
        if custom_file.exists():
            custom_file.unlink()

def test_export_data_integrity(setup_export_test):
    """Test export data integrity"""
    data_manager, scale_manager = setup_export_test

    # Get original data
    original_participants = data_manager.list_participants()
    original_responses = data_manager.list_responses(scale_id=1)

    # Export data
    participants_file = Path("evaluation/temp_integrity_participants.csv")
    responses_file = Path("evaluation/temp_integrity_responses.csv")

    success1 = data_manager.export_participants_to_csv(participants_file)
    success2 = data_manager.export_responses_to_csv(responses_file, scale_id=1)

    try:
        # Assert export success
        assert success1 == True, "Participant data export failed"
        assert success2 == True, "Questionnaire response data export failed"

        # Verify data integrity
        exported_participants = pd.read_csv(participants_file)
        exported_responses = pd.read_csv(responses_file)

        # Verify quantity consistency
        assert len(exported_participants) == len(original_participants), "Exported participant quantity inconsistent with original data"
        assert len(exported_responses) == len(original_responses), "Exported response quantity inconsistent with original data"

        # Verify ID consistency
        original_participant_ids = {p.participant_id for p in original_participants}
        exported_participant_ids = set(exported_participants['participant_id'].values)
        assert original_participant_ids == exported_participant_ids, "Exported participant IDs inconsistent with original data"

        # Verify data value consistency (sampling check)
        for _, row in exported_participants.iterrows():
            original_participant = next((p for p in original_participants if p.participant_id == row['participant_id']), None)
            assert original_participant is not None, f"Cannot find original participant: {row['participant_id']}"
            assert original_participant.name == row['name'], "Participant name inconsistent"
            assert original_participant.gender == row['gender'], "Participant gender inconsistent"
            assert original_participant.age == row['age'], "Participant age inconsistent"

    finally:
        # Clean up files
        if participants_file.exists():
            participants_file.unlink()
        if responses_file.exists():
            responses_file.unlink()

def test_export_error_handling(setup_export_test):
    """Test export error handling"""
    data_manager, scale_manager = setup_export_test

    # Test export to invalid path
    invalid_path = Path("/invalid/path/test.csv")
    success = data_manager.export_participants_to_csv(invalid_path)
    assert success == False, "Export to invalid path should fail"

    # Test export non-existent scale data
    nonexistent_file = Path("evaluation/temp_nonexistent.csv")
    success = data_manager.export_responses_to_csv(nonexistent_file, scale_id=999)
    assert success == False, "Export non-existent scale data should fail"

    # Test empty data export
    empty_scale = scale_manager.create_scale(name="Empty Scale", description="No data")
    empty_file = Path("evaluation/temp_empty.csv")

    try:
        success = data_manager.export_responses_to_csv(empty_file, scale_id=empty_scale.id)
        # Empty data export may succeed but file should only contain header
        if success and empty_file.exists():
            df = pd.read_csv(empty_file)
            assert len(df) == 0, "Empty data export should only contain header"
    finally:
        if empty_file.exists():
            empty_file.unlink()

def test_export_large_dataset(setup_export_test):
    """Test large dataset export performance"""
    data_manager, scale_manager = setup_export_test

    # Create large test data
    import time

    # Record start time
    start_time = time.time()

    # Create 100 participants (simulate large dataset)
    for i in range(100):
        data_manager.create_participant(
            participant_id=f'LARGE_{i:03d}',
            name=f'Large Data Test {i}',
            gender='Male' if i % 2 == 0 else 'Female',
            age=18 + (i % 10),
            grade=f'Year {(i % 4) + 1}',
            major='Psychology' if i % 3 == 0 else 'Education'
        )

        # Create response for each participant
        responses_data = {str(j): (i + j) % 5 + 3 for j in range(1, 9)}
        data_manager.create_response(f'LARGE_{i:03d}', 1, responses_data)

    # Export large dataset
    large_file = Path("evaluation/temp_large_dataset.csv")

    try:
        export_start = time.time()
        success = data_manager.export_responses_to_csv(large_file, scale_id=1)
        export_time = time.time() - export_start

        # Assert
        assert success == True, "Large dataset export failed"
        assert large_file.exists(), "Large dataset export file does not exist"

        # Verify export content
        df = pd.read_csv(large_file)
        assert len(df) >= 103, f"Large dataset export quantity insufficient, expected at least 103, actual: {len(df)}"  # Original 3 + new 100

        # Performance assertion (export time should be within reasonable range)
        assert export_time < 30, f"Large dataset export time too long: {export_time} seconds"

        # Verify file size is reasonable
        file_size = large_file.stat().st_size
        assert file_size > 1000, f"Export file size abnormally small: {file_size} bytes"

    finally:
        # Clean up file
        if large_file.exists():
            large_file.unlink()

        total_time = time.time() - start_time
        print(f"Large dataset test total time: {total_time:.2f} seconds")

def test_export_data_formats(setup_export_test):
    """Test multiple data format export"""
    data_manager, scale_manager = setup_export_test

    # Test supported formats
    formats = [
        ('csv', 'temp_format_test.csv'),
        ('xlsx', 'temp_format_test.xlsx'),
        ('json', 'temp_format_test.json')
    ]

    for format_name, filename in formats:
        file_path = Path(f"evaluation/{filename}")

        try:
            # Call corresponding export method based on format
            if format_name == 'csv':
                success = data_manager.export_participants_to_csv(file_path)
            elif format_name == 'xlsx':
                success = data_manager.export_participants_to_excel(file_path)
            elif format_name == 'json':
                success = data_manager.export_participants_to_json(file_path)

            # Assert
            assert success == True, f"{format_name} format export failed"
            assert file_path.exists(), f"{format_name} format export file does not exist"

            # Verify file size
            file_size = file_path.stat().st_size
            assert file_size > 0, f"{format_name} format export file is empty"

            # Verify file content (basic check)
            if format_name == 'json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    assert isinstance(data, (list, dict)), "JSON format data structure incorrect"
                    if isinstance(data, list):
                        assert len(data) >= 3, "JSON data quantity insufficient"

        finally:
            # Clean up file
            if file_path.exists():
                file_path.unlink()
