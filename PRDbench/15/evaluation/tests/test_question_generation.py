import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from src.questions import generate_questions, Question

def test_all_dimensions_covered():
    question_types = {
        "Single Choice": 10,
        "Multiple Choice": 10,
        "True/False": 10,
        "Situational Analysis": 10,
    }
    questions, _ = generate_questions(question_types, "Beginner")
    questions.extend(generate_questions(question_types, "Intermediate")[0])
    questions.extend(generate_questions(question_types, "Advanced")[0])
    dimensions = {q.dimension for q in questions}
    assert dimensions == {"Professional Knowledge", "Problem Solving", "Teamwork", "Communication", "Learning Ability", "Professionalism"}

def test_question_content_completeness():
    question_types = {"Single Choice": 5}
    questions, _ = generate_questions(question_types, "Beginner")
    for q in questions:
        assert q.answer is not None
        assert q.dimension is not None

def test_star_analysis_present():
    question_types = {"Situational Analysis": 1}
    questions, _ = generate_questions(question_types, "Beginner")
    assert questions[0].star_analysis is not None
