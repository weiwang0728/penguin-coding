import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from sqlalchemy.orm import Session
from src.cli.data_cli import app
from src.database import SessionLocal
from src.models.questionnaire import Questionnaire, Question, Choice, QuestionType
import typer
from typer.testing import CliRunner

# Initialize the CLI runner for testing Typer apps
runner = CliRunner()

@pytest.fixture
def setup_test_db_with_scale_question():
    """Fixture to set up a test questionnaire without affecting existing data."""
    # Import all models to ensure they're registered with Base
    from src.database import Base, engine
    from src.models.questionnaire import Questionnaire, Question, Choice, QuestionType
    from src.models.response import ResponseSession, Response
    
    # Ensure tables exist (but don't drop existing data)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create a test questionnaire with a unique name
        q = Questionnaire(
            title="Range Validation Test Questionnaire_Automated Test",
            description="A test questionnaire for range validation."
        )
        db.add(q)
        db.flush() # Get ID for questions

        # Add a scale question with range 1-5
        q_scale = Question(text="To what extent does price influence you?", module="Travel Motivation", question_type=QuestionType.SCALE, questionnaire_id=q.id)
        db.add(q_scale)
        db.flush()
        # For scale, we store range as a note (as per questionnaire_cli logic)
        db.add(Choice(text="Scale Range: 1-5", question_id=q_scale.id))

        db.commit()
        yield (db, q.id, q.title)
    finally:
        db.close()
        # Don't drop tables - leave existing data intact

def test_range_validation_in_data_collection(setup_test_db_with_scale_question):
    """
    Test range validation for scale questions in the data collection flow.
    This test uses command line arguments to specify the questionnaire directly,
    avoiding the need to interact with questionnaire selection.
    """
    db, questionnaire_id, questionnaire_title = setup_test_db_with_scale_question
    
    # The input data that would be provided by the user during interaction
    # First attempt with out-of-range '6', then valid '4'
    user_input = "\n".join([
        "6",                # First attempt: Out-of-range answer to scale question
        "4",                # Second attempt: Valid answer to scale question
    ])

    # Run the CLI command with command line arguments to specify questionnaire directly
    # This avoids the questionnaire selection interaction
    result = runner.invoke(app, [
        "add",
        "--template-name", questionnaire_title,
        "--collector", "Test Surveyor",
        "--location", "Test Location"
    ], input=user_input)

    # Assert that the command executed successfully (exit code 0)
    assert result.exit_code == 0, f"Command failed with output: {result.stdout}"

    # Assert that the success message is in the output
    assert "Starting to enter new questionnaire response" in result.stdout

    # Assert that range validation error message appears
    assert "Input must be between 1-5" in result.stdout

    # Assert that the questionnaire was processed
    assert questionnaire_title in result.stdout

    # Assert successful completion
    assert "Questionnaire response successfully saved" in result.stdout