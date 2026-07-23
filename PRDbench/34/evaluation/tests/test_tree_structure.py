#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import TreeBuild as tb
import BasicInfo as info

class TestTreeStructure:
    
    def test_member_class_definition(self):
        """Test member class definition and root member setup."""
        # Create a sample member instance
        member = tb.member(idx=0, kids=[], spouse=-1)
        
        # Verify attributes exist
        assert hasattr(member, 'idx')
        assert hasattr(member, 'kids')
        assert hasattr(member, 'spouse')
        
        # Verify initial values
        assert member.idx == 0
        assert member.kids == []
        assert member.spouse == -1
        
    def test_spouse_relationship(self):
        """Test spouse links are bidirectional and children are shared."""
        # Prepare test data
        test_data = [
            ['ZhangSam', 'Beijing', '19700101', '0', '175', 'Bachelor', 'Engineer', 'Manager', '', '0', '1', 'Male'],
            ['LiSi', 'Shanghai', '19720101', '0', '165', 'Bachelor', 'Teacher', 'Director', 'ZhangSam', '1', '1', 'Female'],
            ['ZhangXiaoMing', 'Beijing', '20000101', '0', '160', 'HighSchool', 'Student', 'Student', 'ZhangSam', '2', '1', 'Male']
        ]
        
        # Build the family tree
        family = tb.buildTree(test_data)
        
        # Verify spouse relationships
        assert len(family) >= 2
        if len(family) >= 2:
            # Verify spouse links are bidirectional
            zhang_san_idx = 0
            li_si_idx = 1
            
            assert family[zhang_san_idx].spouse == li_si_idx
            assert family[li_si_idx].spouse == zhang_san_idx
            
            # Verify both spouses share the same children
            assert family[zhang_san_idx].kids == family[li_si_idx].kids
            
    def test_parent_child_relationship(self):
        """Test parent-child links and lookup by name."""
        # Prepare test data
        test_data = [
            ['ZhangSam', 'Beijing', '19700101', '0', '175', 'Bachelor', 'Engineer', 'Manager', '', '0', '1', 'Male'],
            ['ZhangXiaoMing', 'Beijing', '20000101', '0', '160', 'HighSchool', 'Student', 'Student', 'ZhangSam', '2', '1', 'Male']
        ]
        
        # Build the family tree
        family = tb.buildTree(test_data)
        
        # Verify parent-child relationships
        assert len(family) >= 2
        if len(family) >= 2:
            parent_idx = 0
            child_idx = 1
            
            # Verify the parent contains the child in the kids list
            assert child_idx in family[parent_idx].kids
            
            # Verify the name lookup function
            found_idx = tb.find_rela('ZhangSam')
            assert found_idx == parent_idx
            
    def test_index_rebuild_consistency(self):
        """TestSonyImportWeightBuildandResultStructureOneCauseness"""
        # Prepare test data
        test_data = [
            ['ZhangSam', 'Beijing', '19700101', '0', '175', 'Bachelor', 'Engineer', 'Manager', '', '0', '1', 'Male'],
            ['LiSi', 'Shanghai', '19720101', '0', '165', 'Bachelor', 'Teacher', 'Director', '', '0', '1', 'Female'],
            ['ZhangXiaoMing', 'Beijing', '20000101', '0', '160', 'HighSchool', 'Student', 'Student', 'ZhangSam', '2', '1', 'Male']
        ]
        
        # Build the family tree
        family = tb.buildTree(test_data)
        original_length = len(family)
        
        # Verify index consistency
        for i, member in enumerate(family):
            assert member.idx == i
            
        # Verify the resulting structure remains complete
        assert len(family) == original_length
        assert all(isinstance(member, tb.member) for member in family)

if __name__ == '__main__':
    pytest.main([__file__])