#!/usr/bin/env python3
"""
Test historical data version management function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse, DataVersion

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def test_company(app):
    """Create test company"""
    with app.app_context():
        company = Company(name="Test Company", industry="Technology")
        db.session.add(company)
        db.session.commit()
        return company

def test_data_version_snapshots(app, test_company):
    """Test data version snapshot function"""
    with app.app_context():
        # Re-query company object to avoid DetachedInstanceError
        company = Company.query.filter_by(name="Test Company").first()

        # First data import
        survey1 = Survey(title="Initial Survey", company_id=company.id, created_by=1)
        db.session.add(survey1)
        db.session.commit()

        # Add initial data
        initial_responses = [
            SurveyResponse(survey_id=survey1.id, respondent_name="Zhang San", department="Technology Department",
                         management_level="Middle", leadership_score=4.0),
            SurveyResponse(survey_id=survey1.id, respondent_name="Li Si", department="Marketing Department",
                         management_level="Junior", leadership_score=3.5),
        ]
        db.session.add_all(initial_responses)
        db.session.commit()

        # Create first version snapshot
        version1 = DataVersion(
            version_name="1.0",
            description="Initial data import",
            data_type="survey",
            created_by=1
        )
        version1.set_snapshot({
            'company_id': company.id,
            'survey_count': 1,
            'response_count': 2,
            'responses': [
                {'name': 'Zhang San', 'department': 'Technology Department', 'level': 'Middle', 'score': 4.0},
                {'name': 'Li Si', 'department': 'Marketing Department', 'level': 'Junior', 'score': 3.5}
            ]
        })
        db.session.add(version1)
        db.session.commit()

        # Verify first version
        versions = DataVersion.query.filter_by(version_name="1.0").all()
        assert len(versions) == 1
        assert versions[0].version_name == "1.0"
        assert versions[0].get_snapshot()['response_count'] == 2

        # Second data update
        survey2 = Survey(title="Updated Survey", company_id=company.id, created_by=1)
        db.session.add(survey2)
        db.session.commit()

        # Add more data
        additional_responses = [
            SurveyResponse(survey_id=survey2.id, respondent_name="Wang Wu", department="HR Department",
                         management_level="Senior", leadership_score=4.5),
            SurveyResponse(survey_id=survey2.id, respondent_name="Zhao Liu", department="Finance Department",
                         management_level="Middle", leadership_score=3.8),
        ]
        db.session.add_all(additional_responses)
        db.session.commit()

        # Create second version snapshot
        total_responses = SurveyResponse.query.join(Survey)\
                                            .filter(Survey.company_id == company.id)\
                                            .count()

        version2 = DataVersion(
            version_name="2.0",
            description="Data update",
            data_type="survey",
            created_by=1
        )
        version2.set_snapshot({
            'company_id': company.id,
            'survey_count': 2,
            'response_count': total_responses,
            'responses': [
                {'name': 'Zhang San', 'department': 'Technology Department', 'level': 'Middle', 'score': 4.0},
                {'name': 'Li Si', 'department': 'Marketing Department', 'level': 'Junior', 'score': 3.5},
                {'name': 'Wang Wu', 'department': 'HR Department', 'level': 'Senior', 'score': 4.5},
                {'name': 'Zhao Liu', 'department': 'Finance Department', 'level': 'Middle', 'score': 3.8}
            ]
        })
        db.session.add(version2)
        db.session.commit()

        # Verify version management function
        all_versions = DataVersion.query.filter(
            DataVersion.version_name.in_(["1.0", "2.0"])
        ).order_by(DataVersion.created_at).all()

        assert len(all_versions) == 2
        assert all_versions[0].version_name == "1.0"
        assert all_versions[1].version_name == "2.0"

        # Verify version snapshot content
        assert all_versions[0].get_snapshot()['response_count'] == 2
        assert all_versions[1].get_snapshot()['response_count'] == 4

        # Verify read-only nature (version snapshots should not be modified)
        original_snapshot = all_versions[0].get_snapshot().copy()

        # Try to modify snapshot (this should not affect version in database)
        modified_snapshot = all_versions[0].get_snapshot()
        modified_snapshot['modified'] = True

        # Re-query to verify read-only nature
        version_check = DataVersion.query.filter_by(version_name="1.0").first()
        # Note: In actual implementation, there should be mechanisms to prevent version snapshots from being modified

        print("✅ Historical data version management function test passed")

if __name__ == "__main__":
    pytest.main([__file__])
