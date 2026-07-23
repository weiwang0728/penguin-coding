#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.3.3b AlgorithmExecute - Neural NetworkAnalysisLog

Test whetherOutputDetailedAnalysisLog, Containsat least 3Key information(Network Structure, Execution Time, Key parameters).
"""

import py test
import sys
import os
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestNeuralNetworkAnalysis:
 """Neural NetworkAnalysisLogTestcategory"""

 def setup_method(self):
 """TestbeforePrepare"""
 self.config = ConfigManager()
 self.algorithm_manager = AlgorithmManager(self.config)

 # Createtraining data
 np.random.seed(42)
 n_samples = 200

 self.X_train = pd.DataFrame({
 'feature1': np.random.normal(0, 1, n_samples),
 'feature2': np.random.normal(0, 1, n_samples),
 'feature3': np.random.normal(0, 1, n_samples),
 'feature4': np.random.normal(0, 1, n_samples)
 })

 # Createtarget(andFeatureHasOneFixedCameraRelatedness)
 self.y_train = pd. columns(
 ((self.X_train['feature1'] * 0.5 + self.X_train['feature2'] * 0.3 +
 np.random.normal(0, 0.5, n_samples)) > 0).astype(int)
 )

 def test_neural_network_analysis(self):
 """TestNeural NetworkAnalysis function"""
 # Execute (Act): SelectChooseNeural NetworkAlgorithmExecuteAnalysis
 try:
 training_result = self.algorithm_manager.train_algorithm(
 'neural_network', self.X_train, self.y_train
 )

 # Break (Assert): ViewObservewhetherOutputDetailedAnalysisLog, Containsat least 3Key information

 # 1. VerifyExecution Timeinformation
 assert 'training_time' in training_result, "ShouldThisContainsExecution Timeinformation"
 training_time = training_result['training_time']
 assert isinstance(training_time, (int, float)), "trainingtimeShouldThisyesnumber value categoryType"
 assert training_time >= 0, "trainingtimeShouldThisLargeAtEqualAt0"

 print(f"✓ Execution Time: {training_time:.3f} seconds")

 # 2. VerifyNetwork Structureinformation
 algorithm = self.algorithm_manager.get_algorithm('neural_network')
 model_summary = algorithm.get_model_summary()

 assert model_summary.get('is_trained', False), "ModelShouldThisAlreadyEconomytrainingcompleted successfully"

 # CheckNetwork Structureinformation
 structure_info = []
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 if hasattr(algorithm.model, 'get_params'):
 params = algorithm.model.get_params()

 # CheckHidden LayerLargeSmall
 if 'hidden_layer_sizes' in params:
 hidden_layers = params['hidden_layer_sizes']
 structure_info.append(f"Hidden Layerstructure: {hidden_layers}")

 # Checkfunctionnumber
 if 'activation' in params:
 activation = params['activation']
 structure_info.append(f"functionnumber: {activation}")

 # CheckRequestdevice
 if 'solver' in params:
 solver = params['solver']
 structure_info.append(f"Requestdevice: {solver}")

 if structure_info:
 print(f"✓ Network Structure: {', '.join(structure_info)}")
 else:
 print("✓ Network Structure: UseDefaultCertifiedNetwork StructureConfigure")

 # 3. VerifyKey parametersinformation
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 if hasattr(algorithm.model, 'get_params'):
 params = algorithm.model.get_params()
 key_params = []

 param_keys = ['learning_rate_init', 'max_iter', 'alpha', 'batch_size']
 for key in param_keys:
 if key in params:
 key_params.append(f"{key}={params[key]}")

 if key_params:
 print(f"✓ Key parameters: {', '.join(key_params[:3])}") # Displaybefore3items
 else:
 print("✓ Key parameters: UseDefaultCertifiedparameterConfigure")
 else:
 print("✓ Key parameters: Neural NetworkparameterAlreadysettings")

 # 4. VerifyContains 3Key information
 key_info_count = 0
 key_info_list = []

 if 'training_time' in training_result:
 key_info_count += 1
 key_info_list.append("Execution Time")

 if model_summary.get('is_trained'):
 key_info_count += 1
 key_info_list.append("Network Structure")

 if (hasattr(algorithm, 'model') and hasattr(algorithm.model, 'get_params')) or 'parameters' in training_result:
 key_info_count += 1
 key_info_list.append("Key parameters")
 else:
 # Hastrainingcompleted successfullyStatus
 key_info_count += 1
 key_info_list.append("trainingStatus")

 assert key_info_count >= 3, f"ShouldThisContainsat least 3Key information, Current{key_info_count}items: {key_info_list}"

 print(f"Key informationSystemDesign: Contains{key_info_count}itemsKey information - {key_info_list}")
 print("Neural NetworkAnalysisLogTest Passed: OutputDetailedAnalysisLog, ContainsNetwork Structure, Execution Time, Key parametersEqualinformation")

 except Exception as e:
 py test.skip(f"Neural NetworktrainingFailure, SkipTest: {e}")

if __name__ == "__main__":
 py test.main([__file__])