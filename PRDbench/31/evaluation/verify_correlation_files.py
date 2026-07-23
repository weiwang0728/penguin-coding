#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correlation Heatmap File Verification Script
"""
import os
import glob

def verify_correlation_files():
    """Verify correlation heatmap file generation"""
    files = glob.glob('src/output/figures/correlation_*.png')
    
    if files:
        print(f'Correlation heatmap files generated: {len(files)} {"files" if len(files) != 1 else "file"}')
        for f in files:
            if os.path.getsize(f) > 0:
                print(f'  {f}: {os.path.getsize(f)} bytes')
        return True
    else:
        print('No correlation files found: 0 files')
        return False

if __name__ == '__main__':
    verify_correlation_files()