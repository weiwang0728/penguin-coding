#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Descriptive Statistics Chart Verification Script
"""
import os

def verify_descriptive_chart():
    """Verify descriptive statistics chart file generation"""
    path = 'src/output/figures/descriptive_stats_scale_1.png'
    
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    
    if exists and size > 0:
        print(f'File exists and size > 0: {exists} {size}')
        return True
    else:
        print(f'File missing or empty: {exists} {size}')
        return False

if __name__ == '__main__':
    verify_descriptive_chart()