#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BatchUpdateunit_testCommand

Detailed Test Designincomprehensive_unit_tests.pyComm and Update as Test file
"""

import json
import os

def update_test_commands():
 """UpdateTest Command"""

 # Get Test Design
 with open('detailed_test_plan.json', 'r', encoding='utf-8') as f:
 test_plan = json.load(f)

 # Test Command
 test_command_mapping = {
 # Alreadycompleted successfullyTest file
 "2.1.2a Data Validation - MissingFailvalueCheckTest": "python -m py test tests/test_missing_value s_detection.py -v",
 "2.1.2b Data Validation - AbnormalDataCheckTest": "python -m py test tests/test_anomaly_detection.py -v",
 "2.1.2c Data Validation - categoryTypeNotSymboldisplay": "python -m py test tests/test_type_validation.py -v",
 "2.2.1a Data Preprocessing - MissingFailvalue imputationmethodSelectChoose": "python -m py test tests/test_missing_value_method s.py -v",
 "2.2.1b Data Preprocessing - MissingFailvalue processingExecute": "python -m py test tests/test_missing_value_execution.py -v",
 "2.2.2a fieldprocessing - number valueTypeField Type Recognition": "python tests/test_numeric_field_recognition.py",
 "2.2.2b fieldprocessing - ClassificationTypeField Type Recognition": "python tests/test_categorical_field_recognition.py",
 "2.2.3a DataCodeCode - CodeCode": "python tests/test_onehot_encoding.py",
 "2.3.3a AlgorithmExecute - Logistic RegressionAnalysisLog": "python tests/test_logistic_regression_analysis.py",
 "2.3.3b AlgorithmExecute - Neural NetworkAnalysisLog": "python tests/test_neural_network_analysis.py",
 "2.3.4 Algorithm Performance Comparison function": "python tests/test_algorithm_comparison.py",
 "2.4.1a Scoreprediction - SingleDataScore": "python tests/test_single_record_scoring.py",
 "2.4.1b Scoreprediction - BatchDataScore": "python tests/test_batch_scoring.py",
 "2.5.1b ROCCurved rows - AUC value calculate": "python tests/test_auc_calculation.py",
 "2.5.4a basicbasicmetrics - PrecisionRecallF1calculate": "python tests/test_basic_metrics.py",
 "2.5.4b basicbasicmetrics - Confusion Matrix": "python tests/test_confusion_matrix.py",
 "2.6.2 ModelEffectresultSummary": "python tests/test_model_effect_summary.py",
 "2.7.1a Feature Explanation - Logistic Regression columnsnumberOutput": "python tests/test_logistic_coefficients.py",

 # UseCombine Test Piece
 "2.2.3b DataCodeCode - TagCodeCode": "python comprehensive_unit_tests.py",
 "2.2.4 FeatureSelectChoose - CameraRelated columnsnumber calculate": "python comprehensive_unit_tests.py",
 "2.3.1 AlgorithmSelectChoose - Logistic Regression": "python comprehensive_unit_tests.py",
 "2.3.2 AlgorithmSelectChoose - Neural Network": "python comprehensive_unit_tests.py",
 "2.5.2a K-SCurved rows - chartPortraitGenerate": "python comprehensive_unit_tests.py",
 "2.5.2b K-SCurved rows - MostLargeKSDistanceDistanceMarkNote": "python comprehensive_unit_tests.py",
 "2.5.3a LIFTchart - chartPortraitGenerate": "python comprehensive_unit_tests.py",
 "2.5.3b LIFTchart - DivideLayerExtractRepublicDisplay": "python comprehensive_unit_tests.py",
 "2.6.1b ReportContent - Visualization ChartsContains": "python comprehensive_unit_tests.py",
 "2.7.1b Feature Explanation - Top-NWeightnessVisualization": "python comprehensive_unit_tests.py",
 "2.7.2a Neural Network - WeightWeightOutput": "python comprehensive_unit_tests.py",
 "2.7.2b Neural Network - Feature Contribution Visualization": "python comprehensive_unit_tests.py"
 }

 # Update Test Design
 updated_count = 0
 for test_item in test_plan:
 metric = test_item.get('metric', '')
 test_type = test_item.get('type', '')

 if test_type == 'unit_test' and metric in test_command_mapping:
 current_command = test_item['testcases'][0]['test_command']
 new_command = test_command_mapping[metric]

 if current_command != new_command:
 test_item['testcases'][0]['test_command'] = new_command
 updated_count += 1
 print(f"[UPDATE] {metric}: {new_command}")

 # SaveUpdateafter Test Design
 with open('detailed_test_plan.json', 'w', encoding='utf-8') as f:
 json.dump(test_plan, f, indent=4, ensure_ascii=False)

 print(f"\n[SUMMARY] TotalUpdate{updated_count}itemsTest Command")

 # SystemDesignTestcategoryTypeDivideDistribution
 test_type_stats = {}
 for test_item in test_plan:
 test_type = test_item.get('type', 'unknown')
 test_type_stats[test_type] = test_type_stats.get(test_type, 0) + 1

 print(f"\nTestcategoryTypeSystemDesign:")
 for test_type, count in test_type_stats.items():
 print(f" {test_type}: {count}items")

 return updated_count

if __name__ == "__main__":
 updated_count = update_test_commands()
 print(f"\nBatchUpdatecompleted successfully！Update{updated_count}itemsTest Command. ")