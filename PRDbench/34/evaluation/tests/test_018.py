#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info
import TreeBuild as tb
import pytest

def test_function():
    """Test parent-child links and member lookup by name."""
    # SaveNativeInitialFileName
    original_filename = info.cur_filename
    test_filename = "test_data_018.csv"
    info.cur_filename = test_filename
    
    # Clear existing data before the test
    info.alist = []
    tb.family = []
    
    # Create test data
    test_data = [
        {"name": "WangWu", "born_place": "Guangzhou", "born_date": "19800808", "dead_date": "0", "height": "172.0",
         "edu_bg": "Bachelor", "pos": "Teacher", "top_pos": "Principal", "born_rela": "", "rela_ship": "0", "sex": "Male"},
        {"name": "SunQi", "born_place": "Hangzhou", "born_date": "20100101", "dead_date": "0", "height": "120.0",
         "edu_bg": "ElementarySchool", "pos": "Student", "top_pos": "", "born_rela": "WangWu", "rela_ship": "1", "sex": "Male"}
    ]
    
    # Create the test CSV file
    df = pd.DataFrame(test_data)
    df.to_csv(test_filename, index=False)
    
    # Read the file and build the family tree
    info.read_file()
    tb.buildTree(info.alist)
    
    # Verify the family list contains both members
    assert len(tb.family) >= 2, "The family list should contain at least two members"
    
    # Find WangWu and SunQi in the family tree
    wang_idx = None
    sun_idx = None
    for i, member in enumerate(tb.family):
        if info.alist[member.idx]['name'] == 'WangWu':
            wang_idx = i
        elif info.alist[member.idx]['name'] == 'SunQi':
            sun_idx = i
    
    assert wang_idx is not None, "WangWu should be found in the family list"
    assert sun_idx is not None, "SunQi should be found in the family list"
    
    # Verify the parent-child relationship
    assert sun_idx in tb.family[wang_idx].kids, "The parent's kids list should contain the child member"
    
    # Test member lookup by name
    found_wang_idx = tb.find_rela("WangWu")
    found_sun_idx = tb.find_rela("SunQi")
    
    assert found_wang_idx == wang_idx, "The system should locate WangWu at the correct position in the family list"
    assert found_sun_idx == sun_idx, "The system should locate SunQi at the correct position in the family list"
    
    # Clean up test data
    info.alist = []
    tb.family = []
    info.cur_filename = original_filename
    
    # Delete the test file
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("The parent member contains the child in the kids list, and member lookup by name returns the correct positions.")

if __name__ == "__main__":
    test_function()