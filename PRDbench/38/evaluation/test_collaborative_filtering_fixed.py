#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import sys
import os

# AddsrcDirectorytoPath
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

from recommenders.collaborative_filtering_recommender import CollaborativeFilteringRecommender

def create_proper_test_data():
    """CreateContainsPlaceNeedCharacterSegmentCorrectAccurateTestData"""
    ratings_df = pd.DataFrame({
        'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'product_id': [1, 2, 3, 1, 2, 4, 2, 3, 4],
        'rating': [5.0, 4.0, 3.0, 4.0, 5.0, 3.0, 3.0, 4.0, 5.0]
    })
    
    products_df = pd.DataFrame({
        'product_id': [1, 2, 3, 4],
        'name': ['ProductBrandA', 'ProductBrandB', 'ProductBrandC', 'ProductBrandD'],
        'category': ['Electronics', 'Clothing', 'Home', 'Book'],
        'brand': ['BrandBrandA', 'BrandBrandB', 'BrandBrandC', 'BrandBrandD'],
        'price': [100.0, 200.0, 300.0, 400.0],
        'price_range': ['low', 'medium', 'high', 'high']
    })
    
    return ratings_df, products_df

def test_cosine_similarity():
    """TestCosineSimilarity"""
    try:
        config = {'recommendation': {'default_top_n': 5, 'min_ratings': 3}}
        ratings_df, products_df = create_proper_test_data()
        
        recommender = CollaborativeFilteringRecommender(config, similarity_metric='cosine')
        recommender.fit(ratings_df, products_df)
        
        # UseUseCorrectAccurateOfficialMethodNamepredict
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        print("PASS: CosineSimilarityCalculateMethodTest Passed")
        print(f"RecommendationResultQuantity: {len(recommendations)}")
        print(f"CalculateMethodCategoryType: {recommender.similarity_metric}")
        
        return True
        
    except Exception as e:
        print(f"FAIL: CosineSimilarityTest Failed: {e}")
        return False

def test_pearson_similarity():
    """TestPearsonCorrelation"""
    try:
        config = {'recommendation': {'default_top_n': 5}}
        ratings_df, products_df = create_proper_test_data()
        
        recommender = CollaborativeFilteringRecommender(config, similarity_metric='pearson')
        recommender.fit(ratings_df, products_df)
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        print("PASS: PearsonCorrelationTest Passed")
        print(f"CalculateMethodCategoryType: {recommender.similarity_metric}")
        return True
        
    except Exception as e:
        print(f"FAIL: PiErxunTest Failed: {e}")
        return False

def test_euclidean_similarity():
    """TestEuclideanDistance"""
    try:
        config = {'recommendation': {'default_top_n': 5}}
        ratings_df, products_df = create_proper_test_data()
        
        recommender = CollaborativeFilteringRecommender(config, similarity_metric='euclidean')
        recommender.fit(ratings_df, products_df)
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        print("PASS: EuclideanDistanceTest Passed")
        print(f"CalculateMethodCategoryType: {recommender.similarity_metric}")
        return True
        
    except Exception as e:
        print(f"FAIL: OuEuclideanTest Failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Collaborative FilteringRecommendationCalculateMethodEvaluation")
    print("=" * 50)
    
    results = []
    results.append(test_cosine_similarity())
    results.append(test_pearson_similarity()) 
    results.append(test_euclidean_similarity())
    
    passed = sum(results)
    print(f"\nCollaborative FilteringEvaluation Results: {passed}/3 Pass")
    
    sys.exit(0 if passed == 3 else 1)