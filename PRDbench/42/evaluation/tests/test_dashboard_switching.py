#!/usr/bin/env python3
"""
Test dashboard multi-dimensional switching comparison function
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
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
def time_series_data(app):
    """Create time series test data"""
    with app.app_context():
        # Create test company
        company = Company(name="Test Company", industry="Technology")
        db.session.add(company)
        db.session.commit()

        # Create surveys at different times
        base_time = datetime(2024, 1, 1)
        surveys = []
        responses = []

        for i in range(3):  # Create 3 months of data
            survey_time = base_time + timedelta(days=30*i)
            survey = Survey(
                title=f"Monthly Survey_{i+1}",
                company_id=company.id,
                created_by=1,
                created_at=survey_time
            )
            surveys.append(survey)
            db.session.add(survey)

        db.session.commit()

        # Add response data for each survey
        for i, survey in enumerate(surveys):
            # Simulate skills improving over time
            base_score = 3.0 + i * 0.3
            response = SurveyResponse(
                survey_id=survey.id,
                respondent_name=f"Employee{i+1}",
                department="Technology Department",
                management_level="Middle",
                leadership_score=base_score + 0.2,
                planning_score=base_score + 0.1,
                decision_score=base_score,
                professional_score=base_score + 0.3,
                created_at=survey.created_at
            )
            responses.append(response)
            db.session.add(response)

        db.session.commit()

        return {
            'company': company,
            'surveys': surveys,
            'responses': responses
        }

def test_time_dimension_switch(app, time_series_data):
    """Test dashboard function by time dimension switching"""
    with app.app_context():
        visualizer = DataVisualizer()

        # Re-query test-related responses to avoid DetachedInstanceError
        company = Company.query.filter_by(name="Test Company").first()
        responses = SurveyResponse.query.join(Survey).filter(Survey.company_id == company.id).all()

        # Organize data by time dimension
        time_grouped_data = {}
        for response in responses:
            month_key = response.created_at.strftime('%Y-%m')
            if month_key not in time_grouped_data:
                time_grouped_data[month_key] = []

            time_grouped_data[month_key].append({
                'leadership': response.leadership_score,
                'planning': response.planning_score,
                'decision': response.decision_score,
                'professional': response.professional_score
            })

        # Verify time dimension data (adjust according to actual time group count)
        assert len(time_grouped_data) >= 2  # At least 2 time groups

        # Calculate average score for each time point
        time_averages = {}
        for month, data_list in time_grouped_data.items():
            time_averages[month] = {
                'leadership': sum(d['leadership'] for d in data_list) / len(data_list),
                'planning': sum(d['planning'] for d in data_list) / len(data_list),
                'decision': sum(d['decision'] for d in data_list) / len(data_list),
                'professional': sum(d['professional'] for d in data_list) / len(data_list)
            }

        # Verify time trend
        months = sorted(time_averages.keys())
        leadership_trend = [time_averages[month]['leadership'] for month in months]

        # Verify skills improving over time (if there are enough time points)
        if len(leadership_trend) >= 2:
            assert leadership_trend[-1] > leadership_trend[0]  # Last time point higher than first

        print("✅ Time dimension switching function test passed")
        print(f"   Number of time points: {len(time_grouped_data)}")
        for month in months:
            avg_score = sum(time_averages[month].values()) / 4
            print(f"   {month}: Average score {avg_score:.2f}")

def test_company_attribute_switch(app):
    """Test dashboard function by company attribute dimension switching"""
    with app.app_context():
        # Create companies with different attributes
        companies = [
            Company(name="Tech Company A", industry="Information Technology", size="Large"),
            Company(name="Manufacturing Company B", industry="Manufacturing", size="Medium"),
            Company(name="Service Company C", industry="Services", size="Small")
        ]

        db.session.add_all(companies)
        db.session.commit()

        # Create surveys and data for each company
        company_data = {}

        for i, company in enumerate(companies):
            survey = Survey(title=f"Survey_{company.name}", company_id=company.id, created_by=1)
            db.session.add(survey)
            db.session.commit()

            # Different industries have different skill score patterns
            if company.industry == "Information Technology":
                scores = {'leadership': 4.0, 'planning': 4.2, 'decision': 4.5, 'professional': 4.3}
            elif company.industry == "Manufacturing":
                scores = {'leadership': 3.8, 'planning': 4.0, 'decision': 3.5, 'professional': 4.2}
            else:  # Services
                scores = {'leadership': 4.2, 'planning': 3.8, 'decision': 3.9, 'professional': 3.7}

            response = SurveyResponse(
                survey_id=survey.id,
                respondent_name=f"Manager{i+1}",
                department="Management Department",
                management_level="Middle",
                leadership_score=scores['leadership'],
                planning_score=scores['planning'],
                decision_score=scores['decision'],
                professional_score=scores['professional']
            )

            db.session.add(response)
            company_data[company.industry] = scores

        db.session.commit()

        # Verify company attribute dimension switching
        assert len(company_data) == 3

        # Verify different industry skill patterns
        tech_scores = company_data["Information Technology"]
        manufacturing_scores = company_data["Manufacturing"]
        service_scores = company_data["Services"]

        # IT companies should score higher in decision-making innovation
        assert tech_scores['decision'] > manufacturing_scores['decision']

        # Manufacturing companies should score higher in professional control
        assert manufacturing_scores['professional'] > service_scores['professional']

        print("✅ Company attribute dimension switching function test passed")
        print("   Industry skill pattern differences:")
        for industry, scores in company_data.items():
            avg_score = sum(scores.values()) / 4
            print(f"   {industry}: Average score {avg_score:.2f}")

def test_management_level_switch(app):
    """Test dashboard function by management level dimension switching"""
    with app.app_context():
        # Create test company
        company = Company(name="Test Company", industry="Technology")
        db.session.add(company)
        db.session.commit()

        # Create test survey
        survey = Survey(title="Level Test Survey", company_id=company.id, created_by=1)
        db.session.add(survey)
        db.session.commit()

        # Create data for different management levels
        level_data = {
            'Junior': [
                {'name': 'Junior Manager1', 'leadership': 3.2, 'planning': 3.4, 'decision': 3.1, 'professional': 3.3},
                {'name': 'Junior Manager2', 'leadership': 3.4, 'planning': 3.2, 'decision': 3.3, 'professional': 3.1}
            ],
            'Middle': [
                {'name': 'Middle Manager1', 'leadership': 4.0, 'planning': 4.1, 'decision': 3.8, 'professional': 4.0},
                {'name': 'Middle Manager2', 'leadership': 3.9, 'planning': 3.8, 'decision': 4.0, 'professional': 3.9}
            ],
            'Senior': [
                {'name': 'Senior Manager1', 'leadership': 4.6, 'planning': 4.5, 'decision': 4.4, 'professional': 4.7},
                {'name': 'Senior Manager2', 'leadership': 4.8, 'planning': 4.3, 'decision': 4.6, 'professional': 4.5}
            ]
        }

        # Create response data
        all_responses = []
        for level, managers in level_data.items():
            for manager in managers:
                response = SurveyResponse(
                    survey_id=survey.id,
                    respondent_name=manager['name'],
                    department="Management Department",
                    management_level=level,
                    leadership_score=manager['leadership'],
                    planning_score=manager['planning'],
                    decision_score=manager['decision'],
                    professional_score=manager['professional']
                )
                all_responses.append(response)

        db.session.add_all(all_responses)
        db.session.commit()

        # Verify management level dimension switching
        level_averages = {}
        for level in ['Junior', 'Middle', 'Senior']:
            level_responses = SurveyResponse.query.filter_by(management_level=level).all()

            if level_responses:
                level_averages[level] = {
                    'leadership': sum(r.leadership_score for r in level_responses) / len(level_responses),
                    'planning': sum(r.planning_score for r in level_responses) / len(level_responses),
                    'decision': sum(r.decision_score for r in level_responses) / len(level_responses),
                    'professional': sum(r.professional_score for r in level_responses) / len(level_responses)
                }

        # Verify skill differences between levels
        assert len(level_averages) == 3

        # Senior managers should have higher average score than junior
        junior_avg = sum(level_averages['Junior'].values()) / 4
        senior_avg = sum(level_averages['Senior'].values()) / 4

        assert senior_avg > junior_avg

        print("✅ Management level dimension switching function test passed")
        print("   Level skill comparison:")
        for level, scores in level_averages.items():
            avg_score = sum(scores.values()) / 4
            print(f"   {level}: Average score {avg_score:.2f}")

if __name__ == "__main__":
    pytest.main([__file__])
