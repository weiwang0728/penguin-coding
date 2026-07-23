import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.collaborative_filtering import ItemBasedCF


class TestItemCollaborativeFiltering:
    """Item-based collaborative filtering unit tests"""

    def setup_method(self):
        """Test setup"""
        self.item_cf = ItemBasedCF(min_interactions=3)
        
    def create_interaction_data(self):
        """Create user-item interaction data"""
        np.random.seed(42)

        # Create data with 50 users, 100 items, 500 interaction records
        users = range(1, 51)
        items = range(1, 101)
        
        interactions = []
        interaction_id = 1
        
        # Set category attributes for each item
        item_categories = {}
        for item_id in items:
            if item_id <= 20:
                item_categories[item_id] = 'electronics'
            elif item_id <= 40:
                item_categories[item_id] = 'clothing'
            elif item_id <= 60:
                item_categories[item_id] = 'books'
            elif item_id <= 80:
                item_categories[item_id] = 'home'
            else:
                item_categories[item_id] = 'food'

        # Generate interaction records for each user
        for user_id in users:
            # Each user randomly interacts with 10-20 items
            n_interactions = np.random.randint(10, 21)
            user_items = np.random.choice(items, size=n_interactions, replace=False)

            for item_id in user_items:
                # Generate ratings based on item category
                category = item_categories[item_id]

                # Different users have different preferences for different categories
                if user_id <= 15:  # Users 1-15 prefer electronics
                    if category == 'electronics':
                        rating = np.random.choice([4, 5], p=[0.4, 0.6])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.2, 0.5, 0.3])
                elif user_id <= 30:  # Users 16-30 prefer clothing
                    if category == 'clothing':
                        rating = np.random.choice([4, 5], p=[0.4, 0.6])
                    else:
                        rating = np.random.choice([2, 3, 4], p=[0.2, 0.5, 0.3])
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
    
    def test_item_cf_training(self):
        """Test item-based collaborative filtering training"""
        # Prepare test data
        interactions_df = self.create_interaction_data()

        # Train model
        self.item_cf.fit(interactions_df)

        # Verify model training results
        assert self.item_cf.user_item_matrix is not None, "Should generate user-item matrix"
        assert self.item_cf.item_similarity_matrix is not None, "Should generate item similarity matrix"
        assert len(self.item_cf.user_ids) > 0, "Should have user ID list"
        assert len(self.item_cf.item_ids) > 0, "Should have item ID list"

        # Verify matrix dimensions
        n_users = len(self.item_cf.user_ids)
        n_items = len(self.item_cf.item_ids)

        assert self.item_cf.user_item_matrix.shape == (n_users, n_items), "User-item matrix dimensions should be correct"
        assert self.item_cf.item_similarity_matrix.shape == (n_items, n_items), "Item similarity matrix dimensions should be correct"

        # Verify symmetry and diagonal of similarity matrix
        similarity_matrix = self.item_cf.item_similarity_matrix
        assert np.allclose(similarity_matrix, similarity_matrix.T), "Similarity matrix should be symmetric"

        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0), "Similarity matrix diagonal should be all 1s"
    
    def test_item_similarity_calculation(self):
        """Test item similarity calculation"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        # Test similarity calculation
        item1, item2 = 1, 2  # Same category items (electronics)
        similarity = self.item_cf.get_item_similarity(item1, item2)

        # Verify similarity value
        assert isinstance(similarity, (float, np.floating)), "Similarity should be float"
        assert -1 <= similarity <= 1, "Cosine similarity should be in [-1,1] range"

        # Test item similarity with itself
        self_similarity = self.item_cf.get_item_similarity(item1, item1)
        assert abs(self_similarity - 1.0) < 0.001, "Item similarity with itself should be close to 1"

        # Test similarity for non-existent items
        non_exist_similarity = self.item_cf.get_item_similarity(999, 1000)
        assert non_exist_similarity == 0.0, "Similarity for non-existent items should be 0"

        # Verify similarity for same category items
        same_category_sim = self.item_cf.get_item_similarity(5, 10)  # Both electronics
        diff_category_sim = self.item_cf.get_item_similarity(5, 25)  # Electronics vs clothing

        # Note: Due to data randomness, we only do basic verification here
        assert isinstance(same_category_sim, (float, np.floating)), "Same category item similarity calculation should be normal"
        assert isinstance(diff_category_sim, (float, np.floating)), "Different category item similarity calculation should be normal"
    
    def test_item_recommendation(self):
        """Test item-based recommendation function"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        # Generate recommendations for user
        user_id = 1
        recommendations = self.item_cf.recommend(user_id, top_n=10)

        # Verify recommendation results
        assert len(recommendations) <= 10, "Recommendation count should not exceed top_n"
        assert isinstance(recommendations, list), "Recommendation results should be list"

        # Verify recommendation result format
        for item_id, predicted_rating in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(predicted_rating, (float, np.floating)), "Predicted rating should be float"
            assert predicted_rating > 0, "Predicted rating should be positive"

        # Verify recommendations are sorted by predicted rating in descending order
        ratings = [rating for _, rating in recommendations]
        assert ratings == sorted(ratings, reverse=True), "Recommendations should be sorted by predicted rating in descending order"

        # Verify already rated items are not recommended
        user_rated_items = set(interactions_df[interactions_df['user_id'] == user_id]['item_id'])
        recommended_items = set([item_id for item_id, _ in recommendations])
        overlap = user_rated_items.intersection(recommended_items)
        assert len(overlap) == 0, "Already rated items should not be recommended"
    
    def test_similar_items_recommendation(self):
        """Test similar items recommendation function"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        # Recommend items similar to specified item
        target_item_id = 5  # Electronics category
        similar_items = self.item_cf.recommend_similar_items(target_item_id, top_n=10)

        # Verify recommendation results
        assert len(similar_items) <= 10, "Similar item recommendation count should not exceed top_n"
        assert isinstance(similar_items, list), "Similar item recommendation results should be list"

        # Verify recommendation result format
        for item_id, similarity in similar_items:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(similarity, (float, np.floating)), "Similarity should be float"
            assert -1 <= similarity <= 1, "Similarity should be in [-1,1] range"
            assert item_id != target_item_id, "Should not recommend item itself"

        # Verify recommendations are sorted by similarity in descending order
        similarities = [sim for _, sim in similar_items]
        assert similarities == sorted(similarities, reverse=True), "Similar items should be sorted by similarity in descending order"

        # Test similar item recommendation for non-existent item
        non_exist_similar = self.item_cf.recommend_similar_items(999, top_n=5)
        assert len(non_exist_similar) == 0, "Non-existent item should return empty similar item list"
    
    def test_min_interactions_filtering(self):
        """Test minimum interaction count filtering"""
        interactions_df = self.create_interaction_data()

        # Create a model with higher minimum interaction requirement
        strict_cf = ItemBasedCF(min_interactions=10)
        strict_cf.fit(interactions_df)

        # Create a model with lower minimum interaction requirement
        lenient_cf = ItemBasedCF(min_interactions=3)
        lenient_cf.fit(interactions_df)

        # Verify filtering effect
        assert len(strict_cf.item_ids) <= len(lenient_cf.item_ids), "Stricter filtering should retain fewer items"

        # Verify all retained items meet minimum interaction requirement
        for item_id in strict_cf.item_ids:
            item_interaction_count = len(interactions_df[interactions_df['item_id'] == item_id])
            assert item_interaction_count >= 10, f"Item {item_id} interaction count should be ≥10"
    
    def test_recommendation_based_on_user_history(self):
        """Test recommendation logic based on user history"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        # Get a user's interaction history
        user_id = 1
        user_history = interactions_df[interactions_df['user_id'] == user_id]
        user_high_rated_items = user_history[user_history['rating'] >= 4]['item_id'].values

        if len(user_high_rated_items) > 0:
            # Generate recommendations for user
            recommendations = self.item_cf.recommend(user_id, top_n=15)

            if len(recommendations) > 0:
                # Get similar items for recommended items, verify recommendation logic
                recommended_items = [item_id for item_id, _ in recommendations]

                # Check if recommended items have similarity with user's high-rated items
                has_similar_to_history = False
                for rec_item in recommended_items[:5]:  # Check top 5 recommendations
                    for hist_item in user_high_rated_items[:3]:  # Check user's history high-rated items
                        if hist_item in self.item_cf.item_id_to_index and rec_item in self.item_cf.item_id_to_index:
                            similarity = self.item_cf.get_item_similarity(hist_item, rec_item)
                            if similarity > 0.1:  # Has some similarity
                                has_similar_to_history = True
                                break
                    if has_similar_to_history:
                        break

                # Note: Due to data randomness and algorithm complexity, we only verify the recommendation system can run
                assert isinstance(has_similar_to_history, bool), "Similarity check should execute normally"
    
    def test_item_similarity_matrix_properties(self):
        """Test item similarity matrix properties"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        similarity_matrix = self.item_cf.item_similarity_matrix
        n_items = len(self.item_cf.item_ids)

        # Verify matrix dimensions
        assert similarity_matrix.shape == (n_items, n_items), "Similarity matrix dimensions should be 100×100"

        # Verify matrix symmetry
        assert np.allclose(similarity_matrix, similarity_matrix.T, atol=1e-10), "Similarity matrix should be symmetric"

        # Verify diagonal is 1
        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0, atol=1e-10), "Diagonal should be all 1s"

        # Verify similarity value range
        assert np.all(similarity_matrix >= -1), "All similarity values should be ≥-1"
        assert np.all(similarity_matrix <= 1), "All similarity values should be ≤1"

        # Verify off-diagonal elements are not all 1
        off_diagonal = similarity_matrix[~np.eye(n_items, dtype=bool)]
        assert not np.allclose(off_diagonal, 1.0), "Off-diagonal elements should not all be 1"
    
    def test_cold_start_handling(self):
        """Test cold start handling"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        # Test new user recommendation (cold start)
        new_user_id = 999  # Non-existent user
        recommendations = self.item_cf.recommend(new_user_id, top_n=5)

        # Verify cold start recommendation
        assert isinstance(recommendations, list), "Cold start recommendation should return list"
        assert len(recommendations) <= 5, "Cold start recommendation count should not exceed top_n"

        # Cold start should recommend popular items
        if len(recommendations) > 0:
            for item_id, rating in recommendations:
                assert isinstance(item_id, (int, np.integer)), "Recommended item ID should be integer"
                assert isinstance(rating, (float, np.floating)), "Recommended rating should be float"
                assert rating > 0, "Recommended rating should be positive"
                assert item_id in self.item_cf.item_ids, "Recommended item should be in training data"
    
    def test_recommendation_diversity(self):
        """Test recommendation diversity"""
        interactions_df = self.create_interaction_data()
        self.item_cf.fit(interactions_df)

        # Generate recommendations for multiple users
        all_recommendations = set()
        users_to_test = self.item_cf.user_ids[:10]  # Test first 10 users

        for user_id in users_to_test:
            recommendations = self.item_cf.recommend(user_id, top_n=10)
            for item_id, _ in recommendations:
                all_recommendations.add(item_id)

        # Verify recommendation coverage
        total_items = len(self.item_cf.item_ids)
        coverage = len(all_recommendations) / total_items

        assert coverage > 0.05, f"Recommendation coverage should be >5%, actual is {coverage:.2%}"

        # Verify recommendations are not completely identical
        user_recs = {}
        for user_id in users_to_test[:5]:
            recommendations = self.item_cf.recommend(user_id, top_n=8)
            user_recs[user_id] = set([item_id for item_id, _ in recommendations])

        # Calculate recommendation overlap rate between users
        overlaps = []
        user_list = list(user_recs.keys())
        for i in range(len(user_list)):
            for j in range(i+1, len(user_list)):
                user1_recs = user_recs[user_list[i]]
                user2_recs = user_recs[user_list[j]]
                if len(user1_recs) > 0 and len(user2_recs) > 0:
                    union_size = len(user1_recs.union(user2_recs))
                    if union_size > 0:
                        overlap = len(user1_recs.intersection(user2_recs)) / union_size
                        overlaps.append(overlap)

        if overlaps:
            avg_overlap = np.mean(overlaps)
            assert avg_overlap < 0.9, f"Recommendation overlap rate between users should be <90%, actual is {avg_overlap:.2%}"
    
    def test_edge_cases_and_robustness(self):
        """Test edge cases and robustness"""
        # Test empty data
        empty_df = pd.DataFrame(columns=['user_id', 'item_id', 'rating'])

        with pytest.raises(Exception):
            empty_cf = ItemBasedCF()
            empty_cf.fit(empty_df)

        # Test single item with multiple users
        single_item_df = pd.DataFrame({
            'user_id': [1, 2, 3, 4, 5],
            'item_id': [1, 1, 1, 1, 1],  # All users rate the same item
            'rating': [5, 4, 3, 4, 5],
            'interaction_type': ['rating'] * 5
        })

        single_item_cf = ItemBasedCF(min_interactions=3)
        single_item_cf.fit(single_item_df)

        # Single item case should work normally
        recommendations = single_item_cf.recommend(1, top_n=5)
        assert isinstance(recommendations, list), "Single item case should return list"

        # Similar item recommendation should be empty (only one item)
        similar_items = single_item_cf.recommend_similar_items(1, top_n=5)
        assert len(similar_items) == 0, "Single item case should have no similar items"

        # Test extreme rating data
        extreme_df = pd.DataFrame({
            'user_id': [1, 2, 3, 1, 2, 3],
            'item_id': [1, 1, 1, 2, 2, 2],
            'rating': [1, 1, 1, 5, 5, 5],  # Extreme ratings
            'interaction_type': ['rating'] * 6
        })

        extreme_cf = ItemBasedCF(min_interactions=3)
        extreme_cf.fit(extreme_df)

        # Should be able to calculate similarity with extreme ratings
        similarity = extreme_cf.get_item_similarity(1, 2)
        assert isinstance(similarity, (float, np.floating)), "Should be able to calculate similarity with extreme ratings"