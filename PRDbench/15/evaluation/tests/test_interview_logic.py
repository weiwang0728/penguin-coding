import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import os
from src.main import generate_radar_chart, generate_report

# Mocking the console and other dependencies if necessary
class MockConsole:
    def print(self, text):
        pass

@pytest.fixture
def mock_console(monkeypatch):
    monkeypatch.setattr('src.main.console', MockConsole())

def test_radar_chart_generation(mock_console):
    scores = {
        "Professional Knowledge": 4.5,
        "Problem Solving": 3.8,
        "Teamwork": 4.2,
        "Communication": 4.0,
        "Learning Ability": 4.8,
        "Professionalism": 4.6
    }
    generate_radar_chart(scores)
    assert os.path.exists("competency_radar_chart.png")
    os.remove("competency_radar_chart.png")

def test_report_contains_suggestions(capsys):
    scores = {
        "Professional Knowledge": 2.5,
        "Problem Solving": 3.0,
        "Teamwork": 4.0,
        "Communication": 3.5,
        "Learning Ability": 4.5,
        "Professionalism": 4.0
    }
    generate_report(scores, 120)  # Add a mock total_time
    captured = capsys.readouterr()
    # This is a simple check. A more robust test would check for specific suggestions.
    assert "Comprehensive Evaluation Report" in captured.out
