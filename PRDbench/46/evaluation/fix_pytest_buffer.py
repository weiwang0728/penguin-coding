#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix pytest buffer detached error by restoring original stdout/stderr
"""
import sys
import io

def fix_stdout_stderr():
    """Restore original stdout/stderr to fix pytest buffer issue"""
    print("=== Fixing stdout/stderr buffer issue ===")
    
    # Get original streams
    original_stdout = sys.__stdout__
    original_stderr = sys.__stderr__
    
    print(f"Current stdout type: {type(sys.stdout).__name__}")
    print(f"Current stderr type: {type(sys.stderr).__name__}")
    print(f"Original stdout type: {type(original_stdout).__name__}")
    print(f"Original stderr type: {type(original_stderr).__name__}")
    
    # Restore original streams
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    
    print(f"After restore stdout type: {type(sys.stdout).__name__}")
    print(f"After restore stderr type: {type(sys.stderr).__name__}")
    print("Buffer state restored successfully!")
    
if __name__ == "__main__":
    fix_stdout_stderr()