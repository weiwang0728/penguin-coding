#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PNG File Verification Script
"""
import os
import glob

def verify_png_files():
    """Verify PNG chart file generation"""
    files = glob.glob('src/output/figures/*.png')
    
    if files:
        print(f'PNG chart files generated: {len(files)} {"files" if len(files) != 1 else "file"}')
        for f in files:
            if os.path.getsize(f) > 0:
                print(f'  {f}: {os.path.getsize(f)} bytes')
        return True
    else:
        print('No PNG files found: 0 files')
        return False

if __name__ == '__main__':
    verify_png_files()