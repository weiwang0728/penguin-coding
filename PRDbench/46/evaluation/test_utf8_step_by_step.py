#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step-by-step Test under UTF-8 Environment
"""
import py test
import sys
import os
from pathlib import Path

def test_step1_basic():
 """Basic test"""
 assert True
 print("✓ Step 1: Basic test passed")

def test_step2_import_path():
 """Test path import"""
 current_dir = Path(__file__).parent
 src_dir = current_dir.parent / "src"
 sys.path.insert(0, str(src_dir))

 assert str(src_dir) in sys.path
 print("✓ Step 2: Path import passed")

def test_step3_config_manager():
 """Test ConfigManager import"""
 current_dir = Path(__file__).parent
 src_dir = current_dir.parent / "src"
 sys.path.insert(0, str(src_dir))

 from credit_assessment.utils.config_manager import ConfigManager
 config = ConfigManager()

 assert config is not None
 print("✓ Step 3: ConfigManager import passed")

def test_step4_data_manager():
 """Test data manager import and usage"""
 current_dir = Path(__file__).parent
 src_dir = current_dir.parent / "src"
 sys.path.insert(0, str(src_dir))

 from credit_assessment.utils.config_manager import ConfigManager
 from credit_assessment.data.data_manager import DataManager

 config = ConfigManager()
 data_manager = DataManager(config)

 assert data_manager is not None
 print("✓ Step 4: DataManager creation passed")

if __name__ == "__main__":
 py test.main([__file__, "-v"])
