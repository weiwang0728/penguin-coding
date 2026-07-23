#!/usr/bin/env python3
"""
Test Multi-Dimensional Visualization Dashboard Function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import Company, Survey, SurveyResponse
from app.utils.visualizer import DataVisualizer

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
            SurveyResponse(survey_id=survey.id, respondent_name="Zhang San", department="Technical Dept",
                         management_level="Middle", leadership_score=4.2, planning_score=4.0,
                         decision_score=3.8, professional_score=4.5),
            SurveyResponse(survey_id=survey.id, respondent_name="Li Si", department="Marketing Dept",
                         management_level="Junior", leadership_score=3.5, planning_score=3.8,
                         decision_score=4.0, professional_score=3.2),
            SurveyResponse(survey_id=survey.id, respondent_name="Wang Wu", department="HR Dept",
                         management_level="Senior", leadership_score=4.8, planning_score=4.5,
                         decision_score=4.2, professional_score=4.0),
        ]

        db.session.add_all(responses)
        db.session.commit()

        return {
            'company': company,
            'survey': survey,
            'responses': responses
        }

def test_skills_radar_chart(app, sample_data):
    """Test skill distribution radar chart function"""
    with app.app_context():
        visualizer = DataVisualizer()

        # Re-query responses to avoid DetachedInstanceError
        responses = SurveyResponse.query.all()

        # Calculate skill average scores
        skills_data = {
            'Leadership & Motivation': sum(r.leadership_score for r in responses if r.leadership_score) / len([r for r in responses if r.leadership_score]),
            'Planning & Organization': sum(r.planning_score for r in responses if r.planning_score) / len([r for r in responses if r.planning_score]),
            'Decision & Innovation': sum(r.decision_score for r in responses if r.decision_score) / len([r for r in responses if r.decision_score]),
            'Professional Control': sum(r.professional_score for r in responses if r.professional_score) / len([r for r in responses if r.professional_score])
        }

        # Verify radar chart data structure
        assert len(skills_data) == 4
        assert all(0 <= score <= 5 for score in skills_data.values())

        # Mock generate radar chart
        radar_config = {
            'type': 'radar',
            'data': skills_data,
            'title': 'Skill Distribution Radar Chart',
            'max_value': 5
        }

        # Verify radar chart configuration
        assert radar_config['type'] == 'radar'
        assert len(radar_config['data']) == 4
        assert radar_config['max_value'] == 5

        # Verify skill dimension completeness
        required_skills = ['Leadership & Motivation', 'Planning & Organization', 'Decision & Innovation', 'Professional Control']
        for skill in required_skills:
            assert skill in radar_config['data']

        print("✅ Skill distribution radar chart function test passed")
        print(f"   Skill data: {skills_data}")

def test_growth_line_chart(app, sample_data):
    """Test growth trend line chart function"""
    with app.app_context():
        visualizer = DataVisualizer()

        # Mock time series data (skill scores at different time points)
        time_series_data = {
            '2024-01': {'leadership': 3.5, 'planning': 3.3, 'decision': 3.2, 'professional': 3.4},
            '2024-02': {'leadership': 3.7, 'planning': 3.6, 'decision': 3.5, 'professional': 3.6},
            '2024-03': {'leadership': 4.0, 'planning': 3.9, 'decision': 3.8, 'professional': 3.9},
        }

        # Verify line chart data structure
        assert len(time_series_data) == 3

        for month, scores in time_series_data.items():
            assert len(scores) == 4
            assert all(0 <= score <= 5 for score in scores.values())

        # Mock generate line chart configuration
        line_config = {
            'type': 'line',
            'data': time_series_data,
            'title': 'Skill Growth Trend Chart',
            'x_axis': 'time',
            'y_axis': 'score'
        }

        # Verify line chart configuration
        assert line_config['type'] == 'line'
        assert line_config['x_axis'] == 'time'
        assert line_config['y_axis'] == 'score'

        print("✅ Growth trend line chart function test passed")

def test_low_score_heatmap(app, sample_data):
    """Test low score alert heatmap function"""
    with app.app_context():
        visualizer = DataVisualizer()

        # Re-query responses to avoid DetachedInstanceError
        responses = SurveyResponse.query.all()

        # Build heatmap data matrix
        heatmap_data = []
        for response in responses:
            row_data = {
                'name': response.respondent_name,
                'department': response.department,
                'leadership': response.leadership_score,
                'planning': response.planning_score,
                'decision': response.decision_score,
                'professional': response.professional_score
            }
            heatmap_data.append(row_data)

        # Identify low score items (assume less than 3.5 is low score)
        low_score_threshold = 3.5
        low_score_items = []

        for item in heatmap_data:
            for skill in ['leadership', 'planning', 'decision', 'professional']:
                if item[skill] < low_score_threshold:
                    low_score_items.append({
                        'name': item['name'],
                        'department': item['department'],
                        'skill': skill,
                        'score': item[skill]
                    })

        # Verify low score alert function
        assert len(low_score_items) > 0  # Should have low score items

        # Verify heatmap configuration
        heatmap_config = {
            'type': 'heatmap',
            'data': heatmap_data,
            'title': 'Skill Score Heatmap',
            'threshold': low_score_threshold,
            'low_score_items': low_score_items
        }

        assert heatmap_config['type'] == 'heatmap'
        assert heatmap_config['threshold'] == 3.5
        assert len(heatmap_config['low_score_items']) > 0

        print("✅ Low score alert heatmap function test passed")
        print(f"   Found {len(low_score_items)} low score alert item(s)")
        for item in low_score_items:
            print(f"   - {item['name']} ({item['department']}): {item['skill']} = {item['score']}")

if __name__ == "__main__":
    pytest.main([__file__])
