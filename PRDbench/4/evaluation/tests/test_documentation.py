

import os
import pandas as pd
import pytest

# Define the absolute path to the project's root directory
# This is a common approach in tests to make pathing reliable
# We assume the test is run from the root of the project.
# A more robust solution might use a library to find the project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_csv_template_existence_and_headers():
    """
    Tests that the template.csv file exists and has the correct headers.
    """
    # 1. Define the path to the CSV file
    template_path = os.path.join(PROJECT_ROOT, 'src', 'data', 'template.csv')

    # 2. Assert that the file exists
    assert os.path.exists(template_path), f"CSV template file not found at {template_path}"

    # 3. Define the expected headers based on the PRD
    expected_headers = [
        'project_name', 'city', 'area', 'business_circle_type', 'longitude', 'latitude',
        'category1_name', 'category1_ratio', 'category2_name', 'category2_ratio',
        'category3_name', 'category3_ratio', 'avg_item_price', 'ingredient_cost_ratio',
        'packaging_cost_ratio', 'monthly_rent', 'monthly_labor_cost',
        'monthly_marketing_cost', 'commission_rate'
    ]

    # 4. Read the CSV and get its headers
    try:
        df = pd.read_csv(template_path)
        actual_headers = df.columns.tolist()
    except Exception as e:
        pytest.fail(f"Failed to read or parse the CSV file: {e}")

    # 5. Assert that the headers match
    assert actual_headers == expected_headers, (
        f"CSV headers do not match the expected headers.\n"
        f"Expected: {expected_headers}\n"
        f"Actual:   {actual_headers}"
    )

