# -*- coding: utf-8 -*-
import pytest
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from data_manager import DataManager

def test_config_parameter_driven():
    """TestConfigureFileManagementandParameterDrivenAuto"""
    # CreateTemporaryTimeConfigureFile
    test_config = {
        'recommendation': {'top_n': 10, 'similarity_threshold': 0.8},
        'neural_network': {'learning_rate': 0.01}
    }
    
    with open('temp_config.json', 'w') as f:
        json.dump(test_config, f)
    
    # TestConfigureLoad
    data_manager = DataManager('temp_config.json')
    
    # Breakassertion：ConfigureParameterNativeEffect
    assert data_manager.config['recommendation']['top_n'] == 10, "RecommendationQuantityParameterShouldNativeEffect"
    assert data_manager.config['recommendation']['similarity_threshold'] == 0.8, "CameraSimilarRepublicThresholdValueParameterShouldNativeEffect"
    assert data_manager.config['neural_network']['learning_rate'] == 0.01, "OpticsLearnRateParameterShouldNativeEffect"
    
    # CleanProcessorTemporaryTimeFile
    os.remove('temp_config.json')
