# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from evaluator import RecommendationEvaluator

def test_precision_recall_f1():
    """TestStandardAccurateRate、RecallReturnRate、F1DivideNumberDesignCalculate"""
    config = {'evaluation': {'top_n': 5}}
    evaluator = RecommendationEvaluator(config)
    
    # ModelSimulationTestData
    y_true = [1, 1, 0, 1, 0]
    y_pred = [1, 0, 0, 1, 1]
    
    metrics = evaluator.calculate_basic_metrics(y_true, y_pred)
    
    # Breakassertion：Contains3item(s)CoreCoreIndicatorMark
    assert 'precision' in metrics, "ShouldContainsStandardAccurateRate"
    assert 'recall' in metrics, "ShouldContainsRecallReturnRate"
    assert 'f1_score' in metrics, "ShouldContainsF1DivideNumber"
    return True

def test_coverage_diversity():
    """Test CoverageandManyDiversitynessIndicatorMark"""
    config = {'evaluation': {'top_n': 5}}
    evaluator = RecommendationEvaluator(config)
    
    # ModelSimulationRecommendationResult
    recommendations = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    
    advanced_metrics = evaluator.calculate_advanced_metrics(recommendations)
    
    # Breakassertion：Contains3item(s)HighLevelIndicatorMark
    assert 'coverage' in advanced_metrics, "ShouldContainsCoverage"
    assert 'diversity' in advanced_metrics, "ShouldContainsManyDiversityness"
    assert 'cold_start_hit_rate' in advanced_metrics, "ShouldContainsColdStartCommandinRate"
    return True
