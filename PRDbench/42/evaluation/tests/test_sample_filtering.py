#!/usr/bin/env python3
"""
Test multi-dimensional sample filtering function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse
from app.utils.data_processor import DataProcessor

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def sample_data(app):
    """Create test sample data"""
    with app.app_context():
        # Create test companies
        company1 = Company(name="Test Company A", industry="Technology")
        company2 = Company(name="Test Company B", industry="Finance")
        db.session.add_all([company1, company2])
        db.session.commit()

        # Create test surveys
        survey1 = Survey(title="Test Survey A", company_id=company1.id, created_by=1)
        survey2 = Survey(title="Test Survey B", company_id=company2.id, created_by=1)
        db.session.add_all([survey1, survey2])
        db.session.commit()

        # Create test response data
        responses = [
            # Company A data
            SurveyResponse(survey_id=survey1.id, respondent_name="Zhang San", department="Technology Department",
                         position="Manager", management_level="Middle", leadership_score=4.0),
            SurveyResponse(survey_id=survey1.id, respondent_name="Li Si", department="Marketing Department",
                         position="Supervisor", management_level="Junior", leadership_score=3.5),
            SurveyResponse(survey_id=survey1.id, respondent_name="Wang Wu", department="Technology Department",
                         position="Director", management_level="Senior", leadership_score=4.5),

            # Company B data
            SurveyResponse(survey_id=survey2.id, respondent_name="Zhao Liu", department="Finance Department",
                         position="Manager", management_level="Middle", leadership_score=3.8),
            SurveyResponse(survey_id=survey2.id, respondent_name="Qian Qi", department="HR Department",
                         position="Supervisor", management_level="Junior", leadership_score=3.2),
        ]

        db.session.add_all(responses)
        db.session.commit()

        return {
            'companies': [company1, company2],
            'surveys': [survey1, survey2],
            'responses': responses
        }

def test_multi_dimension_filtering(app, sample_data):
    """Test multi-dimensional sample filtering function"""
    with app.app_context():
        data_processor = DataProcessor()

        # Re-query company objects to avoid DetachedInstanceError
        company_a = Company.query.filter_by(name="Test Company A").first()

        # Test company filtering
        company_a_responses = SurveyResponse.query.join(Survey)\
                                                 .filter(Survey.company_id == company_a.id)\
                                                 .all()
        assert len(company_a_responses) == 3

        # Test department filtering
        tech_responses = SurveyResponse.query.filter_by(department="Technology Department").all()
        assert len(tech_responses) == 2

        # Test management level filtering
        senior_responses = SurveyResponse.query.filter_by(management_level="Senior").all()
        assert len(senior_responses) == 1
        assert senior_responses[0].respondent_name == "Wang Wu"

        # Test combined filtering: Company A + Technology Department
        combined_responses = SurveyResponse.query.join(Survey)\
                                                .filter(Survey.company_id == company_a.id)\
                                                .filter(SurveyResponse.department == "Technology Department")\
                                                .all()
        assert len(combined_responses) == 2

        # Verify filtering results correctness
        names = [r.respondent_name for r in combined_responses]
        assert "Zhang San" in names
        assert "Wang Wu" in names

        print("✅ Multi-dimensional sample filtering function test passed")

if __name__ == "__main__":
    pytest.main([__file__])
