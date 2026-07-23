
import pytest
from unittest.mock import MagicMock
from rich.console import Console
from src.cli.data_cli import _collect_single_question_answer
from src.models.questionnaire import Question, QuestionType

@pytest.fixture
def mock_question():
    """Fixture to create a mock question object."""
    return Question(
        id=1,
        text="This is a test question?",
        module="Test Module",
        question_type=QuestionType.OPEN_TEXT
    )

def test_collect_single_question_answer_rejects_empty_then_accepts(monkeypatch, mock_question):
    """
    Tests that the data collection function first rejects an empty answer,
    prints an error, and then accepts a subsequent valid answer.
    """
    # Mock the Prompt.ask to simulate user input
    # First input is empty, second is a valid answer
    inputs = ["", "Valid Answer"]
    input_iterator = iter(inputs)
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda _: next(input_iterator))

    # Mock the console to capture output
    mock_console = MagicMock(spec=Console)

    # Call the function under test
    result = _collect_single_question_answer(mock_question, mock_console)

    # Assert that the function returned the valid answer
    assert result == "Valid Answer"

    # Assert that the error message for required input was printed
    mock_console.print.assert_called_once_with("[bold red]This field is required, please enter valid content.[/bold red]")
