#!/usr/bin/env python3
"""
Test Custom Dimension and Indicator Definition Function
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from app import create_app, db
from app.models import SkillDimension, DimensionIndicator

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_add_custom_dimension(app):
    """Test add custom skill dimension function"""
    with app.app_context():
        # Add custom dimension
        custom_dimension = SkillDimension(
            name="Communication Skills",
            description="Assess manager's verbal expression, written communication, listening skills and cross-cultural communication ability",
            category="communication",
            is_preset=False
        )

        db.session.add(custom_dimension)
        db.session.commit()

        # Verify dimension has been added
        saved_dimension = SkillDimension.query.filter_by(name="Communication Skills").first()
        assert saved_dimension is not None
        assert saved_dimension.name == "Communication Skills"
        assert saved_dimension.category == "communication"
        assert saved_dimension.is_preset == False

        # Verify can query custom dimension
        custom_dimensions = SkillDimension.query.filter_by(is_preset=False).all()
        assert len(custom_dimensions) == 1
        assert custom_dimensions[0].name == "Communication Skills"

        print("✅ Custom skill dimension add function test passed")

def test_add_dimension_indicators(app):
    """Test add indicators and weights to dimension function"""
    with app.app_context():
        # First create custom dimension
        custom_dimension = SkillDimension(
            name="Communication Skills",
            description="Assess manager communication skills",
            category="communication",
            is_preset=False
        )
        db.session.add(custom_dimension)
        db.session.commit()

        # Add indicators to dimension
        indicators = [
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="Verbal Expression Ability",
                description="Clear and accurate expression of ideas and instructions ability",
                weight=0.3
            ),
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="Written Communication Ability",
                description="Writing clear and professional documents and emails ability",
                weight=0.25
            ),
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="Listening Skills",
                description="Effective listening to others' opinions and feedback ability",
                weight=0.25
            ),
            DimensionIndicator(
                dimension_id=custom_dimension.id,
                name="Cross-Department Coordination",
                description="Effective cooperation and communication with other departments ability",
                weight=0.2
            )
        ]

        db.session.add_all(indicators)
        db.session.commit()

        # Verify indicators have been added
        saved_indicators = DimensionIndicator.query.filter_by(dimension_id=custom_dimension.id).all()
        assert len(saved_indicators) == 4

        # Verify weight sum
        total_weight = sum(indicator.weight for indicator in saved_indicators)
        assert abs(total_weight - 1.0) < 0.01  # Weight sum should be close to 1.0

        # Verify all indicators
        indicator_names = [indicator.name for indicator in saved_indicators]
        expected_names = ["Verbal Expression Ability", "Written Communication Ability", "Listening Skills", "Cross-Department Coordination"]

        for expected_name in expected_names:
            assert expected_name in indicator_names

        # Verify indicator weights
        for indicator in saved_indicators:
            assert 0 < indicator.weight <= 1.0
            assert indicator.description is not None

        # Test query dimension configuration details
        dimension_with_indicators = SkillDimension.query.filter_by(name="Communication Skills").first()
        related_indicators = DimensionIndicator.query.filter_by(dimension_id=dimension_with_indicators.id).all()

        assert len(related_indicators) == 4

        print("✅ Dimension indicator and weight configuration function test passed")
        print(f"   Dimension: {dimension_with_indicators.name}")
        print(f"   Indicator count: {len(related_indicators)}")
        for indicator in related_indicators:
            print(f"   - {indicator.name}: {indicator.weight}")

if __name__ == "__main__":
    pytest.main([__file__])
