#!/usr/bin/env python3
"""
Test interview text manual input function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Interview

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_manual_interview_input(app):
    """Test manual input interview text function"""
    with app.app_context():
        # Create test company
        company = Company(name="Test Company", industry="Test Industry")
        db.session.add(company)
        db.session.commit()

        # Prepare interview text
        interview_content = """
        Interview Record - Management Skills Assessment

        Interviewee: Test Manager
        Position: Department Manager
        Interview Date: January 15, 2024

        Question 1: What do you think is the most important management skill?
        Answer: I think communication skills are most important, being able to effectively communicate with team members, understand their needs and difficulties.

        Question 2: What experience do you have in project management?
        Answer: I usually set up detailed project plans, define clear milestones, and track progress regularly.

        Summary: This manager performs well in communication and project management.
        """

        # Create interview record
        interview = Interview(
            title="Manual Input Test Interview",
            company_id=company.id,
            content=interview_content.strip(),
            interviewee_name="Test Manager",
            interviewee_position="Department Manager"
        )

        db.session.add(interview)
        db.session.commit()

        # Verify interview record has been saved
        saved_interview = Interview.query.filter_by(title="Manual Input Test Interview").first()
        assert saved_interview is not None
        assert saved_interview.content == interview_content.strip()
        assert saved_interview.interviewee_name == "Test Manager"
        assert saved_interview.company_id == company.id

        print("✅ Interview text manual input function test passed")

if __name__ == "__main__":
    pytest.main([__file__])
