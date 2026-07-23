
import pytest
import sys
import os
import shutil

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Correctly import the function
from combo_generator import generate_combos
from data_manager import find_ingredient_by_name # We need this for assertions

# Define paths for test data
TEST_DATA_DIR = os.path.dirname(__file__)
APP_DATA_DIR = os.path.abspath(os.path.join(TEST_DATA_DIR, '../../src/data'))
APP_INGREDIENTS_FILE = os.path.join(APP_DATA_DIR, 'ingredients.csv')

@pytest.fixture
def setup_test_ingredients():
    """
    Fixture to replace the main ingredients file with a test version
    before a test, and restore it afterwards.
    """
    # Backup original file if it exists
    original_file_backup = APP_INGREDIENTS_FILE + ".bak"
    if os.path.exists(APP_INGREDIENTS_FILE):
        shutil.copy(APP_INGREDIENTS_FILE, original_file_backup)

    # Copy test data to the location the app uses
    test_ingredients_src = os.path.join(TEST_DATA_DIR, '../ingredients_for_test_2.3.2.csv')
    shutil.copy(test_ingredients_src, APP_INGREDIENTS_FILE)

    yield # This is where the test runs

    # Teardown: Restore the original file
    if os.path.exists(original_file_backup):
        shutil.move(original_file_backup, APP_INGREDIENTS_FILE)
    elif os.path.exists(APP_INGREDIENTS_FILE):
        # If there was no original file, clean up the one we created
        os.remove(APP_INGREDIENTS_FILE)


def test_combo_generation_nutrition_constraints(setup_test_ingredients):
    """
    Tests that all generated combos adhere to the nutritional constraints.
    Metric: 2.3.2 Core combination logic and nutrition constraints
    """
    # Arrange: The fixture has already prepared the data file.

    # Act: Call the function directly. It will now read our test data.
    combos = generate_combos(
        combo_type='single_meal',
        discount=0.9,
        stock_priority='high',
        target_profit_rate=0.3
    )

    # Assert
    assert combos is not None, "Combo generation failed, returned None"
    assert len(combos) > 0, "No candidate combos generated"

    for combo in combos:
        ingredients = combo['ingredients']

        # Get the full ingredient details using the real data_manager function
        full_ingredient_details = [find_ingredient_by_name(item['name']) for item in ingredients]

        # Check for presence and quantity of each category
        has_main = any(ing['category'] == 'staple' and next(item['usage'] for item in ingredients if item['name'] == ing['name']) >= 0.1 for ing in full_ingredient_details if ing)
        has_protein = any(ing['category'] == 'protein' and next(item['usage'] for item in ingredients if item['name'] == ing['name']) >= 0.08 for ing in full_ingredient_details if ing)
        has_veg = any(ing['category'] == 'vegetable' and next(item['usage'] for item in ingredients if item['name'] == ing['name']) >= 0.1 for ing in full_ingredient_details if ing)

        assert has_main, "Combo missing staple or insufficient quantity"
        assert has_protein, "Combo missing protein or insufficient quantity"
        assert has_veg, "Combo missing vegetable or insufficient quantity"

