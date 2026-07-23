#!/usr/bin/env python
# coding: utf-8

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import BasicInfo as info
import TreeBuild as tb
import pytest

def test_function():
    """Test member class definition and root member setup."""
    # Clear existing data before the test
    info.alist = []
    tb.family = []
    
    # Add a single test member
    info.blist = []
    info.add("ZhangSam", "Beijing", "19900101", "0", "175.5", "Bachelor", "SoftwareEngineer", "SeniorEngineer", "", "0", "Male")
    info.save_file(info.blist)
    
    # Read the file and build the family tree
    info.read_file()
    tb.buildTree(info.alist)
    
    # Verify the family list is not empty
    assert len(tb.family) > 0, "The family list should not be empty"
    
    # Verify the first member is the root member
    root_member = tb.family[0]
    
    # Verify required member attributes exist
    assert hasattr(root_member, 'idx'), "Member object should contain the idx attribute"
    assert hasattr(root_member, 'kids'), "Member object should contain the kids attribute"
    assert hasattr(root_member, 'spouse'), "Member object should contain the spouse attribute"
    
    # Verify the root member has RelatedSeries set to -1
    root_info = info.alist[root_member.idx]
    assert root_info['RelatedSeries'] == -1, "The first member should be marked as the root member with RelatedSeries = -1"
    
    # CleanProcessor
    info.alist = []
    tb.family = []
    
    print("Member object includes idx, kids, and spouse, and the first member is marked as the root member with RelatedSeries = -1.")

if __name__ == "__main__":
    test_function()