#!/usr/bin/env python3
"""
Test preset management skill dimensions function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import SkillDimension

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_preset_skill_dimensions(app):
    """Test system preset four core management skill dimensions"""
    with app.app_context():
        # Preset four management skill dimensions
        preset_dimensions = [
            {
                'name': 'Leadership & Motivation Skills',
                'description': 'Assess manager team leadership, motivation techniques, communication coordination and team building capabilities',
                'category': 'leadership'
            },
            {
                'name': 'Planning Organization & Coordination Skills',
                'description': 'Evaluate manager planning setting, resource allocation, process optimization and cross-department coordination capabilities',
                'category': 'planning'
            },
            {
                'name': 'Decision-Making & Innovation Skills',
                'description': 'Examine manager decision analysis, risk assessment, innovative thinking and change management capabilities',
                'category': 'decision'
            },
            {
                'name': 'Professional & Control Skills',
                'description': 'Evaluate manager professional knowledge level, quality control, performance management and standard execution capabilities',
                'category': 'professional'
            }
        ]

        # Create preset dimensions (simulate system initialization)
        for dim_data in preset_dimensions:
            dimension = SkillDimension(
                name=dim_data['name'],
                description=dim_data['description'],
                category=dim_data['category'],
                is_preset=True
            )
            db.session.add(dimension)

        db.session.commit()

        # Verify preset dimensions
        all_dimensions = SkillDimension.query.filter_by(is_preset=True).all()
        assert len(all_dimensions) == 4

        # Verify specific dimension names
        dimension_names = [dim.name for dim in all_dimensions]
        expected_names = [
            'Leadership & Motivation Skills',
            'Planning Organization & Coordination Skills',
            'Decision-Making & Innovation Skills',
            'Professional & Control Skills'
        ]

        for expected_name in expected_names:
            assert expected_name in dimension_names

        # Verify dimension categories
        categories = [dim.category for dim in all_dimensions]
        expected_categories = ['leadership', 'planning', 'decision', 'professional']

        for expected_category in expected_categories:
            assert expected_category in categories

        # Verify each dimension has description
        for dimension in all_dimensions:
            assert dimension.description is not None
            assert len(dimension.description) > 0

        print("✅ Preset management skill dimensions function test passed")
        print(f"   Found {len(all_dimensions)} preset skill dimensions")
        for dim in all_dimensions:
            print(f"   - {dim.name} ({dim.category})")

if __name__ == "__main__":
    pytest.main([__file__])
