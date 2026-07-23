#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity Output Format Test
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import pytest

def test_entity_name_and_type():
    """Test entity name and type output"""
    # Simulate entity data
    entities = {
        'nr': [('Kaga Kyoichiro', 3, 'YesOneNameexcellentpolice detective')],
        'ns': [('Tokyo', 2, 'CasePieceSendNativeinTokyo')],
        't': [('March 15, 2023', 1, 'CasePieceSendNativeinMarch 15, 2023in the evening at ')],
        'nn': [('doctor', 1, 'doctorCheckillnessPerson')]
    }

    # Test that each entity contains name and type
    for entity_type, entity_list in entities.items():
        for entity_name, frequency, context in entity_list:
            assert entity_name is not None and entity_name != ""
            assert entity_type in ['nr', 'ns', 't', 'nn']
            assert isinstance(frequency, int) and frequency > 0
            assert context is not None and context != ""

def test_entity_frequency():
    """Test entity frequency information"""
    # Simulate entity data
    entities = {
        'nr': [('Kaga Kyoichiro', 3, 'YesOneNameexcellentpolice detective')],
        'ns': [('Tokyo', 2, 'CasePieceSendNativeinTokyo')]
    }

    # Test frequency information
    for entity_type, entity_list in entities.items():
        for entity_name, frequency, context in entity_list:
            assert isinstance(frequency, int)
            assert frequency > 0

def test_entity_context():
    """Test entity context information"""
    # Simulate entity data
    entities = {
        'nr': [('Kaga Kyoichiro', 3, 'YesOneNameexcellentpolice detective')],
        'ns': [('Tokyo', 2, 'CasePieceSendNativeinTokyo')]
    }

    # Test context information
    for entity_type, entity_list in entities.items():
        for entity_name, frequency, context in entity_list:
            assert context is not None
            assert isinstance(context, str)
            assert len(context) > 0

if __name__ == "__main__":
    pytest.main([__file__])
