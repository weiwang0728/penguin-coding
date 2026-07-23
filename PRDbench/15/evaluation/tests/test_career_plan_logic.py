import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from src.career_planning import generate_development_plan

def test_development_plan_core_skills():
    plan = generate_development_plan("Technical/Functional Competence")
    assert "Core Competency Improvement Recommendations" in plan
    assert "Deepen professional knowledge" in plan or "Professional knowledge" in plan

def test_development_plan_resources():
    plan = generate_development_plan("General Managerial Competence")
    assert "Recommended Learning Resources" in plan
    assert "Online Course Platforms" in plan

def test_development_plan_goals():
    plan = generate_development_plan("Entrepreneurial Creativity")
    assert "Phased Goal Setting" in plan
    assert "Short-term (1-3 months)" in plan
