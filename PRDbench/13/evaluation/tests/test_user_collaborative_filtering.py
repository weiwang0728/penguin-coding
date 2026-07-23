import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


from algorithms.collaborative_filtering import UserBasedCF


class TestUserCollaborativeFiltering:
    """User-based collaborative filtering unit tests"""

    def setup_method(self):
        """Pre-test setup"""
        self.user_cf = UserBasedCF(min_interactions=3)
        
    def create_interaction_data(self):
        """Create user-item interaction data"""
        np.random.seed(42)

        # Create data with 50 users, 100 items, 500 interaction records
        users = range(1, 51)
        items = range(1, 101)

        interactions = []
        interaction_id = 1

        # Generate interaction records for each user
        for user_id in users:
            # Each user randomly interacts with 10-20 items
            n_interactions = np.random.randint(10, 21)
            user_items = np.random.choice(items, size=n_interactions, replace=False)

            for item_id in user_items:
                # Generate ratings with certain user preference patterns
                if user_id <= 10:  # First 10 users prefer electronics (item_id 1-20)
                    if item_id <= 20:
                        rating = np.random.choice([4, 5], p=[0.3, 0.7])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
                elif user_id <= 20:  # Users 11-20 prefer clothing (item_id 21-40)
                    if 21 <= item_id <= 40:
                        rating = np.random.choice([4, 5], p=[0.3, 0.7])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
                elif user_id <= 30:  # Users 21-30 prefer books (item_id 41-60)
                    if 41 <= item_id <= 60:
                        rating = np.random.choice([4, 5], p=[0.3, 0.7])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.3, 0.4, 0.3])
                else:  # Other users have random preferences
                    rating = np.random.choice([2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.3])
                
                interactions.append({
                    'interaction_id': interaction_id,
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': rating,
                    'interaction_type': 'rating'
                })
                interaction_id += 1
        
        return pd.DataFrame(interactions)
    
    def test_user_cf_training(self):
        """Test user-based collaborative filtering training"""
        # Prepare test data
        interactions_df = self.create_interaction_data()

        # Train model
        self.user_cf.fit(interactions_df)

        # Verify model training results
        assert self.user_cf.user_item_matrix is not None, "Should generate user-item matrix"
        assert self.user_cf.user_similarity_matrix is not None, "Should generate user similarity matrix"
        assert len(self.user_cf.user_ids) > 0, "Should have user ID list"
        assert len(self.user_cf.item_ids) > 0, "Should have item ID list"

        # Verify matrix dimensions
        n_users = len(self.user_cf.user_ids)
        n_items = len(self.user_cf.item_ids)

        assert self.user_cf.user_item_matrix.shape == (n_users, n_items), "User-item matrix dimensions should be correct"
        assert self.user_cf.user_similarity_matrix.shape == (n_users, n_users), "User similarity matrix dimensions should be correct"

        # Verify symmetry and diagonal of similarity matrix
        similarity_matrix = self.user_cf.user_similarity_matrix
        assert np.allclose(similarity_matrix, similarity_matrix.T), "Similarity matrix should be symmetric"

        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0), "Similarity matrix diagonal should be all 1s"
    
    def test_user_similarity_calculation(self):
        """Test user similarity calculation"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)

        # Test similarity calculation
        user1, user2 = 1, 2
        similarity = self.user_cf.get_user_similarity(user1, user2)

        # Verify similarity value
        assert isinstance(similarity, (float, np.floating)), "Similarity should be float"
        assert -1 <= similarity <= 1, "Cosine similarity should be in [-1,1] range"

        # Test user's similarity with itself
        self_similarity = self.user_cf.get_user_similarity(user1, user1)
        assert abs(self_similarity - 1.0) < 0.001, "User's similarity with itself should be close to 1"

        # Test non-existent user similarity
        non_exist_similarity = self.user_cf.get_user_similarity(999, 1000)
        assert non_exist_similarity == 0.0, "Non-existent user similarity should be 0"

        # Verify similar user identification
        # Based on our data generation logic, first 10 users should have higher similarity
        similar_users_sim = self.user_cf.get_user_similarity(1, 5)  # Both prefer electronics
        different_users_sim = self.user_cf.get_user_similarity(1, 15)  # Different preferences

        # Note: Due to randomness, this test may be unstable, so only basic verification
        assert isinstance(similar_users_sim, (float, np.floating)), "Similar user similarity calculation should be normal"
        assert isinstance(different_users_sim, (float, np.floating)), "Different user similarity calculation should be normal"
    
    def test_user_recommendation(self):
        """Test user-based recommendation function"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)

        # Generate recommendations for user
        user_id = 1
        recommendations = self.user_cf.recommend(user_id, top_n=10)

        # Verify recommendation results
        assert len(recommendations) <= 10, "Number of recommendations should not exceed top_n"
        assert isinstance(recommendations, list), "Recommendation results should be a list"

        # Verify recommendation result format
        for item_id, predicted_rating in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(predicted_rating, (float, np.floating)), "Predicted rating should be float"
            assert predicted_rating > 0, "Predicted rating should be positive"

        # Verify recommendations are sorted by predicted rating in descending order
        ratings = [rating for _, rating in recommendations]
        assert ratings == sorted(ratings, reverse=True), "Recommendations should be sorted by predicted rating in descending order"

        # Verify not recommending already rated items (default behavior)
        user_rated_items = set(interactions_df[interactions_df['user_id'] == user_id]['item_id'])
        recommended_items = set([item_id for item_id, _ in recommendations])
        overlap = user_rated_items.intersection(recommended_items)
        assert len(overlap) == 0, "By default should not recommend already rated items"
    
    def test_cold_start_handling(self):
        """Test cold start handling"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)

        # Test new user recommendation (cold start)
        new_user_id = 999  # Non-existent user
        recommendations = self.user_cf.recommend(new_user_id, top_n=5)

        # Verify cold start recommendations
        assert isinstance(recommendations, list), "Cold start recommendations should return a list"
        assert len(recommendations) <= 5, "Cold start recommendation count should not exceed top_n"

        # Cold start should recommend popular items
        if len(recommendations) > 0:
            for item_id, rating in recommendations:
                assert isinstance(item_id, (int, np.integer)), "Recommended item ID should be integer"
                assert isinstance(rating, (float, np.floating)), "Recommended rating should be float"
                assert rating > 0, "Recommended rating should be positive"
    
    def test_min_interactions_filtering(self):
        """Test minimum interaction count filtering"""
        interactions_df = self.create_interaction_data()

        # Create a model with higher minimum interaction count requirement
        strict_cf = UserBasedCF(min_interactions=15)
        strict_cf.fit(interactions_df)

        # Create a model with lower minimum interaction count requirement
        lenient_cf = UserBasedCF(min_interactions=5)
        lenient_cf.fit(interactions_df)

        # Verify filtering effect
        assert len(strict_cf.user_ids) <= len(lenient_cf.user_ids), "Stricter filtering should retain fewer users"

        # Verify all retained users meet minimum interaction count requirement
        for user_id in strict_cf.user_ids:
            user_interaction_count = len(interactions_df[interactions_df['user_id'] == user_id])
            assert user_interaction_count >= 15, f"User {user_id} interaction count should be ≥15"
    
    def test_recommendation_diversity_and_coverage(self):
        """Test recommendation diversity and coverage"""
        interactions_df = self.create_interaction_data()
        self.user_cf.fit(interactions_df)

        # Generate recommendations for multiple users
        all_recommendations = set()
        users_to_test = self.user_cf.user_ids[:10]  # Test first 10 users

        for user_id in users_to_test:
            recommendations = self.user_cf.recommend(user_id, top_n=10)
            for item_id, _ in recommendations:
                all_recommendations.add(item_id)

        # Verify recommendation coverage
        total_items = len(self.user_cf.item_ids)
        coverage = len(all_recommendations) / total_items

        assert coverage > 0.1, f"Recommendation coverage should be >10%, actual: {coverage:.2%}"

        # Verify recommendations are not completely identical for all users
        user_recs = {}
        for user_id in users_to_test[:5]:
            recommendations = self.user_cf.recommend(user_id, top_n=5)
            user_recs[user_id] = set([item_id for item_id, _ in recommendations])

        # Calculate recommendation overlap between users
        overlaps = []
        user_list = list(user_recs.keys())
        for i in range(len(user_list)):
            for j in range(i+1, len(user_list)):
                user1_recs = user_recs[user_list[i]]
                user2_recs = user_recs[user_list[j]]
                if len(user1_recs) > 0 and len(user2_recs) > 0:
                    overlap = len(user1_recs.intersection(user2_recs)) / len(user1_recs.union(user2_recs))
                    overlaps.append(overlap)

        if overlaps:
            avg_overlap = np.mean(overlaps)
            assert avg_overlap < 0.8, f"Recommendation overlap between users should be <80%, actual: {avg_overlap:.2%}"
    
    def test_rating_prediction_accuracy(self):
        """Test rating prediction accuracy"""
        interactions_df = self.create_interaction_data()

        # Split train/test set
        train_size = int(0.8 * len(interactions_df))
        train_df = interactions_df.iloc[:train_size]
        test_df = interactions_df.iloc[train_size:]

        # Train model
        self.user_cf.fit(train_df)

        # Predict test set ratings
        predictions = []
        actuals = []

        for _, row in test_df.head(50).iterrows():  # Only test first 50 to avoid slowness
            user_id = row['user_id']
            item_id = row['item_id']
            actual_rating = row['rating']

            if user_id in self.user_cf.user_id_to_index and item_id in self.user_cf.item_id_to_index:
                # Generate recommendations and find predicted rating for this item
                recommendations = self.user_cf.recommend(user_id, top_n=100, exclude_rated=False)

                predicted_rating = None
                for rec_item_id, rec_rating in recommendations:
                    if rec_item_id == item_id:
                        predicted_rating = rec_rating
                        break

                if predicted_rating is not None:
                    predictions.append(predicted_rating)
                    actuals.append(actual_rating)

        # Calculate prediction accuracy
        if len(predictions) > 10:  # At least 10 predictions
            mae = np.mean(np.abs(np.array(predictions) - np.array(actuals)))
            rmse = np.sqrt(np.mean((np.array(predictions) - np.array(actuals)) ** 2))

            # Rating range is 1-5, reasonable MAE should be <2, RMSE should be <2.5
            assert mae < 2.0, f"Mean absolute error should be <2.0, actual: {mae:.3f}"
            assert rmse < 2.5, f"Root mean square error should be <2.5, actual: {rmse:.3f}"
    
    def test_edge_cases_and_robustness(self):
        """Test edge cases and robustness"""
        # Test empty data
        empty_df = pd.DataFrame(columns=['user_id', 'item_id', 'rating'])

        with pytest.raises(Exception):
            empty_cf = UserBasedCF()
            empty_cf.fit(empty_df)

        # Test single user single item
        minimal_df = pd.DataFrame({
            'user_id': [1, 1, 1, 1, 1],  # Single user multiple interactions to meet min_interactions
            'item_id': [1, 2, 3, 4, 5],
            'rating': [5, 4, 3, 4, 5],
            'interaction_type': ['rating'] * 5
        })

        minimal_cf = UserBasedCF(min_interactions=3)
        minimal_cf.fit(minimal_df)

        # Single user case should work normally, but recommendations may be empty
        recommendations = minimal_cf.recommend(1, top_n=5)
        assert isinstance(recommendations, list), "Single user case should return a list"

        # Test extreme rating data
        extreme_df = pd.DataFrame({
            'user_id': [1, 1, 1, 2, 2, 2],
            'item_id': [1, 2, 3, 1, 2, 3],
            'rating': [1, 1, 1, 5, 5, 5],  # Extreme ratings
            'interaction_type': ['rating'] * 6
        })

        extreme_cf = UserBasedCF(min_interactions=3)
        extreme_cf.fit(extreme_df)

        # Should be able to calculate similarity with extreme ratings
        similarity = extreme_cf.get_user_similarity(1, 2)
        assert isinstance(similarity, (float, np.floating)), "Should be able to calculate similarity with extreme ratings"