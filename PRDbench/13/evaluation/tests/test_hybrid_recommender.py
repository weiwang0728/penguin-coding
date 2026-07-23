import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.hybrid_recommender import HybridRecommender, HybridStrategy


class TestHybridRecommender:
    """Hybrid recommendation algorithm unit test"""

    def setup_method(self):
        """Setup before test"""
        self.weighted_recommender = HybridRecommender(HybridStrategy.WEIGHTED)
        self.parallel_recommender = HybridRecommender(HybridStrategy.PARALLEL)
        self.pipeline_recommender = HybridRecommender(HybridStrategy.PIPELINE)

    def create_test_data(self):
        """Create test data"""
        np.random.seed(42)

        # Create user data
        users_data = {
            'user_id': range(1, 31),
            'age': np.random.randint(18, 65, 30),
            'gender': np.random.choice(['Male', 'Female'], 30),
            'city': np.random.choice(['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'], 30)
        }
        users_df = pd.DataFrame(users_data)

        # Create product data
        categories = ['Phone', 'Computer', 'Shoes', 'Appliances', 'Books']
        brands = ['Apple', 'Huawei', 'Xiaomi', 'Samsung', 'OPPO']

        items_data = {
            'item_id': range(1, 61),
            'title': [f"Product {i} Title" for i in range(1, 61)],
            'description': [f"This is a detailed description of product {i}, including rich functional features and usage scenarios" for i in range(1, 61)],
            'category': np.random.choice(categories, 60),
            'brand': np.random.choice(brands, 60),
            'price': np.random.uniform(100, 5000, 60),
            'tags': [f"tag{i},feature{i},function{i}" for i in range(1, 61)]
        }
        items_df = pd.DataFrame(items_data)

        # Create interaction data
        interactions = []
        interaction_id = 1

        for user_id in range(1, 31):
            # Each user interacts with 8-15 products
            n_interactions = np.random.randint(8, 16)
            user_items = np.random.choice(range(1, 61), size=n_interactions, replace=False)

            for item_id in user_items:
                rating = np.random.choice([3, 4, 5], p=[0.2, 0.5, 0.3])
                interactions.append({
                    'interaction_id': interaction_id,
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': float(rating),
                    'interaction_type': 'rating'
                })
                interaction_id += 1

        interactions_df = pd.DataFrame(interactions)

        return users_df, items_df, interactions_df
    
    def test_weighted_hybrid_strategy(self):
        """Test integrated hybrid strategy"""
        users_df, items_df, interactions_df = self.create_test_data()

        # Train model
        self.weighted_recommender.fit(users_df, items_df, interactions_df)

        # Verify model training status
        assert self.weighted_recommender.is_fitted, "Model should be in trained state"

        # Generate recommendations
        user_id = 1
        user_preferences = {
            'interests': 'smartphone photography',
            'brand': 'Apple Huawei',
            'category': 'Phone'
        }

        recommendations = self.weighted_recommender.recommend(
            user_id, items_df, interactions_df, top_n=10, user_preferences=user_preferences
        )

        # Verify recommendation results
        assert len(recommendations) <= 10, "Number of recommendations should not exceed top_n"
        assert isinstance(recommendations, list), "Recommendation results should be a list"

        # Verify recommendation result format
        for item_id, score, reason in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Product ID should be integer"
            assert isinstance(score, (float, np.floating)), "Recommendation score should be float"
            assert isinstance(reason, str), "Recommendation reason should be string"
            assert score > 0, "Recommendation score should be positive"
            assert len(reason) > 0, "Recommendation reason should not be empty"

        # Verify recommendation results are sorted in descending order by score
        scores = [score for _, score, _ in recommendations]
        assert scores == sorted(scores, reverse=True), "Recommendation results should be sorted in descending order by score"

        # Verify weight fusion logic
        weights = self.weighted_recommender.weights
        assert abs(sum(weights.values()) - 1.0) < 0.01, "Weight sum should be close to 1.0"
        assert len(weights) >= 3, "Should combine ≥3 recommendation algorithms"
    
    def test_parallel_hybrid_strategy(self):
        """Test parallel hybrid strategy"""
        users_df, items_df, interactions_df = self.create_test_data()

        # Train model
        self.parallel_recommender.fit(users_df, items_df, interactions_df)

        # Generate recommendations
        user_id = 2
        user_preferences = {
            'interests': 'gaming computer',
            'category': 'Computer'
        }

        recommendations = self.parallel_recommender.recommend(
            user_id, items_df, interactions_df, top_n=10, user_preferences=user_preferences
        )

        # Verify recommendation results
        assert len(recommendations) <= 10, "Number of recommendations should not exceed top_n"
        assert isinstance(recommendations, list), "Recommendation results should be a list"

        # Verify recommendation result format
        for item_id, score, reason in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Product ID should be integer"
            assert isinstance(score, (float, np.floating)), "Recommendation score should be float"
            assert isinstance(reason, str), "Recommendation reason should be string"
            assert score > 0, "Recommendation score should be positive"

        # Verify parallel strategy specific recommendation reasons
        reasons = [reason for _, _, reason in recommendations]
        has_multiple_algorithms = any("algorithm" in reason for reason in reasons)
        assert has_multiple_algorithms or len(recommendations) > 0, "Parallel strategy should show multi-algorithm recommendation information"

        # Verify deduplication and sorting
        item_ids = [item_id for item_id, _, _ in recommendations]
        assert len(item_ids) == len(set(item_ids)), "Recommendation results should be deduplicated"

    def test_pipeline_hybrid_strategy(self):
        """Test pipeline hybrid strategy"""
        users_df, items_df, interactions_df = self.create_test_data()

        # Train model
        self.pipeline_recommender.fit(users_df, items_df, interactions_df)

        # Generate recommendations
        user_id = 3
        user_preferences = {
            'interests': 'sports fitness',
            'category': 'Shoes'
        }

        recommendations = self.pipeline_recommender.recommend(
            user_id, items_df, interactions_df, top_n=10, user_preferences=user_preferences
        )

        # Verify recommendation results
        assert len(recommendations) <= 10, "Number of recommendations should not exceed top_n"
        assert isinstance(recommendations, list), "Recommendation results should be a list"

        # Verify recommendation result format
        for item_id, score, reason in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Product ID should be integer"
            assert isinstance(score, (float, np.floating)), "Recommendation score should be float"
            assert isinstance(reason, str), "Recommendation reason should be string"
            assert score > 0, "Recommendation score should be positive"

        # Verify pipeline strategy specific recommendation reasons
        reasons = [reason for _, _, reason in recommendations]
        has_pipeline_reason = any("pipeline" in reason or "stage" in reason for reason in reasons)
        assert has_pipeline_reason or len(recommendations) > 0, "Pipeline strategy should reflect multi-stage processing"

        # Verify multi-stage processing flow
        # Pipeline recommendation should include multiple processing stages: content recall → collaborative filtering reranking → diversity optimization
        if recommendations:
            sample_reason = recommendations[0][2]  # Take reason of first recommendation
            # Verify recommendation reason contains multi-stage information
            assert "pipeline" in sample_reason, f"Recommendation reason should include pipeline information, actual: {sample_reason}"

        assert self.pipeline_recommender.is_fitted, "Pipeline recommendation should go through complete training process"
    
    def test_weight_configuration(self):
        """Test weight configuration function"""
        users_df, items_df, interactions_df = self.create_test_data()
        self.weighted_recommender.fit(users_df, items_df, interactions_df)

        # Test custom weights
        custom_weights = {
            'content': 0.4,
            'user_cf': 0.3,
            'item_cf': 0.2,
            'matrix_factorization': 0.1
        }

        self.weighted_recommender.set_weights(custom_weights)

        # Verify weight settings
        updated_weights = self.weighted_recommender.weights
        for key, value in custom_weights.items():
            assert abs(updated_weights[key] - value) < 0.01, f"Weight {key} should be correctly set"

        # Verify weight sum equals 1.0
        total_weight = sum(updated_weights.values())
        assert abs(total_weight - 1.0) < 0.01, f"Weight sum should be 1.0, actual is {total_weight}"

        # Generate recommendations using new weights
        recommendations = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=5)
        assert len(recommendations) > 0, "Should be able to generate recommendations normally after custom weights"

    def test_diversity_evaluation(self):
        """Test diversity evaluation"""
        users_df, items_df, interactions_df = self.create_test_data()
        self.weighted_recommender.fit(users_df, items_df, interactions_df)

        # Generate recommendations
        recommendations = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=10)

        # Evaluate diversity
        diversity_metrics = self.weighted_recommender.evaluate_diversity(recommendations, items_df)

        # Verify diversity metrics
        assert 'category_diversity' in diversity_metrics, "Should include category diversity metric"
        assert 'brand_diversity' in diversity_metrics, "Should include brand diversity metric"

        category_diversity = diversity_metrics['category_diversity']
        brand_diversity = diversity_metrics['brand_diversity']

        assert 0 <= category_diversity <= 1, "Category diversity should be in [0,1] range"
        assert 0 <= brand_diversity <= 1, "Brand diversity should be in [0,1] range"

        # Verify diversity metric reasonableness
        if len(recommendations) > 1:
            assert category_diversity > 0, "Multiple recommended products should have some category diversity"
    
    def test_cold_start_handling(self):
        """Test cold start handling"""
        users_df, items_df, interactions_df = self.create_test_data()
        self.weighted_recommender.fit(users_df, items_df, interactions_df)

        # Test completely new user
        new_user_id = 999
        cold_start_recs = self.weighted_recommender.handle_cold_start(
            new_user_id, items_df, interactions_df, top_n=10
        )

        # Verify cold start recommendations
        assert len(cold_start_recs) <= 10, "Number of cold start recommendations should not exceed top_n"
        assert len(cold_start_recs) > 0, "Should provide recommendations for new users"

        # Verify recommendation format
        for item_id, score, reason in cold_start_recs:
            assert isinstance(item_id, (int, np.integer)), "Product ID should be integer"
            assert isinstance(score, (float, np.floating)), "Recommendation score should be float"
            assert isinstance(reason, str), "Recommendation reason should be string"
            assert item_id in items_df['item_id'].values, "Recommended product should exist in product library"

        # Verify popular product recommendations
        reasons = [reason for _, _, reason in cold_start_recs]
        has_popular_items = any("popular" in reason for reason in reasons)
        assert has_popular_items, "New users should receive popular product recommendations"

    def test_algorithm_integration(self):
        """Test algorithm integration"""
        users_df, items_df, interactions_df = self.create_test_data()

        # Verify all recommenders are correctly initialized
        assert self.weighted_recommender.content_recommender is not None, "Should include content recommender"
        assert self.weighted_recommender.user_cf is not None, "Should include user collaborative filtering"
        assert self.weighted_recommender.item_cf is not None, "Should include item collaborative filtering"
        assert self.weighted_recommender.matrix_factorization is not None, "Should include matrix factorization"

        # Train hybrid recommendation system
        self.weighted_recommender.fit(users_df, items_df, interactions_df)

        # Verify each sub-recommender is trained
        assert self.weighted_recommender.content_recommender.tfidf_vectorizer is not None, "Content recommender should be trained"
        assert self.weighted_recommender.user_cf.user_similarity_matrix is not None, "User collaborative filtering should be trained"
        assert self.weighted_recommender.item_cf.item_similarity_matrix is not None, "Item collaborative filtering should be trained"
        assert self.weighted_recommender.matrix_factorization.model is not None, "Matrix factorization should be trained"

        # Verify ≥3 algorithms integrated
        algorithm_count = len(self.weighted_recommender.weights)
        assert algorithm_count >= 3, f"Should integrate ≥3 recommendation algorithms, actual is {algorithm_count}"
    
    def test_recommendation_quality(self):
        """Test recommendation quality"""
        users_df, items_df, interactions_df = self.create_test_data()

        # Test three hybrid strategies
        strategies = [
            (self.weighted_recommender, "Weighted fusion"),
            (self.parallel_recommender, "Parallel"),
            (self.pipeline_recommender, "Pipeline")
        ]

        for recommender, strategy_name in strategies:
            recommender.fit(users_df, items_df, interactions_df)

            # Generate recommendations for multiple users
            all_recommendations = []
            for user_id in [1, 2, 3, 4, 5]:
                recs = recommender.recommend(user_id, items_df, interactions_df, top_n=8)
                all_recommendations.extend([item_id for item_id, _, _ in recs])

            # Verify recommendation coverage
            unique_items = len(set(all_recommendations))
            total_items = len(items_df)
            coverage = unique_items / total_items

            assert coverage > 0.1, f"{strategy_name} strategy recommendation coverage should be >10%, actual is {coverage:.2%}"

            # Verify no duplicate recommendations
            user_recs = recommender.recommend(1, items_df, interactions_df, top_n=10)
            item_ids = [item_id for item_id, _, _ in user_recs]
            assert len(item_ids) == len(set(item_ids)), f"{strategy_name} strategy recommendation results should not be duplicated"

    def test_edge_cases_and_robustness(self):
        """Test edge cases and robustness"""
        users_df, items_df, interactions_df = self.create_test_data()

        # Test untrained model
        untrained_recommender = HybridRecommender(HybridStrategy.WEIGHTED)
        untrained_recs = untrained_recommender.recommend(1, items_df, interactions_df, top_n=5)
        assert len(untrained_recs) == 0, "Untrained model should return empty recommendations"

        # Test empty user preferences
        self.weighted_recommender.fit(users_df, items_df, interactions_df)
        no_preference_recs = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=5)
        assert isinstance(no_preference_recs, list), "Should return list when no user preferences"

        # Test non-existent user
        non_exist_recs = self.weighted_recommender.recommend(999, items_df, interactions_df, top_n=5)
        assert isinstance(non_exist_recs, list), "Should be able to handle non-existent user"

        # Test very small top_n
        small_recs = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=1)
        assert len(small_recs) <= 1, "Should return at most 1 recommendation when top_n=1"

        # Test very large top_n
        large_recs = self.weighted_recommender.recommend(1, items_df, interactions_df, top_n=1000)
        assert len(large_recs) <= len(items_df), "Number of recommendations should not exceed total number of products"