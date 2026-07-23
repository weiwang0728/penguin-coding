#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
# AddsrcDirectorytoPythonPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommenders.attribute_utility_recommender import AttributeUtilityRecommender
import pandas as pd

def test_attribute_utility_recommendation():
    """TestAttributeUtilityOverlayRecommendationFunction"""
    try:
        config = {
            'recommendation': {'default_top_n': 5},
            'recommendation_settings': {
                'attribute_weights': {
                    'price': 0.3,
                    'quality': 0.25,
                    'function': 0.25,
                    'appearance': 0.2
                }
            }
        }
        recommender = AttributeUtilityRecommender(config)
        
        # CreateTestData
        ratings_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2],
            'product_id': [1, 2, 1, 3], 
            'rating': [5.0, 4.0, 3.0, 5.0]
        })
        
        products_df = pd.DataFrame({
            'product_id': [1, 2, 3],
            'name': ['ProductBrandA', 'ProductBrandB', 'ProductBrandC'],
            'category': ['Electronics', 'Clothing', 'Home'],
            'brand': ['BrandBrandA', 'BrandBrandB', 'BrandBrandC'],
            'price': [100.0, 200.0, 300.0],
            'price_range': ['LowPrice', 'MidPrice', 'HighPrice'],
            'avg_rating': [4.0, 4.5, 3.5]
        })
        
        # TrainingAndGenerateRecommendation
        recommender.fit(ratings_df, products_df)
        recommendations = recommender.predict(user_id=1, top_n=5)
        
        print("SUCCESS: AttributeEffectUseRecommendationSuccess")
        print(f"RecommendationQuantity: {len(recommendations)}")
        
        # CheckRecommendationExplanation
        has_explanation = any('explanation' in rec or 'reason' in rec for rec in recommendations)
        if has_explanation:
            print("SUCCESS: ContainsRecommendationExplanation")
        
        return True
        
    except Exception as e:
        print(f"ERROR: RecommendationGenerateFailure: {e}")
        return False

if __name__ == "__main__":
    success = test_attribute_utility_recommendation()
    sys.exit(0 if success else 1)
