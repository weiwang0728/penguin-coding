#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Py test-safe version of ConfigManager
"""
import os
import sys


class PytestSafeConfigManager:
 """Py test-safe ConfigManager that doesn't cause buffer issues"""

 def __init__(self):
 """Safe initialization"""
 self._config = {
 'data': {
 'encoding': 'utf-8',
 'test_size': 0.3,
 'random_state': 42,
 'input_path': 'sample_data/credit_data.csv',
 'output_path': 'outputs',
 'max_file_size_mb': 100,
 'min_samples': 10
 },
 'preprocessing': {
 'missing_value_strategy': 'mean',
 'outlier_removal': True,
 'outlier_threshold': 3.0,
 'feature_selection': True,
 'correlation_threshold': 0.9,
 'scaling_method': 'standard'
 },
 'algorithms': {
 'logistic_regression': {
 'max_iter': 1000,
 'random_state': 42,
 'penalty': 'l2',
 'C': 1.0
 },
 'neural_network': {
 'hidden_layer_sizes': [64, 32],
 'activation': 'relu',
 'solver': 'adam',
 'alpha': 0.001,
 'max_iter': 1000,
 'random_state': 42
 }
 },
 'logging': {
 'level': 'INFO',
 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 'file_path': 'logs/credit_assessment.log',
 'max_bytes': 10485760,
 'backup_count': 5
 }
 }

 def get(self, key: str, default=None):
 """Get configuration value"""
 keys = key.split('.')
 value = self._config
 try:
 for k in keys:
 value = value[k]
 return value
 except (KeyError, TypeError):
 return default

 def get_section(self, section: str):
 """Get configuration section"""
 return self._config.get(section, {})


# Create patch function to temporarily replace ConfigManager in tests
def patch_config_manager():
 """Patch ConfigManager for py test compatibility"""
 if '../src' not in sys.path:
 sys.path.insert(0, '../src')

 # Dynamically replace ConfigManager
 import credit_assessment.utils.config_manager as config_module
 config_module.ConfigManager = PytestSafeConfigManager

 return PytestSafeConfigManager


if __name__ == "__main__":
 print("Py test-safe ConfigManager created")