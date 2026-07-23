# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from recommenders.attribute_utility_recommender import AttributeUtilityRecommender

def test_cold_start_attribute_initialization():
    """TestColdStartUserProcessingandAttributeDistributionInitialization"""
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
    
    # ModelSimulationAlreadyHasUserData
    ratings_df = pd.DataFrame({
        'user_id': [1, 2, 3], 'product_id': [1, 2, 3], 'rating': [5, 4, 3]
    })
    products_df = pd.DataFrame({
        'product_id': [1, 2, 3],
        'category': ['A', 'B', 'C'],
        'price': [100, 200, 300],
        'price_range': ['LowPrice', 'MidPrice', 'HighPrice'],
        'name': ['ProductBrandA', 'ProductBrandB', 'ProductBrandC'],
        'brand': ['BrandBrandA', 'BrandBrandB', 'BrandBrandC'],
        'avg_rating': [4.0, 4.5, 3.5]
    })
    
    # TrainingRecommendationDevice
    recommender.fit(ratings_df, products_df)
    
    # asNewUser(ID=999)GetGetAttributePreference（ColdStartScenario）
    new_user_id = 999
    # TryasColdStartUserGenerateRecommendation（thisWillTouchSendInitialInitializationLogic）
    recommendations = recommender.predict(new_user_id, top_n=3)
    
    # Breakassertion：SuccessasColdStartUserGenerateRecommendation（CertifiedClearFoundationAtAutomaticGlobalAttributeDistributionInitializationSuccess）
    assert recommendations is not None, "ShouldThisEnergyasColdStartUserGenerateRecommendation"
    assert len(recommendations) > 0, "ColdStartRecommendationResultNotShouldasEmpty"
    
    # VerifyRecommendationResultCombineProcessorness（FoundationAtAutomaticGlobalAttributeDivideDistribution）
    for rec in recommendations:
        assert 'product_id' in rec, "RecommendationResultShouldContainsProductBrandID"
        assert 'score' in rec, "RecommendationResultShouldContainsScore"
        assert rec['score'] > 0, "ColdStartRecommendationScoreShouldasCorrectValue"
    
    print(f"✓ ColdStartUser999InitialInitializationSuccess，Generate{len(recommendations)}item(s)Recommendation")
    print("✓ FoundationAtAutomaticGlobalAttributeDivideDistributionasNewUserAutoAutoInitialInitialization，GenerateCombineProcessorInitialInitialRecommendation")
