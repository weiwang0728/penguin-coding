import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from src.cli.questionnaire_cli import add_question
from src.models.questionnaire import Questionnaire, Question, Choice, QuestionType
from src.database import SessionLocal

# Test data
TEST_TEMPLATE_NAME = "2024 Spring Survey"
TEST_MODULE = "Consumption Status"
TEST_Q_TYPE = "Multiple Choice"
TEST_TITLE = "Which types of golf courses do you frequently visit?"
TEST_OPTIONS = "Public Course,Private Club,Practice Range"


def test_add_multiple_choice_question_to_existing_template():
    """
    Test adding a multiple-choice question to an existing questionnaire template.
    This test mocks the database session and asserts that the correct objects
    are created and added to the session.
    """
    # Create a real Questionnaire instance for the relationship
    # We create it without adding it to a session to keep the test isolated
    real_questionnaire = Questionnaire(title=TEST_TEMPLATE_NAME)
    # If the model requires an ID for relationship setup, we can set it directly
    # This is a common practice in unit tests for ORM models
    real_questionnaire.id = 1 

    # Create a mock session
    mock_db = MagicMock(spec=Session)
    # Mock the query method to return the real questionnaire instance
    mock_db.query.return_value.filter.return_value.first.return_value = real_questionnaire

    # Mock the add, flush, and commit methods
    mock_db.add = MagicMock()
    mock_db.flush = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.rollback = MagicMock()

    # Patch the SessionLocal to return our mock session
    with patch('src.cli.questionnaire_cli.SessionLocal', return_value=mock_db):
        # Call the function under test with simulated command-line arguments
        # We need to handle the Typer Exit exception
        try:
            add_question(
                template_name=TEST_TEMPLATE_NAME,
                module=TEST_MODULE,
                q_type=TEST_Q_TYPE,
                title=TEST_TITLE,
                options=TEST_OPTIONS
            )
        except SystemExit:
            pass # Expected due to typer.Exit() call in the function

    # Assert that the questionnaire query was called correctly
    mock_db.query.assert_called_once_with(Questionnaire)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.first.assert_called_once()

    # Assert that a Question object was created with the correct parameters
    created_question = mock_db.add.call_args_list[0][0][0]
    assert isinstance(created_question, Question)
    assert created_question.text == TEST_TITLE
    assert created_question.module == TEST_MODULE
    assert created_question.question_type == QuestionType.MULTIPLE_CHOICE
    # Assert that the questionnaire relationship is set correctly
    # Since we used a real instance, we can compare IDs or the instance itself
    assert created_question.questionnaire is real_questionnaire
    # Note: In a real database session, after db.add() and db.flush(), 
    # the ORM would set created_question.questionnaire_id to real_questionnaire.id.
    # However, in this mock test environment, this automatic assignment doesn't happen.
    # The critical part is that the 'questionnaire' relationship object is correctly set,
    # which we've verified with the 'is' assertion above.
    # We are intentionally not asserting questionnaire_id here due to the limitations of the mock.

    # Assert that three Choice objects were created and added
    assert mock_db.add.call_count == 4 # 1 for question + 3 for choices
    for i, option_text in enumerate(["Public Course", "Private Club", "Practice Range"], start=1):
        created_choice = mock_db.add.call_args_list[i][0][0]
        assert isinstance(created_choice, Choice)
        assert created_choice.text == option_text
        assert created_choice.question == created_question

    # Assert that flush and commit were called
    mock_db.flush.assert_called_once()
    mock_db.commit.assert_called_once()

    # Assert that rollback was not called (i.e., no exception was raised before commit)
    mock_db.rollback.assert_not_called()
