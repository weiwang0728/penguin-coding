#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal pytest test to identify the issue
"""
import pytest

def test_minimal():
    """Most basic test possible"""
    assert True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])