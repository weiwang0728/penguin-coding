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
    """Test spouse links are bidirectional and children are shared."""
    # SaveNativeInitialFileName
    original_filename = info.cur_filename
    test_filename = "test_data_017.csv"
    info.cur_filename = test_filename
    
    # Clear existing data before the test
    info.alist = []
    tb.family = []
    
    # Create test data
    test_data = [
        {"name": "WangWu", "born_place": "Guangzhou", "born_date": "19800808", "dead_date": "0", "height": "172.0",
         "edu_bg": "Bachelor", "pos": "Teacher", "top_pos": "Principal", "born_rela": "", "rela_ship": "0", "sex": "Male"},
        {"name": "ZhaoLiu", "born_place": "Shenzhen", "born_date": "19750315", "dead_date": "0", "height": "165.0",
         "edu_bg": "HighSchool", "pos": "SalesRep", "top_pos": "SalesManager", "born_rela": "WangWu", "rela_ship": "0", "sex": "Female"},
        {"name": "SunQi", "born_place": "Hangzhou", "born_date": "20100101", "dead_date": "0", "height": "120.0",
         "edu_bg": "ElementarySchool", "pos": "Student", "top_pos": "", "born_rela": "WangWu", "rela_ship": "1", "sex": "Male"}
    ]
    
    # Create the test CSV file
    df = pd.DataFrame(test_data)
    df.to_csv(test_filename, index=False)
    
    # Read the file and build the family tree
    info.read_file()
    tb.buildTree(info.alist)
    
    # Verify the family list contains all members
    assert len(tb.family) >= 3, "The family list should contain at least three members"
    
    # Find WangWu and ZhaoLiu in the family tree
    wang_idx = None
    zhao_idx = None
    for i, member in enumerate(tb.family):
        if info.alist[member.idx]['name'] == 'WangWu':
            wang_idx = i
        elif info.alist[member.idx]['name'] == 'ZhaoLiu':
            zhao_idx = i
    
    assert wang_idx is not None, "WangWu should be found in the family list"
    assert zhao_idx is not None, "ZhaoLiu should be found in the family list"
    
    # Verify spouse links are bidirectional
    assert tb.family[wang_idx].spouse == zhao_idx, "WangWu's spouse should point to ZhaoLiu"
    assert tb.family[zhao_idx].spouse == wang_idx, "ZhaoLiu's spouse should point to WangWu"
    
    # Verify spouses share the same children list
    assert tb.family[wang_idx].kids == tb.family[zhao_idx].kids, "Spouses should share the same children list"
    assert len(tb.family[wang_idx].kids) > 0, "The spouse pair should have at least one child"
    
    # Clean up test data
    info.alist = []
    tb.family = []
    info.cur_filename = original_filename
    
    # Delete the test file
    if os.path.exists(test_filename):
        os.remove(test_filename)
    
    print("Spouse links point to each other correctly, and both spouses share the same child list.")

if __name__ == "__main__":
    test_function()