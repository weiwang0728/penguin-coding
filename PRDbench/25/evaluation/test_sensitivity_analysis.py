# -*- coding: utf-8 -*-
"""Test sensitivityInfectionnessAnalysis"""
import sys; sys.path.append('src')
from model_evaluation import ModelEvaluator

print("Test: ModelTypeEvaluationandAnalysis → sensitivityInfectionnessAnalysis")
evaluator = ModelEvaluator()
evaluator.sensitivity_analysis()
print("[Success] sensitivityInfectionnessAnalysisCompleteSuccess!")