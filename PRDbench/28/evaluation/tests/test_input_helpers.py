# -*- coding: utf-8 -*-
"""
Inputhelper/auxiliaryToolunitTest
"""

import pytest
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from utils.input_helpers import InputHelper


class TestInputHelper:
 """Inputhelper/auxiliaryToolTestclass"""
 
 def setup_method(self):
 """Setup before test"""
 self.input_helper = InputHelper()
 
 def test_format_currency_default_unit(self):
 """Test currency format - default unit"""
 result = self.input_helper.format_currency(1000.0)
 assert result == "1,000.00thousand yuan"

 def test_format_currency_custom_unit(self):
 """Test currency format - custom unit"""
 result = self.input_helper.format_currency(5000.0, "yuan")
 assert result == "5,000.00yuan"
 
 def test_format_currency_small_amount(self):
 """Test currency format - small amount"""
 result = self.input_helper.format_currency(123.45)
 assert result == "123.45thousand yuan"

 def test_format_currency_zero(self):
 """Test currency format - zero amount"""
 result = self.input_helper.format_currency(0.0)
 assert result == "0.00thousand yuan"

 def test_format_currency_negative(self):
 """Test currency format - negative number"""
 result = self.input_helper.format_currency(-1000.0)
 assert result == "-1,000.00thousand yuan"

 def test_format_currency_large_amount(self):
 """Test currency format - large amount"""
 result = self.input_helper.format_currency(1234567.89)
 assert result == "1,234,567.89thousand yuan"

 def test_format_percentage_normal(self):
 """Test percentage format - normal ratio"""
 result = self.input_helper.format_percentage(0.15)
 assert result == "15.0%"

 def test_format_percentage_zero(self):
 """Test percentage format - zero ratio"""
 result = self.input_helper.format_percentage(0.0)
 assert result == "0.0%"

 def test_format_percentage_one(self):
 """Test percentage format - 100%"""
 result = self.input_helper.format_percentage(1.0)
 assert result == "100.0%"

 def test_format_percentage_greater_than_one(self):
 """Test percentage format - greater than 100%"""
 result = self.input_helper.format_percentage(1.5)
 assert result == "150.0%"

 def test_format_percentage_small_decimal(self):
 """Test percentage format - small decimal"""
 result = self.input_helper.format_percentage(0.123456)
 assert result == "12.3%"

 def test_truncate_text_short_text(self):
 """Test text truncate - short text"""
 text = "Short text"
 result = self.input_helper.truncate_text(text, 10)
 assert result == "Short text"

 def test_truncate_text_exact_length(self):
 """Test text truncate - exact length"""
 text = "Exactly ten characters text content"
 result = self.input_helper.truncate_text(text, 10)
 assert result == "Exactly ten characters text content"

 def test_truncate_text_long_text(self):
 """Test text truncate - long text"""
 text = "This is a very long text content, needs to be truncated"
 result = self.input_helper.truncate_text(text, 10)
 assert result == "This is a ..."
 assert len(result) == 10

 def test_truncate_text_english(self):
 """Test text truncate - English text"""
 text = "This is a very long English text that needs to be truncated"
 result = self.input_helper.truncate_text(text, 20)
 assert result == "This is a very lo..."
 assert len(result) == 20

 def test_truncate_text_mixed_language(self):
 """Test text truncate - English mixed"""
 text = "This is English mixed text very long content"
 result = self.input_helper.truncate_text(text, 15)
 assert result == "This is English..."
 assert len(result) == 15

 def test_truncate_text_empty_string(self):
 """Test text truncate - empty string"""
 result = self.input_helper.truncate_text("", 10)
 assert result == ""

 def test_truncate_text_custom_max_length(self):
 """Test text truncate - custom max length"""
 text = "Test custom length truncate function text content"
 result = self.input_helper.truncate_text(text, 8)
 assert result == "Test cus..."
 assert len(result) == 8

 def test_truncate_text_very_short_limit(self):
 """Test text truncate - extremely short limit"""
 text = "Test text"
 result = self.input_helper.truncate_text(text, 3)
 assert result == "..."
 assert len(result) == 3

 def test_truncate_text_boundary_cases(self):
 """Test text truncate - boundary case"""
 # Length is 4 case (exactly equals ... length plus 1)
 text = "Test boundary case text"
 result = self.input_helper.truncate_text(text, 4)
 assert result == "Test..."
 assert len(result) == 4

 def test_format_functions_with_none_input(self):
 """Test format function processing None input"""
 # These functions usually should not receive None, but test exception handling
 with pytest.raises((TypeError, AttributeError)):
 self.input_helper.truncate_text(None, 10)

 def test_format_currency_precision(self):
 """Test currency format precision"""
 # Test keep two decimal places
 result1 = self.input_helper.format_currency(123.4)
 assert result1 == "123.40thousand yuan"

 result2 = self.input_helper.format_currency(123.456789)
 assert result2 == "123.46thousand yuan" # Round to nearest

 def test_format_percentage_precision(self):
 """Test percentage format precision"""
 # Test keep one decimal place
 result1 = self.input_helper.format_percentage(0.123)
 assert result1 == "12.3%"

 result2 = self.input_helper.format_percentage(0.12789)
 assert result2 == "12.8%" # Round to nearest


if __name__ == "__main__":
 pytest.main([__file__])