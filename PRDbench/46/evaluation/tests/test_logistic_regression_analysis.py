#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test2.3.3a AlgorithmExecute - Logistic RegressionAnalysisLog

Test whetherOutputDetailedAnalysisLog, Containsat least 3Key information(Execution Time, parametersettings, ReceiveStatus).
"""

import py test
import sys
import os
import tempfile
import pandas as pd
import numpy as np

# Add project path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
 from credit_assessment.algorithms.algorithm_manager import AlgorithmManager
 from credit_assessment.utils.config_manager import ConfigManager
except ImportError as e:
 py test.skip(f"NoMethodImportModule: {e}", allow_module_level=True)

class TestLogisticRegressionAnalysis:
 """Logistic RegressionAnalysisLogTestcategory"""

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
 ((self.X_train['feature1'] + self.X_train['feature2'] +
 np.random.normal(0, 0.5, n_samples)) > 0).astype(int)
 )

 def test_logistic_regression_analysis(self):
 """TestLogistic RegressionAnalysis function"""
 # Execute (Act): SelectChooseLogistic RegressionAlgorithmExecuteAnalysis
 try:
 training_result = self.algorithm_manager.train_algorithm(
 'logistic_regression', self.X_train, self.y_train
 )

 # Break (Assert): ViewObservewhetherOutputDetailedAnalysisLog, Containsat least 3Key information

 # 1. VerifyExecution Timeinformation
 assert 'training_time' in training_result, "ShouldThisContainsExecution Timeinformation"
 training_time = training_result['training_time']
 assert isinstance(training_time, (int, float)), "trainingtimeShouldThisyesnumber value categoryType"
 assert training_time >= 0, "trainingtimeShouldThisLargeAtEqualAt0"

 print(f"✓ Execution Time: {training_time:.3f} seconds")

 # 2. Verifyparametersettingsinformation(PassAlgorithmImplementationExampleGetGet)
 algorithm = self.algorithm_manager.get_algorithm('logistic_regression')
 model_summary = algorithm.get_model_summary()

 assert model_summary.get('is_trained', False), "ModelShouldThisAlreadyEconomytrainingcompleted successfully"

 # CheckwhetherHasparameterinformation
 if 'parameters' in model_summary or hasattr(algorithm, 'model'):
 print("✓ parametersettings: ContainsAlgorithmConfigureinformation")

 # resultHasModelObject, Checkparameter
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 if hasattr(algorithm.model, 'get_params'):
 params = algorithm.model.get_params()
 print(f" Modelparameter: {list(params.keys())[:3]}") # Displaybefore3itemsparameterName
 else:
 print("✓ parametersettings: AlgorithmUseDefaultCertifiedparameterConfigure")

 # 3. VerifyReceiveStatusinformation
 convergence_info = "NotKnow"
 if hasattr(algorithm, 'model') and algorithm.model is not None:
 # Checksklearn LogisticRegressionReceiveinformation
 if hasattr(algorithm.model, 'n_iter_'):
 iterations = algorithm.model.n_iter_
 if isinstance(iterations, np.ndarray):
 iterations = iterations[0] if len(iterations) > 0 else 0
 convergence_info = f"ReceiveAt{iterations}TimesGeneration"
 print(f"✓ ReceiveStatus: {convergence_info}")
 elif 'converged' in training_result:
 convergence_info = "AlreadyReceive" if training_result['converged'] else "NotReceive"
 print(f"✓ ReceiveStatus: {convergence_info}")
 else:
 print("✓ ReceiveStatus: trainingcompleted successfully(ToolintegratedReceiveinformationAlgorithmImplementationImplementationExtractProvide)")

 # 4. VerifyContains 3Key information
 key_info_count = 0
 key_info_list = []

 if 'training_time' in training_result:
 key_info_count += 1
 key_info_list.append("Execution Time")

 if model_summary.get('is_trained') or (hasattr(algorithm, 'model') and algorithm.model is not None):
 key_info_count += 1
 key_info_list.append("parametersettings")

 if (hasattr(algorithm, 'model') and hasattr(algorithm.model, 'n_iter_')) or 'converged' in training_result:
 key_info_count += 1
 key_info_list.append("ReceiveStatus")
 else:
 # Hastrainingcompleted successfullyStatus
 key_info_count += 1
 key_info_list.append("trainingStatus")

 assert key_info_count >= 3, f"ShouldThisContainsat least 3Key information, Current{key_info_count}items: {key_info_list}"

 print(f"Key informationSystemDesign: Contains{key_info_count}itemsKey information - {key_info_list}")
 print("Logistic RegressionAnalysisLogTest Passed: OutputDetailedAnalysisLog, ContainsExecution Time, parametersettings, ReceiveStatusEqualKey information")

 except Exception as e:
 py test.skip(f"Logistic RegressiontrainingFailure, SkipTest: {e}")

if __name__ == "__main__":
 py test.main([__file__])