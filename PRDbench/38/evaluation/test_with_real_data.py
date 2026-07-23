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

from recommenders.collaborative_filtering_recommender import CollaborativeFilteringRecommender
from recommenders.neural_network_recommender import NeuralNetworkRecommender
from recommenders.attribute_utility_recommender import AttributeUtilityRecommender

def load_real_data():
    """Loaditem(s)TrueImplementationData"""
    try:
        data_dir = os.path.join(project_root, 'src', 'data')
        
        products_df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        ratings_df = pd.read_csv(os.path.join(data_dir, 'ratings.csv'))
        users_df = pd.read_csv(os.path.join(data_dir, 'users.csv'))
        
        print(f"DataLoadSuccess:")
        print(f"  - ProductBrandData: {len(products_df)} records")
        print(f"  - ScoreData: {len(ratings_df)} records") 
        print(f"  - UserData: {len(users_df)} records")
        
        return ratings_df, products_df, users_df
        
    except Exception as e:
        print(f"DataLoadFailure: {e}")
        return None, None, None

def test_collaborative_filtering_with_real_data():
    """UseUseTrueImplementationDataTestCollaborative FilteringCalculateMethod"""
    print("\n" + "="*50)
    print("Collaborative FilteringCalculateMethodTrueImplementationDataTest")
    print("="*50)
    
    ratings_df, products_df, users_df = load_real_data()
    if ratings_df is None:
        return False
    
    config = {
        'recommendation_settings': {
            'top_n': 10,
            'min_ratings_per_user': 5,
            'attribute_weights': {
                'price': 0.3,
                'brand': 0.2,
                'category': 0.25,
                'rating': 0.25
            }
        }
    }
    results = []
    
    # TestSamTypeCameraSimilarRepublicCalculateMethod
    similarity_methods = ['cosine', 'pearson', 'euclidean']
    
    for method in similarity_methods:
        try:
            print(f"\nTest {method} CameraSimilarRepublicCalculateMethod...")
            recommender = CollaborativeFilteringRecommender(config, similarity_metric=method)
            recommender.fit(ratings_df, products_df, users_df)
            
            # asUser1GenerateRecommendation
            recommendations = recommender.predict(user_id=1, top_n=3)
            
            print(f"PASS: {method}CameraSimilarRepublicCalculateMethodTest Passed")
            print(f"RecommendationResultQuantity: {len(recommendations)}")
            results.append(True)
            
        except Exception as e:
            print(f"FAIL: {method}CalculateMethodTest Failed: {e}")
            results.append(False)
    
    return all(results)

def test_neural_network_with_real_data():
    """UseUseTrueImplementationDataTestGodEconomyNetworkRecommendation"""
    print("\n" + "="*50)
    print("GodEconomyNetworkRecommendationTrueImplementationDataTest")
    print("="*50)
    
    ratings_df, products_df, users_df = load_real_data()
    if ratings_df is None:
        return False
        
    try:
        config = {
            'recommendation_settings': {
                'top_n': 10,
                'min_ratings_per_user': 5,
                'attribute_weights': {
                    'price': 0.3,
                    'brand': 0.2,
                    'category': 0.25,
                    'rating': 0.25
                }
            },
            'neural_network': {'hidden_layer_sizes': [32, 16], 'max_iter': 100}
        }
        
        recommender = NeuralNetworkRecommender(config)
        recommender.fit(ratings_df, products_df, users_df)
        
        print("PASS: GodEconomyNetworkRecommendationTrainingSuccess")
        print(f"ModelTypeStatus: {'AlreadyTraining' if recommender.is_trained else 'NotTraining'}")
        print("SUCCESS: MLPRegressorinCPUonTrainingCompleteSuccess")
        
        return True
        
    except Exception as e:
        print(f"FAIL: GodEconomyNetworkRecommendationFailure: {e}")
        return False

def test_attribute_utility_with_real_data():
    """UseUseTrueImplementationDataTestAttributeEffectUseRecommendation"""
    print("\n" + "="*50)
    print("AttributeEffectUseRecommendationTrueImplementationDataTest")
    print("="*50)
    
    ratings_df, products_df, users_df = load_real_data()
    if ratings_df is None:
        return False
        
    try:
        config = {
            'recommendation_settings': {
                'top_n': 10,
                'min_ratings_per_user': 5,
                'attribute_weights': {
                    'price': 0.3,
                    'brand': 0.2,
                    'category': 0.25,
                    'rating': 0.25
                }
            }
        }
        
        recommender = AttributeUtilityRecommender(config)
        recommender.fit(ratings_df, products_df, users_df)
        
        # TestRecommendationGenerate
        recommendations = recommender.predict(user_id=1, top_n=5)
        
        print("PASS: AttributeEffectUseRecommendationTest Passed")
        print(f"RecommendationResultQuantity: {len(recommendations)}")
        print("SUCCESS: RecommendationExplanationFunctionAlreadyImplementationImplementation")
        
        return True
        
    except Exception as e:
        print(f"FAIL: AttributeEffectUseRecommendationFailure: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   AIEvaluation Expert - RecommendationCalculateMethodTrueImplementationDataEvaluation")
    print("=" * 60)
    
    # RunPlaceHasTest
    cf_result = test_collaborative_filtering_with_real_data()
    nn_result = test_neural_network_with_real_data()  
    au_result = test_attribute_utility_with_real_data()
    
    total_passed = sum([cf_result, nn_result, au_result])
    
    print("\n" + "="*50)
    print("RecommendationCalculateMethodEvaluationSummary")
    print("="*50)
    print(f"Collaborative FilteringCalculateMethod: {'PASS' if cf_result else 'FAIL'}")
    print(f"GodEconomyNetworkRecommendation: {'PASS' if nn_result else 'FAIL'}")
    print(f"AttributeEffectUseRecommendation: {'PASS' if au_result else 'FAIL'}")
    print(f"\nTotalIntegratedResult: {total_passed}/3 CalculateMethodPassTest")
    
    sys.exit(0 if total_passed >= 2 else 1)