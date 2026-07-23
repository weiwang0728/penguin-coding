# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
import numpy as np

# AddsrcDirectorytoPythonPath
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from recommenders.collaborative_filtering_recommender import CollaborativeFilteringRecommender

class TestCollaborativeFiltering:
    """Collaborative FilteringRecommendation-ManyTypeCameraSimilarRepublicDesignCalculateTest"""
    
    def setup_method(self):
        """TestbeforeStandardPrepare"""
        self.config = {
            'recommendation': {
                'default_top_n': 5,
                'min_ratings': 3
            }
        }
        
        # CreateTestData
        self.ratings_df = pd.DataFrame({
            'user_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'product_id': [1, 2, 3, 1, 2, 4, 2, 3, 4],
            'rating': [5.0, 4.0, 3.0, 4.0, 5.0, 3.0, 3.0, 4.0, 5.0]
        })
        
        self.products_df = pd.DataFrame({
            'product_id': [1, 2, 3, 4],
            'name': ['ProductBrandA', 'ProductBrandB', 'ProductBrandC', 'ProductBrandD'],
            'category': ['Electronics', 'Clothing', 'Home', 'Book'],
            'brand': ['BrandBrandA', 'BrandBrandB', 'BrandBrandC', 'BrandBrandD'],
            'price': [100.0, 200.0, 300.0, 400.0],
            'price_range': ['LowPrice', 'MidPrice', 'MidPrice', 'HighPrice'],
            'avg_rating': [4.0, 4.5, 3.5, 4.5]
        })
        
        self.users_df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'age': [25, 30, 35],
            'gender': ['Male', 'Female', 'Male']
        })
    
    def test_cosine_similarity(self):
        """TestCosineSimilarity"""
        recommender = CollaborativeFilteringRecommender(self.config, similarity_metric='cosine')
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        # asUser1GenerateRecommendation
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        # Breakassertion：CosineSimilarityDesignCalculateCorrectAccurate
        assert len(recommendations) > 0, "CosineSimilarityRecommendationResultNotShouldasEmpty"
        assert all('score' in rec for rec in recommendations), "RecommendationResultShouldContainsDivideNumber"
        assert recommender.similarity_metric == 'cosine', "ShouldUseUseCosineSimilarity"
    
    def test_pearson_similarity(self):
        """TestPearsonCorrelation"""
        recommender = CollaborativeFilteringRecommender(self.config, similarity_metric='pearson')
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        # Breakassertion：PearsonCorrelationDesignCalculateCorrectAccurate
        assert len(recommendations) > 0, "PearsonCorrelationRecommendationResultNotShouldasEmpty"
        assert recommender.similarity_metric == 'pearson', "ShouldUseUsePearsonCorrelation"
    
    def test_euclidean_similarity(self):
        """TestEuclideanDistance"""
        recommender = CollaborativeFilteringRecommender(self.config, similarity_metric='euclidean')
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        recommendations = recommender.predict(user_id=1, top_n=3)
        
        # Breakassertion：EuclideanDistanceDesignCalculateCorrectAccurate
        assert len(recommendations) > 0, "EuclideanDistanceRecommendationResultNotShouldasEmpty"
        assert recommender.similarity_metric == 'euclidean', "ShouldUseUseEuclideanDistance"
    
    def test_similarity_methods_difference(self):
        """TestNotSameCameraSimilarRepublicOfficialMethodMadeNativeNotSameResult"""
        # CreateSamitem(s)NotSameRecommendationDevice
        cosine_rec = CollaborativeFilteringRecommender(self.config, similarity_metric='cosine')
        pearson_rec = CollaborativeFilteringRecommender(self.config, similarity_metric='pearson')
        euclidean_rec = CollaborativeFilteringRecommender(self.config, similarity_metric='euclidean')
        
        # TrainingModelType
        cosine_rec.fit(self.ratings_df, self.products_df)
        pearson_rec.fit(self.ratings_df, self.products_df)
        euclidean_rec.fit(self.ratings_df, self.products_df)
        
        # GenerateRecommendation
        cosine_recs = cosine_rec.recommend(user_id=1, top_n=3)
        pearson_recs = pearson_rec.recommend(user_id=1, top_n=3)
        euclidean_recs = euclidean_rec.recommend(user_id=1, top_n=3)
        
        # Breakassertion：NotSameOfficialMethodMadeNativeRecommendationResultShouldHasDifferenceDifferent
        cosine_scores = [rec['score'] for rec in cosine_recs]
        pearson_scores = [rec['score'] for rec in pearson_recs]
        euclidean_scores = [rec['score'] for rec in euclidean_recs]
        
        # ToFewHasOneitem(s)OfficialMethodResultandOtherOfficialMethodNotSame
        methods_different = (cosine_scores != pearson_scores or 
                           pearson_scores != euclidean_scores or 
                           cosine_scores != euclidean_scores)
        
        assert methods_different, "NotSameCameraSimilarRepublicOfficialMethodShouldMadeNativeNotSameRecommendationResult"


# AddIndependentTestFunctionNumber，CanByDirectInterfacePassFunctionNumberNameAdjustUse
def test_cosine_similarity():
    """TestCosineSimilarity（IndependentFunctionNumberEditionBook）"""
    test_instance = TestCollaborativeFiltering()
    test_instance.setup_method()
    test_instance.test_cosine_similarity()


def test_pearson_similarity():
    """TestPearsonCorrelation（IndependentFunctionNumberEditionBook）"""
    test_instance = TestCollaborativeFiltering()
    test_instance.setup_method()
    test_instance.test_pearson_similarity()


def test_euclidean_similarity():
    """TestEuclideanDistance（IndependentFunctionNumberEditionBook）"""
    test_instance = TestCollaborativeFiltering()
    test_instance.setup_method()
    test_instance.test_euclidean_similarity()