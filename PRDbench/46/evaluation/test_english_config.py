#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test if English config file fixes pytest issue
"""
import pytest
import sys
import os
import shutil
from pathlib import Path

# Add project path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))


class TestEnglishConfig:
    """Test with English config file"""
    
    def setup_method(self):
        """Backup original config and use English version"""
        self.original_config = "../src/config.yaml"
        self.backup_config = "../src/config_backup.yaml"
        self.english_config = "config_english.yaml"
        
        # Backup original config
        if os.path.exists(self.original_config):
            shutil.copy2(self.original_config, self.backup_config)
        
        # Copy English config to replace original
        shutil.copy2(self.english_config, self.original_config)
    
    def teardown_method(self):
        """Restore original config"""
        if os.path.exists(self.backup_config):
            shutil.copy2(self.backup_config, self.original_config)
            os.remove(self.backup_config)
    
    def test_config_manager_with_english_config(self):
        """Test ConfigManager with English config"""
        print(f"stdout type before import: {type(sys.stdout).__name__}")
        
        # Import and create ConfigManager with English config
        from credit_assessment.utils.config_manager import ConfigManager
        print(f"stdout type after import: {type(sys.stdout).__name__}")
        
        # Create instance (this triggers config loading)
        config = ConfigManager()
        print(f"stdout type after creation: {type(sys.stdout).__name__}")
        
        # Verify config works
        data_section = config.get_section('data')
        assert data_section['encoding'] == 'utf-8'
        
        print("✓ ConfigManager with English config works!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])