# -*- coding: utf-8 -*-
import pytest
import sys
import os
import pandas as pd
import numpy as np

# AddsrcDirectorytoPythonPath
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from recommenders.neural_network_recommender import NeuralNetworkRecommender

class TestNeuralNetwork:
    """LightweightNeuralNetworkRecommendation-MLPRegressorUseUseTest"""
    
    def setup_method(self):
        """TestbeforeStandardPrepare"""
        self.config = {
            'recommendation': {
                'default_top_n': 5,
                'min_ratings': 3
            },
            'neural_network': {
                'hidden_layer_sizes': [64, 32],
                'max_iter': 500,
                'random_state': 42
            }
        }
        
        # CreateTestData
        # CreateSufficientLargeTestDataSet（30recordsByMeetsVerifySetRequirements）
        user_ids = []
        product_ids = []
        ratings = []
        
        for user in range(1, 11):  # 10item(s)User
            for product in range(1, 6):  # 5item(s)ProductBrand
                if np.random.random() > 0.3:  # 70%SummaryRateHasScore
                    user_ids.append(user)
                    product_ids.append(product)
                    ratings.append(np.random.randint(3, 6))  # 3-5DivideScore
        
        self.ratings_df = pd.DataFrame({
            'user_id': user_ids,
            'product_id': product_ids,
            'rating': ratings
        })
        
        self.products_df = pd.DataFrame({
            'product_id': [1, 2, 3, 4, 5],
            'name': ['ProductBrandA', 'ProductBrandB', 'ProductBrandC', 'ProductBrandD', 'ProductBrandE'],
            'category': ['Electronics', 'Clothing', 'Home', 'Book', 'RunAuto'],
            'brand': ['BrandBrandA', 'BrandBrandB', 'BrandBrandC', 'BrandBrandD', 'BrandBrandE'],
            'price': [100.0, 200.0, 300.0, 400.0, 500.0],
            'price_range': ['LowPrice', 'MidPrice', 'MidPrice', 'HighPrice', 'HighPrice'],
            'avg_rating': [4.0, 4.5, 3.5, 4.5, 3.8]
        })
        
        self.users_df = pd.DataFrame({
            'user_id': range(1, 11),
            'age': np.random.randint(20, 60, 10),
            'gender': np.random.choice(['Male', 'Female'], 10)
        })
    
    def test_mlp_regressor_usage(self):
        """TestMLPRegressorUseUseandCPUTraining"""
        recommender = NeuralNetworkRecommender(self.config)
        
        # TrainingModelType
        recommender.fit(self.ratings_df, self.products_df, self.users_df)
        
        # Breakassertion：ModelTypeUseUseMLPRegressor
        assert hasattr(recommender, 'model'), "ShouldThisHasWellTrainedModelType"
        
        # Breakassertion：CPUTrainingSuccess（NoGPUDependDepend）
        assert recommender.is_trained, "ModelTypeShouldThisSuccessTraining"
        
        # GenerateRecommendation
        recommendations = recommender.predict(user_id=1, top_n=5)
        
        # Breakassertion：EnergyOutputRecommendationResult
        assert len(recommendations) > 0, "ShouldThisEnergyGenerateRecommendationResult"
        assert all('score' in rec for rec in recommendations), "RecommendationResultShouldContainsDivideNumber"
        
        # Breakassertion：VerifyModelTypeCategoryTypeandTrainingStatus
        assert str(type(recommender.model)).find('MLPRegressor') != -1, "ShouldUseUsescikit-learnMLPRegressor"
        print("✓ UseUsescikit-learn MLPRegressor，CPUTrainingCompleteSuccess")


# AddIndependentTestFunctionNumber，CanByDirectInterfacePassFunctionNumberNameAdjustUse
def test_mlp_regressor_usage():
    """TestMLPRegressorUseUseandCPUTraining（IndependentFunctionNumberEditionBook）"""
    test_instance = TestNeuralNetwork()
    test_instance.setup_method()
    test_instance.test_mlp_regressor_usage()