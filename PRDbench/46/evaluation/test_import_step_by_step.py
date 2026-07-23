#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step by step import test to find the problematic module
"""
import pytest
import sys
import os
from pathlib import Path

# Add project path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))


def test_step1_config_manager():
    """Test importing ConfigManager"""
    from credit_assessment.utils.config_manager import ConfigManager
    config = ConfigManager()
    assert config is not None
    print("Step 1: ConfigManager OK")


def test_step2_logger():
    """Test importing logger"""
    from credit_assessment.utils.logger import setup_logger
    logger = setup_logger("test")
    assert logger is not None
    print("Step 2: Logger OK")


def test_step3_data_manager():
    """Test importing DataManager"""
    from credit_assessment.data.data_manager import DataManager
    from credit_assessment.utils.config_manager import ConfigManager
    
    config = ConfigManager()
    data_manager = DataManager(config)
    assert data_manager is not None
    print("Step 3: DataManager OK")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])