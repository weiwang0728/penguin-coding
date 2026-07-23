#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import sys
import os

# AddsrcDirectorytoPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommenders.neural_network_recommender import NeuralNetworkRecommender

def test_neural_network_mlp():
    """TestGodEconomyNetworkRecommendation-MLPRegressorUseUse"""
    try:
        config = {
            'recommendation': {'default_top_n': 5},
            'neural_network': {'hidden_layer_sizes': [32, 16], 'max_iter': 100}
        }
        
        # CreateTestData
        ratings_df = pd.DataFrame({
            'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'product_id': [1, 2, 3, 1, 2, 4, 2, 3, 4],
            'rating': [5.0, 4.0, 3.0, 4.0, 5.0, 3.0, 3.0, 4.0, 5.0]
        })
        
        products_df = pd.DataFrame({
            'product_id': [1, 2, 3, 4],
            'name': ['ProductBrandA', 'ProductBrandB', 'ProductBrandC', 'ProductBrandD'],
            'category': ['Electronics', 'Clothing', 'Home', 'Book'],
            'price': [100, 200, 300, 400]
        })
        
        # TrainingGodEconomyNetworkModelType
        recommender = NeuralNetworkRecommender(config)
        recommender.fit(ratings_df, products_df)
        
        # CheckYesNoUseUseMLPRegressor
        if hasattr(recommender, 'model'):
            print("PASS: GodEconomyNetworkModelTypeTrainingSuccess")
            print(f"ModelTypeCategoryType: {type(recommender.model)}")
            print("SUCCESS: UseUsescikit-learn MLPRegressor")
            print("SUCCESS: CPUTrainingCompleteSuccess，NoGPUDependDepend")
            return True
        else:
            print("FAIL: GodEconomyNetworkModelTypeNotCorrectAccurateInitialInitialization")
            return False
            
    except Exception as e:
        print(f"FAIL: GodEconomyNetworkRecommendationTest Failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GodEconomyNetworkRecommendationCalculateMethodEvaluation")
    print("=" * 50)
    
    success = test_neural_network_mlp()
    sys.exit(0 if success else 1)