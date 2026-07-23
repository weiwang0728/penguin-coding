#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# AddsrcDirectorytoPythonPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from evaluator import RecommendationEvaluator

def test_evaluation_metrics():
    """TestRecommendationCalculateMethodPerformanceEvaluateTestIndicatorMark"""
    try:
        config = {'evaluation': {'top_n': 5}}
        evaluator = RecommendationEvaluator(config)
        
        # ModelSimulationTestData
        y_true = [1, 1, 0, 1, 0, 1, 0, 1, 1, 0]
        y_pred = [1, 0, 0, 1, 1, 0, 0, 1, 1, 0]
        
        # DesignCalculateFoundationFoundationIndicatorMark
        metrics = evaluator.calculate_basic_metrics(y_true, y_pred)
        
        # CheckCoreCoreIndicatorMark
        required_metrics = ['precision', 'recall', 'f1_score']
        all_present = all(metric in metrics for metric in required_metrics)
        
        if all_present:
            print("SUCCESS: BasicPrecisionRecallF1IndicatorMarkDesignCalculateSuccess")
            for metric in required_metrics:
                print(f"  {metric}: {metrics[metric]:.3f}")
        
        # DesignCalculateHighLevelIndicatorMark
        recommendations = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
        advanced_metrics = evaluator.calculate_advanced_metrics(recommendations)
        
        advanced_required = ['coverage', 'diversity', 'cold_start_hit_rate']
        advanced_present = all(metric in advanced_metrics for metric in advanced_required)
        
        if advanced_present:
            print("SUCCESS: CoverageDiversityIndicatorMarkDesignCalculateSuccess")
            for metric in advanced_required:
                print(f"  {metric}: {advanced_metrics[metric]:.3f}")
        
        return all_present and advanced_present
        
    except Exception as e:
        print(f"ERROR: EvaluationIndicatorMarkDesignCalculateFailure: {e}")
        return False

if __name__ == "__main__":
    success = test_evaluation_metrics()
    sys.exit(0 if success else 1)
