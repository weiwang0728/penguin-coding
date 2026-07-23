"""
Scale Import Export Functional Test
"""
import pytest
import sys
import json
import pandas as pd
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

@pytest.fixture
def test_scale_json_file():
    """Create test JSON scale file"""
    test_data = {
        "name": "JSON Test Scale",
        "description": "Test scale imported from JSON",
        "version": "1.0",
        "config": {
            "scoring_method": "likert_7",
            "dimensions": ["Dimension 1", "Dimension 2"],
            "scoring_range": [1, 7],
            "higher_better": True
        },
        "items": [
            {
                "item_number": 1,
                "content": "Test item 1",
                "dimension": "Dimension 1",
                "is_reverse": False
            },
            {
                "item_number": 2,
                "content": "Test item 2",
                "dimension": "Dimension 2",
                "is_reverse": True
            }
        ]
    }

    test_file = Path("evaluation/temp_test_scale.json")
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    yield test_file

    # Clean up
    if test_file.exists():
        test_file.unlink()

@pytest.fixture
def test_scale_csv_file():
    """Create test CSV scale file"""
    test_data = {
        'item_number': [1, 2, 3],
        'content': ['CSV Test Item 1', 'CSV Test Item 2', 'CSV Test Item 3'],
        'dimension': ['Dimension A', 'Dimension B', 'Dimension A'],
        'is_reverse': [False, True, False]
    }

    test_file = Path("evaluation/temp_test_scale.csv")
    df = pd.DataFrame(test_data)
    df.to_csv(test_file, index=False, encoding='utf-8')

    yield test_file

    # Clean up
    if test_file.exists():
        test_file.unlink()

def test_import_scale_json(scale_manager, test_scale_json_file):
    """Test import scale from JSON file"""
    # Execute import
    scale = scale_manager.import_scale_from_json(test_scale_json_file)

    # Assert
    assert scale is not None, "JSON scale import failed"
    assert scale.name == "JSON Test Scale", f"Scale name does not match, expected: JSON Test Scale, actual: {scale.name}"
    assert scale.description == "Test scale imported from JSON", "Scale description does not match"
    assert len(scale.items) == 2, f"Item quantity does not match, expected: 2, actual: {len(scale.items)}"

    # Verify item content
    items = sorted(scale.items, key=lambda x: x.item_number)
    assert items[0].content == "Test item 1", "First item content does not match"
    assert items[0].dimension == "Dimension 1", "First item dimension does not match"
    assert items[0].is_reverse == False, "First item reverse scoring setting does not match"

    assert items[1].content == "Test item 2", "Second item content does not match"
    assert items[1].dimension == "Dimension 2", "Second item dimension does not match"
    assert items[1].is_reverse == True, "Second item reverse scoring setting does not match"

    # Verify configuration
    expected_config = {
        "scoring_method": "likert_7",
        "dimensions": ["Dimension 1", "Dimension 2"],
        "scoring_range": [1, 7],
        "higher_better": True
    }
    assert scale.config == expected_config, "Scale configuration does not match"

def test_import_scale_csv(scale_manager, test_scale_csv_file):
    """Test import scale from CSV file"""
    # Execute import
    scale = scale_manager.import_scale_from_csv(test_scale_csv_file)

    # Assert
    assert scale is not None, "CSV scale import failed"
    assert len(scale.items) == 3, f"Item quantity does not match, expected: 3, actual: {len(scale.items)}"

    # Verify item content
    items = sorted(scale.items, key=lambda x: x.item_number)
    assert items[0].content == "CSV Test Item 1", "First item content does not match"
    assert items[1].content == "CSV Test Item 2", "Second item content does not match"
    assert items[2].content == "CSV Test Item 3", "Third item content does not match"

    # Verify dimensions
    assert items[0].dimension == "Dimension A", "First item dimension does not match"
    assert items[1].dimension == "Dimension B", "Second item dimension does not match"
    assert items[2].dimension == "Dimension A", "Third item dimension does not match"

    # Verify reverse scoring
    assert items[0].is_reverse == False, "First item reverse scoring setting does not match"
    assert items[1].is_reverse == True, "Second item reverse scoring setting does not match"
    assert items[2].is_reverse == False, "Third item reverse scoring setting does not match"

def test_export_scale_csv(scale_manager):
    """Test export scale in CSV format"""
    # Create test scale
    items = [
        {'item_number': 1, 'content': 'Export Test Item 1', 'dimension': 'Dimension X', 'is_reverse': False},
        {'item_number': 2, 'content': 'Export Test Item 2', 'dimension': 'Dimension Y', 'is_reverse': True}
    ]

    scale = scale_manager.create_scale(
        name="Export Test Scale",
        description="For testing export function",
        items=items
    )

    # Execute export
    output_path = Path("evaluation/temp_exported_scale.csv")
    success = scale_manager.export_scale_to_csv(scale.id, output_path)

    try:
        # Assert
        assert success == True, "CSV export failed"
        assert output_path.exists(), "Exported CSV file does not exist"

        # Verify export content
        df = pd.read_csv(output_path)
        assert len(df) == 2, f"Exported item quantity does not match, expected: 2, actual: {len(df)}"
        assert 'item_number' in df.columns, "Missing item_number column"
        assert 'content' in df.columns, "Missing content column"
        assert 'dimension' in df.columns, "Missing dimension column"
        assert 'is_reverse' in df.columns, "Missing is_reverse column"

        # Verify specific content
        assert df.iloc[0]['content'] == 'Export Test Item 1', "First item content does not match"
        assert df.iloc[1]['content'] == 'Export Test Item 2', "Second item content does not match"

    finally:
        # Clean up
        if output_path.exists():
            output_path.unlink()

def test_export_scale_json(scale_manager):
    """Test export scale in JSON format"""
    # Create test scale
    items = [
        {'item_number': 1, 'content': 'JSON Export Test Item 1', 'dimension': 'Dimension A', 'is_reverse': False},
        {'item_number': 2, 'content': 'JSON Export Test Item 2', 'dimension': 'Dimension B', 'is_reverse': True}
    ]

    config = {
        'scoring_method': 'likert_5',
        'dimensions': ['Dimension A', 'Dimension B']
    }

    scale = scale_manager.create_scale(
        name="JSON Export Test Scale",
        description="For testing JSON export function",
        items=items,
        config=config
    )

    # Execute export
    output_path = Path("evaluation/temp_exported_scale.json")
    success = scale_manager.export_scale_to_json(scale.id, output_path)

    try:
        # Assert
        assert success == True, "JSON export failed"
        assert output_path.exists(), "Exported JSON file does not exist"

        # Verify export content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['name'] == "JSON Export Test Scale", "Exported scale name does not match"
        assert data['description'] == "For testing JSON export function", "Exported scale description does not match"
        assert len(data['items']) == 2, f"Exported item quantity does not match, expected: 2, actual: {len(data['items'])}"
        assert data['config'] == config, "Exported configuration does not match"

        # Verify item content
        items_data = sorted(data['items'], key=lambda x: x['item_number'])
        assert items_data[0]['content'] == 'JSON Export Test Item 1', "First item content does not match"
        assert items_data[1]['content'] == 'JSON Export Test Item 2', "Second item content does not match"

    finally:
        # Clean up
        if output_path.exists():
            output_path.unlink()

def test_scale_list_and_retrieval(scale_manager):
    """Test scale list and retrieval function"""
    # Create multiple test scales
    scale1 = scale_manager.create_scale(name="List Test Scale 1", description="First test scale")
    scale2 = scale_manager.create_scale(name="List Test Scale 2", description="Second test scale")

    # Test list function
    scales = scale_manager.list_scales()
    assert len(scales) >= 2, f"Scale quantity insufficient, expected at least 2, actual: {len(scales)}"

    # Test retrieve by name
    retrieved_scale1 = scale_manager.get_scale_by_name("List Test Scale 1")
    assert retrieved_scale1 is not None, "Retrieve scale by name failed"
    assert retrieved_scale1.id == scale1.id, "Retrieved scale ID does not match"

    # Test retrieve by ID
    retrieved_scale2 = scale_manager.get_scale(scale2.id)
    assert retrieved_scale2 is not None, "Retrieve scale by ID failed"
    assert retrieved_scale2.name == "List Test Scale 2", "Retrieved scale name does not match"
