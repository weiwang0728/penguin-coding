#!/usr/bin/env python3
"""
Test sample batch metadata annotation function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse

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
        # Create test company
        company = Company(name="Test Company", industry="Technology")
        db.session.add(company)
        db.session.commit()

        # Create test survey
        survey = Survey(title="Test Survey", company_id=company.id, created_by=1)
        db.session.add(survey)
        db.session.commit()

        # Create test response data
        responses = [
            SurveyResponse(survey_id=survey.id, respondent_name="Zhang San", department="Technology Department",
                         management_level="Middle", leadership_score=4.0),
            SurveyResponse(survey_id=survey.id, respondent_name="Li Si", department="Marketing Department",
                         management_level="Junior", leadership_score=3.5),
            SurveyResponse(survey_id=survey.id, respondent_name="Wang Wu", department="HR Department",
                         management_level="Senior", leadership_score=4.5),
        ]

        db.session.add_all(responses)
        db.session.commit()

        return {
            'company': company,
            'survey': survey,
            'responses': responses
        }

def test_batch_metadata_annotation(app, sample_data):
    """Test batch metadata annotation function"""
    with app.app_context():
        # Re-query survey object to avoid DetachedInstanceError
        survey = Survey.query.filter_by(title="Test Survey").first()

        # Get sample data
        responses = SurveyResponse.query.filter_by(survey_id=survey.id).all()

        # Simulate batch adding metadata tags
        metadata_tags = {
            'data_source': 'Source A',
            'data_quality': 'Valid',
            'batch_id': 'BATCH_001',
            'validation_status': 'Verified'
        }

        # Add metadata to all samples
        for response in responses:
            # Use raw_data field to save metadata
            current_raw_data = response.get_raw_data() or {}
            current_raw_data.update({'metadata': metadata_tags})
            response.set_raw_data(current_raw_data)
            # Ensure object is marked as modified
            db.session.add(response)

        db.session.commit()

        # Verify metadata annotation results
        updated_responses = SurveyResponse.query.filter_by(survey_id=survey.id).all()

        for response in updated_responses:
            raw_data = response.get_raw_data()
            assert 'metadata' in raw_data
            assert raw_data['metadata']['data_source'] == 'Source A'
            assert raw_data['metadata']['data_quality'] == 'Valid'
            assert raw_data['metadata']['batch_id'] == 'BATCH_001'
            assert raw_data['metadata']['validation_status'] == 'Verified'

        # Test filtering by metadata
        filtered_responses = []
        for response in updated_responses:
            raw_data = response.get_raw_data()
            if raw_data.get('metadata', {}).get('data_source') == 'Source A':
                filtered_responses.append(response)

        assert len(filtered_responses) == 3

        print("✅ Batch metadata annotation function test passed")

if __name__ == "__main__":
    pytest.main([__file__])
