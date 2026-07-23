import sys
import os
import pandas as pd
import pytest

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from tta.processor import process_data


def test_feedback_simplification():
    """
    Test whether the feedback column text simplification function works as expected.
    """
    # Arrange
    data = {
        'Task ID': ['TASK-001'],
        'Task Name': ['Test Task'],
        'Test Item': ['Project A'],
        'Equipment Duration': [1.0],
        'Test Status': ['Success'],
        'Test Type': ['Type 1'],
        'Test Item Feedback': ['Trial shows no anomaly']
    }
    input_df = pd.DataFrame(data)

    # Act
    result_df = process_data(input_df)

    # Assert
    assert not result_df.empty
    assert 'Test Item Feedback' in result_df.columns
    assert result_df.loc[0, 'Test Item Feedback'] == 'No anomalies'


def test_error_code_extraction():
    """
    Test the function for extracting exception identifiers from the feedback column.
    """
    # Arrange
    data = {
        'Task ID': ['TASK-002'],
        'Task Name': ['Another Test'],
        'Test Item': ['Project B'],
        'Equipment Duration': [2.0],
        'Test Status': ['Failure'],
        'Test Type': ['Type 2'],
        'Test Item Feedback': ['Error-404, Device Restart']
    }
    input_df = pd.DataFrame(data)

    # Act
    result_df = process_data(input_df)

    # Assert
    assert 'Anomaly Identifier' in result_df.columns
    assert result_df.loc[0, 'Anomaly Identifier'] == 'Error-404,'