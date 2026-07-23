import pytest
import os
import json
from src.utils import validate_chinese_name, is_valid_date, is_future_date, calculate_bazi_wuxing

# --- 1.1 User Information Entry Flow - Name Input ---
def test_validate_chinese_name_valid():
    assert validate_chinese_name("Zhang San") == True
    assert validate_chinese_name("John Doe") == True
    assert validate_chinese_name("Li Si") == True
    assert validate_chinese_name("Wang Wu Zhao Liu") == True

def test_validate_chinese_name_invalid():
    assert validate_chinese_name("A") == False  # Too short
    assert validate_chinese_name("VeryLongNameThatExceedsTwentyCharactersLimit") == False  # Too long (Chinese)
    assert validate_chinese_name("VeryLongNameThatExceedsTwentyCharactersLimit") == False  # Too long (English)
    assert validate_chinese_name("A") == False  # Too short

# --- 1.2 User Information Entry Flow - Birth Date Input ---
def test_is_valid_date():
    assert is_valid_date(1990, 1, 1) == True
    assert is_valid_date(1990, 13, 1) == False  # Invalid month
    assert is_valid_date(1990, 2, 30) == False  # Invalid date

def test_is_future_date():
    from datetime import date
    # Assuming today is 2023-10-27, test a future date
    future_date = date.today().replace(year=date.today().year + 1)
    assert is_future_date(future_date.year, future_date.month, future_date.day) == True
    # Test a past date
    assert is_future_date(1990, 1, 1) == False

# --- 4.1a Fortune Comprehensive Calculation - BaZi Five Elements Calculation ---
# This test verifies the basic logic of BaZi calculation, not pursuing absolute precision (as PRD mentions simplified version)
def test_calculate_bazi_wuxing():
    result = calculate_bazi_wuxing(1990, 1, 1)
    bazi = result['bazi']
    wuxing_dist = result['wuxing_distribution']

    # Verify return structure
    assert 'year' in bazi
    assert 'month' in bazi
    assert 'day' in bazi
    assert 'hour' in bazi
    assert set(wuxing_dist.keys()) == {'Metal', 'Wood', 'Water', 'Fire', 'Earth'}

    # Verify Five Elements distribution are numeric values
    for value in wuxing_dist.values():
        assert isinstance(value, (int, float))

# --- 1.4 User Information Storage and Loading ---
# This test is more suitable for shell_interaction testing as it involves file I/O and complete program flow
# But we can test the core part of save/load logic
def test_user_data_save_load_logic():
    # Note: This test assumes it's safe to write and read files in the test environment
    # In actual pytest environment, may need to use tmp_path fixture
    test_data = {
        'name': 'Test User',
        'birth_date': '1990-01-01',
        'gender': 'Male'
    }

    # To avoid polluting source code directory, create temp file in current test directory
    # In actual pytest, should use tmp_path
    test_file = 'test_user_data.json'

    try:
        # Simulate save
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=4)

        # Simulate load
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        assert loaded_data == test_data
    finally:
        # Cleanup temp file
        if os.path.exists(test_file):
            os.remove(test_file)