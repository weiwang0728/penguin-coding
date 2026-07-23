#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON File Comparison Script
"""
import json
import sys

def compare_json_files(file1, file2):
    """Compare two JSON files, ignoring timestamp fields"""
    try:
        with open(file1, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        
        with open(file2, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        # Remove timestamp fields
        data1.pop('created_at', None)
        data1.pop('updated_at', None)
        data2.pop('created_at', None)
        data2.pop('updated_at', None)
        
        if data1 == data2:
            print('Files match')
            return True
        else:
            print('Files differ')
            return False
            
    except Exception as e:
        print(f'Error comparing files: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python compare_json.py <file1> <file2>')
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    result = compare_json_files(file1, file2)
    sys.exit(0 if result else 1)