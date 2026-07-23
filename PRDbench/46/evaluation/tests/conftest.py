#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest configuration file to fix buffer detached issue
"""
import pytest
import gc
import sys
import warnings

def pytest_runtest_setup(item):
    """Cleanup before each test"""
    # Force garbage collection to avoid dangling references
    gc.collect()

    # Ensure stdout/stderr status is normal
    if hasattr(sys.stdout, 'flush'):
        try:
            sys.stdout.flush()
        except:
            pass
    if hasattr(sys.stderr, 'flush'):
        try:
            sys.stderr.flush()
        except:
            pass

def pytest_runtest_teardown(item, nextitem):
    """Cleanup after each test"""
    # Force garbage collection
    gc.collect()
