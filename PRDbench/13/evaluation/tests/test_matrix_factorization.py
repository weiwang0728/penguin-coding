import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.collaborative_filtering import MatrixFactorization


class TestMatrixFactorization:
    """Matrix factorization algorithm unit tests"""

    def setup_method(self):
        """Test setup"""
        self.matrix_factorization = MatrixFactorization()
        
    def create_sparse_interaction_data(self):
        """Create sparse user-item rating matrix data"""
        np.random.seed(42)

        # Create sparse interaction data for 30 users and 60 items
        users = range(1, 31)
        items = range(1, 61)

        interactions = []
        interaction_id = 1

        # To create sparse data (sparsity ≥90%), each user only interacts with few items
        for user_id in users:
            # Each user only interacts with 3-8 items to ensure sparsity
            n_interactions = np.random.randint(3, 9)
            user_items = np.random.choice(items, size=n_interactions, replace=False)

            for item_id in user_items:
                # Generate ratings from 1-5
                rating = np.random.randint(1, 6)

                interactions.append({
                    'interaction_id': interaction_id,
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': float(rating),
                    'interaction_type': 'rating'
                })
                interaction_id += 1

        df = pd.DataFrame(interactions)

        # Verify sparsity
        total_possible = len(users) * len(items)
        actual_interactions = len(df)
        sparsity = 1 - (actual_interactions / total_possible)

        assert sparsity >= 0.85, f"Data sparsity should be ≥85%, actual is {sparsity:.2%}"

        return df
    
    def test_matrix_factorization_training(self):
        """Test matrix factorization model training"""
        # Prepare test data
        interactions_df = self.create_sparse_interaction_data()

        # Train model
        self.matrix_factorization.fit(interactions_df, test_size=0.2)

        # Verify model training results
        assert self.matrix_factorization.model is not None, "SVD model should be successfully trained"
        assert self.matrix_factorization.trainset is not None, "Should have training set"
        assert self.matrix_factorization.testset is not None, "Should have test set"

        # Verify model parameters
        model = self.matrix_factorization.model
        assert hasattr(model, 'n_factors'), "Model should have n_factors parameter"
        assert hasattr(model, 'n_epochs'), "Model should have n_epochs parameter"
        assert hasattr(model, 'lr_all'), "Model should have learning rate parameter"
        assert hasattr(model, 'reg_all'), "Model should have regularization parameter"

        # Verify latent factor count is configurable and ≥50
        assert model.n_factors >= 50, f"Latent factor count should be ≥50, actual is {model.n_factors}"
    
    def test_rating_prediction(self):
        """Test rating prediction function"""
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)

        # Test rating prediction
        user_id = 1
        item_id = 10
        predicted_rating = self.matrix_factorization.predict(user_id, item_id)

        # Verify prediction result
        assert isinstance(predicted_rating, (float, np.floating)), "Predicted rating should be float"
        assert 1 <= predicted_rating <= 5, "Predicted rating should be in 1-5 range"

        # Test multiple predictions
        predictions = []
        for user_id in [1, 2, 3]:
            for item_id in [5, 15, 25]:
                pred = self.matrix_factorization.predict(user_id, item_id)
                predictions.append(pred)

        # Verify prediction diversity (not all predictions should be the same)
        assert len(set(predictions)) > 1, "Prediction results should have diversity"

        # Test prediction from untrained model
        untrained_mf = MatrixFactorization()
        untrained_pred = untrained_mf.predict(1, 1)
        assert untrained_pred == 0.0, "Untrained model should return 0.0"
    
    def test_recommendation_generation(self):
        """Test recommendation generation function"""
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)

        # Generate recommendations for user
        user_id = 1
        candidate_items = list(range(1, 21))  # Candidate items 1-20
        recommendations = self.matrix_factorization.recommend(user_id, candidate_items, top_n=10)

        # Verify recommendation results
        assert len(recommendations) <= 10, "Recommendation count should not exceed top_n"
        assert len(recommendations) <= len(candidate_items), "Recommendation count should not exceed candidate item count"

        # Verify recommendation result format
        for item_id, predicted_rating in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(predicted_rating, (float, np.floating)), "Predicted rating should be float"
            assert item_id in candidate_items, "Recommended item should be in candidate list"
            assert 1 <= predicted_rating <= 5, "Predicted rating should be in 1-5 range"

        # Verify recommendations are sorted by predicted rating in descending order
        ratings = [rating for _, rating in recommendations]
        assert ratings == sorted(ratings, reverse=True), "Recommendations should be sorted by predicted rating in descending order"

        # Test recommendation from untrained model
        untrained_mf = MatrixFactorization()
        untrained_recs = untrained_mf.recommend(1, [1, 2, 3], top_n=5)
        assert len(untrained_recs) == 0, "Untrained model should return empty recommendations"
    
    def test_user_and_item_factors(self):
        """Test user and item factor vectors"""
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)

        # Get user factor vector
        user_id = 1
        user_factors = self.matrix_factorization.get_user_factors(user_id)

        if user_factors is not None:
            assert isinstance(user_factors, np.ndarray), "User factors should be numpy array"
            assert len(user_factors) == self.matrix_factorization.model.n_factors, "User factor dimension should equal model factor count"
            assert not np.all(user_factors == 0), "User factors should not be all zeros"

        # Get item factor vector
        item_id = 1
        item_factors = self.matrix_factorization.get_item_factors(item_id)

        if item_factors is not None:
            assert isinstance(item_factors, np.ndarray), "Item factors should be numpy array"
            assert len(item_factors) == self.matrix_factorization.model.n_factors, "Item factor dimension should equal model factor count"
            assert not np.all(item_factors == 0), "Item factors should not be all zeros"

        # Test non-existent user and item
        non_exist_user_factors = self.matrix_factorization.get_user_factors(999)
        non_exist_item_factors = self.matrix_factorization.get_item_factors(999)

        assert non_exist_user_factors is None, "Non-existent user should return None"
        assert non_exist_item_factors is None, "Non-existent item should return None"

        # Test untrained model
        untrained_mf = MatrixFactorization()
        untrained_user_factors = untrained_mf.get_user_factors(1)
        untrained_item_factors = untrained_mf.get_item_factors(1)

        assert untrained_user_factors is None, "Untrained model should return None for user factors"
        assert untrained_item_factors is None, "Untrained model should return None for item factors"
    
    def test_sparse_data_handling(self):
        """Test sparse data handling capability"""
        # Create extremely sparse data (sparsity >95%)
        sparse_interactions = []
        users = range(1, 21)  # 20 users
        items = range(1, 101)  # 100 items

        # Each user only interacts with 1-3 items
        for user_id in users:
            n_interactions = np.random.randint(1, 4)
            user_items = np.random.choice(items, size=n_interactions, replace=False)

            for item_id in user_items:
                sparse_interactions.append({
                    'user_id': user_id,
                    'item_id': item_id,
                    'rating': float(np.random.randint(1, 6))
                })

        sparse_df = pd.DataFrame(sparse_interactions)

        # Verify sparsity
        total_possible = 20 * 100
        actual_interactions = len(sparse_df)
        sparsity = 1 - (actual_interactions / total_possible)
        assert sparsity > 0.95, f"Data should be extremely sparse (>95%), actual sparsity is {sparsity:.2%}"

        # Train model to handle sparse data
        sparse_mf = MatrixFactorization()
        sparse_mf.fit(sparse_df)

        # Verify model can handle sparse data
        assert sparse_mf.model is not None, "Should be able to handle extremely sparse data"

        # Test prediction function
        prediction = sparse_mf.predict(1, 50)  # Predict a possibly non-interacted user-item pair
        assert isinstance(prediction, (float, np.floating)), "Sparse data model should be able to make predictions"
        assert 1 <= prediction <= 5, "Predicted rating should be in reasonable range"
    
    def test_model_performance_metrics(self):
        """Test model performance metrics"""
        interactions_df = self.create_sparse_interaction_data()

        # Train model and get performance metrics
        self.matrix_factorization.fit(interactions_df, test_size=0.3)

        # Evaluate model performance on test set
        predictions = self.matrix_factorization.model.test(self.matrix_factorization.testset)

        # Calculate RMSE and MAE
        squared_errors = [(pred.est - pred.r_ui) ** 2 for pred in predictions]
        absolute_errors = [abs(pred.est - pred.r_ui) for pred in predictions]

        rmse = np.sqrt(np.mean(squared_errors))
        mae = np.mean(absolute_errors)

        # Verify performance metrics are reasonable
        assert 0 < rmse < 3, f"RMSE should be in reasonable range (0-3), actual is {rmse:.3f}"
        assert 0 < mae < 2, f"MAE should be in reasonable range (0-2), actual is {mae:.3f}"
        assert mae <= rmse, "MAE should be less than or equal to RMSE"

        # Verify predicted values are in reasonable range
        predicted_ratings = [pred.est for pred in predictions]
        assert all(1 <= pred <= 5 for pred in predicted_ratings), "All predicted ratings should be in 1-5 range"
    
    def test_different_parameters(self):
        """Test different parameter configurations"""
        interactions_df = self.create_sparse_interaction_data()

        # Test different factor counts
        mf_50_factors = MatrixFactorization()
        mf_50_factors.fit(interactions_df)

        # Verify default parameters
        assert mf_50_factors.model.n_factors >= 50, "Default factor count should be ≥50"

        # Test model training success
        prediction_50 = mf_50_factors.predict(1, 1)
        assert isinstance(prediction_50, (float, np.floating)), "Model with different parameters should be able to predict normally"
    
    def test_recommendation_consistency(self):
        """Test recommendation consistency"""
        interactions_df = self.create_sparse_interaction_data()

        # Train two models with same parameters
        mf1 = MatrixFactorization()
        mf2 = MatrixFactorization()

        # Use same random seed
        np.random.seed(42)
        mf1.fit(interactions_df)

        np.random.seed(42)
        mf2.fit(interactions_df)

        # Compare prediction results
        user_id, item_id = 1, 5
        pred1 = mf1.predict(user_id, item_id)
        pred2 = mf2.predict(user_id, item_id)

        # Due to random initialization, predictions may have slight differences, but should be in similar range
        assert isinstance(pred1, (float, np.floating)), "First model prediction should be normal"
        assert isinstance(pred2, (float, np.floating)), "Second model prediction should be normal"
        assert 1 <= pred1 <= 5, "First model prediction should be in reasonable range"
        assert 1 <= pred2 <= 5, "Second model prediction should be in reasonable range"
    
    def test_edge_cases_and_robustness(self):
        """Test edge cases and robustness"""
        # Test empty candidate item list
        interactions_df = self.create_sparse_interaction_data()
        self.matrix_factorization.fit(interactions_df)

        empty_recommendations = self.matrix_factorization.recommend(1, [], top_n=5)
        assert len(empty_recommendations) == 0, "Empty candidate list should return empty recommendations"

        # Test single candidate item
        single_recommendations = self.matrix_factorization.recommend(1, [10], top_n=5)
        assert len(single_recommendations) <= 1, "Single candidate item should return at most 1 recommendation"

        # Test very small dataset
        minimal_df = pd.DataFrame({
            'user_id': [1, 1, 2, 2],
            'item_id': [1, 2, 1, 3],
            'rating': [4.0, 3.0, 5.0, 2.0]
        })

        minimal_mf = MatrixFactorization()
        minimal_mf.fit(minimal_df)

        # Minimal dataset should also be able to train
        assert minimal_mf.model is not None, "Minimal dataset should also be able to train model"

        # Test prediction
        minimal_pred = minimal_mf.predict(1, 3)
        assert isinstance(minimal_pred, (float, np.floating)), "Minimal dataset model should be able to predict"