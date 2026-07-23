"""
Scale Creation Functional Test
"""
import pytest
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scale_manager import ScaleManager
from models import create_tables

@pytest.fixture
def scale_manager():
    """Create scale manager instance"""
    create_tables()
    return ScaleManager()

def test_create_scale_basic_info(scale_manager):
    """Test scale basic information creation"""
    # Prepare test data
    scale_name = "Test Scale"
    scale_description = "This is a test scale"
    scale_version = "1.0"

    # Execute creation operation
    scale = scale_manager.create_scale(
        name=scale_name,
        description=scale_description,
        version=scale_version
    )

    # Assert
    assert scale is not None, "Scale creation failed"
    assert scale.name == scale_name, f"Scale name does not match, expected: {scale_name}, actual: {scale.name}"
    assert scale.description == scale_description, f"Scale description does not match"
    assert scale.version == scale_version, f"Scale version does not match"
    assert scale.id is not None, "Scale ID should not be empty"

    # Verify scale can be retrieved
    retrieved_scale = scale_manager.get_scale(scale.id)
    assert retrieved_scale is not None, "Cannot retrieve created scale"
    assert retrieved_scale.name == scale_name, "Retrieved scale name does not match"

def test_create_scale_with_items(scale_manager):
    """Test create scale with items"""
    # Prepare test data
    scale_name = "Test Scale with Items"
    scale_description = "Test scale containing multiple items"

    items = [
        {
            'item_number': 1,
            'content': 'I can maintain attention for a long time',
            'dimension': 'Attention Sustaining',
            'is_reverse': False
        },
        {
            'item_number': 2,
            'content': 'I am easily distracted',
            'dimension': 'Attention Focus',
            'is_reverse': True
        },
        {
            'item_number': 3,
            'content': 'I can control my attention',
            'dimension': 'Attention Control',
            'is_reverse': False
        }
    ]

    config = {
        'scoring_method': 'likert_7',
        'dimensions': ['Attention Sustaining', 'Attention Focus', 'Attention Control'],
        'scoring_range': [1, 7],
        'higher_better': True
    }

    # Execute creation operation
    scale = scale_manager.create_scale(
        name=scale_name,
        description=scale_description,
        items=items,
        config=config
    )

    # Assert
    assert scale is not None, "Scale creation failed"
    assert scale.name == scale_name, "Scale name does not match"
    assert len(scale.items) == 3, f"Item quantity does not match, expected: 3, actual: {len(scale.items)}"

    # Verify item content
    scale_items = sorted(scale.items, key=lambda x: x.item_number)

    for i, expected_item in enumerate(items):
        actual_item = scale_items[i]
        assert actual_item.item_number == expected_item['item_number'], f"Item {i+1} number does not match"
        assert actual_item.content == expected_item['content'], f"Item {i+1} content does not match"
        assert actual_item.dimension == expected_item['dimension'], f"Item {i+1} dimension does not match"
        assert actual_item.is_reverse == expected_item['is_reverse'], f"Item {i+1} reverse scoring setting does not match"

    # Verify configuration
    assert scale.config == config, "Scale configuration does not match"

def test_scale_validation():
    """Test scale data validation"""
    scale_manager_instance = ScaleManager()

    # Test empty name
    with pytest.raises(Exception):
        scale_manager_instance.create_scale(name="", description="Test")

    # Test duplicate name
    scale_manager_instance.create_scale(name="Duplicate Test Scale", description="First one")

    # Creating scale with same name should succeed (system allows duplicate scale names)
    scale2 = scale_manager_instance.create_scale(name="Duplicate Test Scale", description="Second one")
    assert scale2 is not None, "Duplicate scale name creation should succeed"

def test_scale_statistics(scale_manager):
    """Test scale statistics information"""
    # Create test scale
    items = [
        {'item_number': 1, 'content': 'Test item 1', 'dimension': 'Dimension 1', 'is_reverse': False},
        {'item_number': 2, 'content': 'Test item 2', 'dimension': 'Dimension 1', 'is_reverse': True},
        {'item_number': 3, 'content': 'Test item 3', 'dimension': 'Dimension 2', 'is_reverse': False}
    ]

    scale = scale_manager.create_scale(
        name="Statistics Test Scale",
        description="For testing statistics function",
        items=items
    )

    # Get statistics information
    stats = scale_manager.get_scale_statistics(scale.id)

    # Assert
    assert stats is not None, "Statistics information retrieval failed"
    assert stats['scale_name'] == "Statistics Test Scale", "Scale name does not match"
    assert stats['total_items'] == 3, f"Item quantity does not match, expected: 3, actual: {stats['total_items']}"
    assert len(stats['dimensions']) == 2, f"Dimension quantity does not match, expected: 2, actual: {len(stats['dimensions'])}"
    assert stats['reverse_items'] == 1, f"Reverse item quantity does not match, expected: 1, actual: {stats['reverse_items']}"
    assert 'created_at' in stats, "Missing creation time information"
    assert 'updated_at' in stats, "Missing update time information"
