

import pytest
import sys
import os
from unittest.mock import patch

# Add src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Now import the functions
from cost_calculator import calculate_ingredient_cost, calculate_combo_cost

# Mock data that the data_manager would normally provide
MOCK_INGREDIENTS = {
    "wuchang_rice": {'purchase_price': 10, 'processing_loss_rate': 10, 'unit': 'kg'},
    "chicken_breast": {'purchase_price': 15, 'processing_loss_rate': 5, 'unit': 'kg'},
    "zero_loss_ingredient": {'purchase_price': 20, 'processing_loss_rate': 0, 'unit': 'kg'},
}

MOCK_EXTRA_COSTS = {
    "packaging_box": 1.5,
    "disposable_utensils": 0.8
}

@pytest.fixture
def mock_data_manager():
    """Pytest fixture to mock the data_manager functions."""
    with patch('cost_calculator.find_ingredient_by_name', side_effect=lambda name: MOCK_INGREDIENTS.get(name)), \
         patch('cost_calculator.get_extra_costs', return_value=MOCK_EXTRA_COSTS):
        yield

# Metric: 2.2.1 Single ingredient cost calculation (with boundary conditions)
@pytest.mark.parametrize("name, usage, expected_cost", [
    ("wuchang_rice", 0.15, 1.65),      # Standard case from metric
    ("chicken_breast", 0.2, 3.15),     # Another standard case
    ("zero_loss_ingredient", 1, 20.0), # Boundary: Zero waste loss
    ("wuchang_rice", 0, 0.0),          # Boundary: Zero quantity
    ("nonexistent_ingredient", 0.1, 0.0),  # Edge: Ingredient not found
])
def test_calculate_ingredient_cost(mock_data_manager, name, usage, expected_cost):
    cost, _ = calculate_ingredient_cost(name, usage)
    assert cost == pytest.approx(expected_cost)

# Metric: 2.2.2a Total cost calculation - cost summary
def test_calculate_combo_cost(mock_data_manager):
    ingredients_list = [
        {'name': 'wuchang_rice', 'usage': 0.15}, # Cost: 1.65
        {'name': 'chicken_breast', 'usage': 0.35}  # Cost: 5.5125 -> 5.51
    ]
    extra_cost_names = ["packaging_box"] # Cost: 1.5
    # Expected: 1.65 + 5.51 + 1.5 = 8.66

    total_cost, _, _ = calculate_combo_cost(ingredients_list, extra_cost_names)
    assert total_cost == pytest.approx(8.66)

def test_calculate_combo_cost_with_all_extras(mock_data_manager):
    ingredients_list = [{'name': 'wuchang_rice', 'usage': 0.15}] # Cost: 1.65
    extra_cost_names = ["packaging_box", "disposable_utensils"] # Cost: 1.5 + 0.8 = 2.3
    # Expected: 1.65 + 2.3 = 3.95

    total_cost, _, _ = calculate_combo_cost(ingredients_list, extra_cost_names)
    assert total_cost == pytest.approx(3.95)

def test_calculate_combo_cost_no_extras(mock_data_manager):
    ingredients_list = [{'name': 'wuchang_rice', 'usage': 0.15}] # Cost: 1.65
    extra_cost_names = []
    # Expected: 1.65

    total_cost, _, _ = calculate_combo_cost(ingredients_list, extra_cost_names)
    assert total_cost == pytest.approx(1.65)

