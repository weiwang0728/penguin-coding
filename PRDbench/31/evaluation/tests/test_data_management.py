"""
Data Management Functional Test
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
def setup_data_manager():
    """Set up data manager"""
    create_tables()

    scale_manager = ScaleManager()
    data_manager = DataManager()

    # Create default scales
    scale_manager.create_default_scales()

    return data_manager, scale_manager

def test_create_participant(setup_data_manager):
    """Test create participant"""
    data_manager, scale_manager = setup_data_manager

    # Execute create participant
    participant = data_manager.create_participant(
        participant_id="TEST_P001",
        name="Test Participant",
        gender="Male",
        age=20,
        grade="Sophomore",
        major="Psychology"
    )

    # Assert
    assert participant is not None, "Participant creation failed"
    assert participant.participant_id == "TEST_P001", "Participant ID does not match"
    assert participant.name == "Test Participant", "Participant name does not match"
    assert participant.gender == "Male", "Participant gender does not match"
    assert participant.age == 20, "Participant age does not match"
    assert participant.grade == "Sophomore", "Participant grade does not match"
    assert participant.major == "Psychology", "Participant major does not match"

def test_create_response(setup_data_manager):
    """Test create questionnaire response"""
    data_manager, scale_manager = setup_data_manager

    # First create participant
    participant = data_manager.create_participant(
        participant_id="TEST_R001",
        name="Response Tester",
        gender="Female",
        age=19,
        grade="Freshman",
        major="Education"
    )

    # Create questionnaire response
    responses_data = {
        "1": 5, "2": 3, "3": 6, "4": 2,
        "5": 5, "6": 4, "7": 3, "8": 5
    }

    response = data_manager.create_response(
        participant_id="TEST_R001",
        scale_id=1,
        responses_data=responses_data
    )

    # Assert
    assert response is not None, "Questionnaire response creation failed"
    assert response.participant_id == participant.id, "Participant ID association error"
    assert response.scale_id == 1, "Scale ID does not match"
    assert response.responses_data == responses_data, "Response data does not match"
    assert response.total_score is not None, "Total score calculation failed"
    assert response.dimension_scores is not None, "Dimension score calculation failed"

def test_data_grouping(setup_data_manager):
    """Test data grouping function"""
    data_manager, scale_manager = setup_data_manager

    # Create multiple participants for grouping test
    participants_data = [
        {'participant_id': 'GROUP_001', 'gender': 'Male', 'grade': 'Freshman', 'major': 'Psychology'},
        {'participant_id': 'GROUP_002', 'gender': 'Female', 'grade': 'Freshman', 'major': 'Education'},
        {'participant_id': 'GROUP_003', 'gender': 'Male', 'grade': 'Sophomore', 'major': 'Psychology'},
        {'participant_id': 'GROUP_004', 'gender': 'Female', 'grade': 'Sophomore', 'major': 'Education'},
        {'participant_id': 'GROUP_005', 'gender': 'Male', 'grade': 'Junior', 'major': 'Psychology'},
    ]

    for p_data in participants_data:
        data_manager.create_participant(**p_data)

    # Test grouping by gender
    gender_groups = data_manager.list_participants(gender='Male')
    assert len(gender_groups) == 3, f"Male participant quantity does not match, expected: 3, actual: {len(gender_groups)}"

    female_groups = data_manager.list_participants(gender='Female')
    assert len(female_groups) == 2, f"Female participant quantity does not match, expected: 2, actual: {len(female_groups)}"

    # Test grouping by grade
    grade1_groups = data_manager.list_participants(grade='Freshman')
    assert len(grade1_groups) == 2, f"Freshman participant quantity does not match, expected: 2, actual: {len(grade1_groups)}"

    grade2_groups = data_manager.list_participants(grade='Sophomore')
    assert len(grade2_groups) == 2, f"Sophomore participant quantity does not match, expected: 2, actual: {len(grade2_groups)}"

    # Test grouping by major
    psychology_groups = data_manager.list_participants(major='Psychology')
    assert len(psychology_groups) == 3, f"Psychology major participant quantity does not match, expected: 3, actual: {len(psychology_groups)}"

    education_groups = data_manager.list_participants(major='Education')
    assert len(education_groups) == 2, f"Education major participant quantity does not match, expected: 2, actual: {len(education_groups)}"

def test_data_summary(setup_data_manager):
    """Test data summary function"""
    data_manager, scale_manager = setup_data_manager

    # Create test data
    participants_data = [
        {'participant_id': 'SUMMARY_001', 'gender': 'Male', 'grade': 'Freshman'},
        {'participant_id': 'SUMMARY_002', 'gender': 'Female', 'grade': 'Sophomore'},
        {'participant_id': 'SUMMARY_003', 'gender': 'Male', 'grade': 'Junior'},
    ]

    for p_data in participants_data:
        data_manager.create_participant(**p_data)

    # Create questionnaire responses
    for i, p_data in enumerate(participants_data):
        responses_data = {str(j): (i % 5) + 3 for j in range(1, 9)}  # Generate responses 3-7
        data_manager.create_response(
            participant_id=p_data['participant_id'],
            scale_id=1,
            responses_data=responses_data
        )

    # Test overall data summary
    summary = data_manager.get_data_summary()

    # Assert
    assert 'error' not in summary, f"Data summary retrieval failed: {summary.get('error', '')}"
    assert 'total_participants' in summary, "Missing total participants count"
    assert 'total_responses' in summary, "Missing total responses count"
    assert 'gender_distribution' in summary, "Missing gender distribution"
    assert 'grade_distribution' in summary, "Missing grade distribution"

    # Verify value reasonableness
    assert summary['total_participants'] >= 3, "Total participants should be at least 3"
    assert summary['total_responses'] >= 3, "Total responses should be at least 3"

    # Test specific scale data summary
    scale_summary = data_manager.get_data_summary(scale_id=1)

    assert 'responses_count' in scale_summary, "Missing scale responses count"
    assert 'completion_rate' in scale_summary, "Missing completion rate"
    assert scale_summary['responses_count'] >= 3, "Scale responses count should be at least 3"
    assert 0 <= scale_summary['completion_rate'] <= 100, "Completion rate should be between 0-100"

def test_data_anomaly_detection(setup_data_manager):
    """Test data anomaly detection"""
    data_manager, scale_manager = setup_data_manager

    # Create test data containing anomalies
    participants_data = [
        {'participant_id': 'ANOMALY_001', 'gender': 'Male', 'grade': 'Freshman'},
        {'participant_id': 'ANOMALY_002', 'gender': 'Female', 'grade': 'Sophomore'},
        {'participant_id': 'ANOMALY_003', 'gender': 'Male', 'grade': 'Junior'},
    ]

    for p_data in participants_data:
        data_manager.create_participant(**p_data)

    # Create normal response
    normal_responses = {str(j): j % 5 + 2 for j in range(1, 9)}
    data_manager.create_response("ANOMALY_001", 1, normal_responses)

    # Create extreme value response (all 7s)
    extreme_responses = {str(j): 7 for j in range(1, 9)}
    data_manager.create_response("ANOMALY_002", 1, extreme_responses)

    # Create missing response (only answer some items)
    missing_responses = {str(j): j % 5 + 2 for j in range(1, 6)}  # Only answer first 5 items
    data_manager.create_response("ANOMALY_003", 1, missing_responses)

    # Execute anomaly detection
    anomalies = data_manager.detect_data_anomalies(scale_id=1)

    # Assert
    assert 'error' not in anomalies, f"Anomaly detection failed: {anomalies.get('error', '')}"
    assert 'missing_responses' in anomalies, "Missing missing responses detection"
    assert 'extreme_values' in anomalies, "Missing extreme values detection"
    assert 'duplicate_responses' in anomalies, "Missing duplicate responses detection"

    # Verify detection results
    # Should detect extreme values (all 7s)
    extreme_values = anomalies['extreme_values']
    assert len(extreme_values) >= 1, "Should detect at least 1 extreme value"

    # Verify extreme value detection result structure
    if extreme_values:
        extreme_item = extreme_values[0]
        assert 'participant_id' in extreme_item, "Extreme value detection result missing participant ID"
        assert 'pattern' in extreme_item, "Extreme value detection result missing pattern description"

def test_import_export_participants(setup_data_manager):
    """Test participant data import and export"""
    data_manager, scale_manager = setup_data_manager

    # Create test CSV file
    test_data = {
        'participant_id': ['IMPORT_001', 'IMPORT_002', 'IMPORT_003'],
        'name': ['Import Test 1', 'Import Test 2', 'Import Test 3'],
        'gender': ['Male', 'Female', 'Male'],
        'age': [20, 19, 21],
        'grade': ['Sophomore', 'Freshman', 'Junior'],
        'major': ['Psychology', 'Education', 'Psychology']
    }

    test_file = Path("evaluation/temp_participants.csv")
    df = pd.DataFrame(test_data)
    df.to_csv(test_file, index=False, encoding='utf-8')

    try:
        # Test import
        participants = data_manager.import_participants_from_csv(test_file)

        # Assert
        assert len(participants) == 3, f"Imported participant quantity does not match, expected: 3, actual: {len(participants)}"

        # Verify imported data
        for i, participant in enumerate(participants):
            assert participant.participant_id == test_data['participant_id'][i], f"Participant {i+1} ID does not match"
            assert participant.name == test_data['name'][i], f"Participant {i+1} name does not match"
            assert participant.gender == test_data['gender'][i], f"Participant {i+1} gender does not match"

        # Test export
        export_file = Path("evaluation/temp_exported_participants.csv")
        success = data_manager.export_participants_to_csv(export_file)

        assert success == True, "Participant data export failed"
        assert export_file.exists(), "Exported participant file does not exist"

        # Verify export content
        exported_df = pd.read_csv(export_file)
        assert len(exported_df) >= 3, "Exported participant quantity insufficient"
        assert 'participant_id' in exported_df.columns, "Export file missing participant_id column"
        assert 'gender' in exported_df.columns, "Export file missing gender column"

        # Clean up export file
        if export_file.exists():
            export_file.unlink()

    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

def test_import_export_responses(setup_data_manager):
    """Test questionnaire response data import and export"""
    data_manager, scale_manager = setup_data_manager

    # First create participants
    participants = [
        {'participant_id': 'RESP_001', 'gender': 'Male', 'grade': 'Freshman'},
        {'participant_id': 'RESP_002', 'gender': 'Female', 'grade': 'Sophomore'},
    ]

    for p_data in participants:
        data_manager.create_participant(**p_data)

    # Create test response CSV file
    test_data = {
        'participant_id': ['RESP_001', 'RESP_002'],
        'item_1': [5, 6],
        'item_2': [3, 2],
        'item_3': [6, 7],
        'item_4': [2, 1],
        'item_5': [5, 6],
        'item_6': [4, 5],
        'item_7': [3, 2],
        'item_8': [5, 6]
    }

    test_file = Path("evaluation/temp_responses.csv")
    df = pd.DataFrame(test_data)
    df.to_csv(test_file, index=False, encoding='utf-8')

    try:
        # Test import
        responses = data_manager.import_responses_from_csv(test_file, scale_id=1)

        # Assert
        assert len(responses) == 2, f"Imported response quantity does not match, expected: 2, actual: {len(responses)}"

        # Verify response data
        for response in responses:
            assert response.scale_id == 1, "Scale ID does not match"
            assert response.total_score is not None, "Total score not calculated"
            assert response.dimension_scores is not None, "Dimension scores not calculated"
            assert len(response.responses_data) == 8, "Response item quantity does not match"

        # Test export
        export_file = Path("evaluation/temp_exported_responses.csv")
        success = data_manager.export_responses_to_csv(export_file, scale_id=1)

        assert success == True, "Questionnaire response export failed"
        assert export_file.exists(), "Exported response file does not exist"

        # Verify export content
        exported_df = pd.read_csv(export_file)
        assert len(exported_df) >= 2, "Exported response quantity insufficient"
        assert 'participant_id' in exported_df.columns, "Export file missing participant_id column"
        assert 'total_score' in exported_df.columns, "Export file missing total_score column"

        # Clean up export file
        if export_file.exists():
            export_file.unlink()

    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

def test_get_response_data(setup_data_manager):
    """Test get response data DataFrame"""
    data_manager, scale_manager = setup_data_manager

    # Create test data
    participant = data_manager.create_participant(
        participant_id="DATA_001",
        gender="Male",
        age=20,
        grade="Sophomore",
        major="Psychology"
    )

    responses_data = {str(i): i % 5 + 3 for i in range(1, 9)}
    data_manager.create_response("DATA_001", 1, responses_data)

    # Get data DataFrame
    df = data_manager.get_response_data(scale_id=1, include_demographics=True)

    # Assert
    assert not df.empty, "Retrieved data DataFrame is empty"
    assert 'participant_id' in df.columns, "Missing participant_id column"
    assert 'total_score' in df.columns, "Missing total_score column"
    assert 'gender' in df.columns, "Missing gender column"
    assert 'grade' in df.columns, "Missing grade column"

    # Verify item columns
    item_columns = [col for col in df.columns if col.startswith('item_')]
    assert len(item_columns) >= 8, f"Item column quantity insufficient, expected at least 8, actual: {len(item_columns)}"

    # Verify data content
    assert len(df) >= 1, "Data row count insufficient"
    first_row = df.iloc[0]
    assert first_row['participant_id'] == "DATA_001", "Participant ID does not match"
    assert first_row['gender'] == "Male", "Gender information does not match"

def test_data_validation():
    """Test data validation function"""
    data_manager = DataManager()

    # Test duplicate participant ID
    data_manager.create_participant(participant_id="DUPLICATE_001", name="First one")
    duplicate_participant = data_manager.create_participant(participant_id="DUPLICATE_001", name="Second one")

    # System should return existing participant, not create new one
    assert duplicate_participant.name == "First one", "Duplicate ID handling incorrect"

    # Test invalid questionnaire response
    with pytest.raises(Exception):
        # Try to create response for non-existent participant
        data_manager.create_response("NONEXISTENT", 1, {"1": 5})

    with pytest.raises(Exception):
        # Try to create response for non-existent scale
        data_manager.create_response("DUPLICATE_001", 999, {"1": 5})

def test_score_calculation(setup_data_manager):
    """Test score calculation function"""
    data_manager, scale_manager = setup_data_manager

    # Create participant
    participant = data_manager.create_participant(
        participant_id="SCORE_001",
        gender="Female",
        age=19
    )

    # Create response with reverse scoring
    responses_data = {
        "1": 7,  # Forward item, high score
        "2": 1,  # Reverse item, low score (actually high score)
        "3": 6,  # Forward item
        "4": 2,  # Reverse item (actually high score)
        "5": 5,  # Forward item
        "6": 4,  # Forward item
        "7": 3,  # Reverse item (actually medium score)
        "8": 6   # Forward item
    }

    response = data_manager.create_response("SCORE_001", 1, responses_data)

    # Assert
    assert response.total_score is not None, "Total score calculation failed"
    assert response.dimension_scores is not None, "Dimension score calculation failed"
    assert isinstance(response.total_score, (int, float)), "Total score should be numeric type"
    assert isinstance(response.dimension_scores, dict), "Dimension scores should be dictionary type"

    # Verify score range reasonableness (assuming 7-point scale)
    assert 1 <= response.total_score <= 7, f"Total score out of reasonable range: {response.total_score}"

    # Verify dimension scores
    for dimension, score in response.dimension_scores.items():
        assert 1 <= score <= 7, f"Dimension {dimension} score out of reasonable range: {score}"
