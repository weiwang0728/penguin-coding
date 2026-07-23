import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import ContentBasedRecommender


class TestTFIDFImplementation:
    """TF-IDF implementation unit tests"""

    def setup_method(self):
        """Pre-test setup"""
        self.recommender = ContentBasedRecommender()
        
    def create_items_data(self):
        """Create product text description dataset"""
        items_data = {
            'item_id': range(1, 101),
            'title': [
                "Apple iPhone 14 Pro Smartphone", "Huawei Mate50 Pro 5G Phone", "Xiaomi 13 Ultra Leica Camera",
                "OPPO Find X6 Pro Hasselblad Image", "vivo X90 Pro+ Zeiss Optics", "Samsung Galaxy S23 Ultra",
                "OnePlus 11 Snapdragon 8Gen2 Processor", "Meizu 20 Pro Boundless Design", "Sony Xperia 1 V Display",
                "Google Pixel 7 Pro System", "Lenovo Legion Y9000P Gaming Laptop", "Dell XPS 13 Plus Ultrabook",
                "ASUS ROG Republic of Gamers", "HP Omen 8 Gaming Laptop", "ThinkPad X1 Business Office",
                "MacBook Pro 14-inch Professional", "Surface Laptop Microsoft Certified", "Mechrevo Jiao Long 16K Esports",
                "Shinelon Destroyer DD2 Gaming", "Hasee War God Z8 Cost-effective", "Nike Air Jordan Basketball Shoes",
                "Adidas Ultraboost Running Shoes", "New Balance 990v5 Retro Sneakers", "Converse All Star Canvas Shoes",
                "Vans Old Skool Skateboard Shoes", "Puma Suede Classic Sneakers", "Anta KT7 Thompson Basketball",
                "Li-Ning Way of Wade 10 Basketball Shoes", "361 Degrees Professional Running Shoes", "Xtep Speed 160X Marathon",
                "Midea Inverter Air Conditioner Energy Saving Silent", "Gree Pinyue Wall-mounted Air Conditioner", "Haier Smart Air Conditioner",
                "AUX Golden Classic Inverter Air Conditioner", "TCL Bedroom Air Conditioner Cooling", "Hisense Comfort Home Inverter Air Conditioner",
                "Changhong Joy Energy Saving Air Conditioner", "Chigo Cloud Air Conditioner Remote Control", "Kelon Elegant Silent Air Conditioner",
                "Chunlan Classic Mechanical Air Conditioner", "Siemens Drum Washing Machine", "Haier Wave Wheel Washing Machine",
                "Little Swan Beverly Laundry", "Midea Washer-Dryer All-in-one", "Panasonic Romeo Washing Machine",
                "LG Steam Washing Machine Sterilization", "Bosch European Import Washing Machine", "Whirlpool American Washing Machine",
                "Sanyo Wave Wheel Washing Machine", "Leader Haier Washing Machine"
            ] + [f"Product{i} Smart Device" for i in range(51, 101)],
            'description': [
                "This is a high-end smartphone with powerful photography features and excellent performance, suitable for business and entertainment use.",
                "5G network support, HarmonyOS operating system, excellent photography, Huawei's latest flagship product.",
                "Equipped with Leica imaging system, Snapdragon 8Gen2 processor, provides professional-grade photography experience.",
                "Hasselblad imaging technology, flagship photography phone, true-to-life color reproduction.",
                "Zeiss optical lens, strong night portrait shooting capability, outstanding night mode effects.",
                "S Pen stylus support, large screen design, suitable for office work and creation.",
                "Snapdragon 8Gen2 processor, 2K 120Hz curved screen, powerful gaming performance.",
                "Star Era Meizu dual brand, boundless design concept, simple and fashionable appearance.",
                "4K HDR OLED display technology, Sony professional display tuning.",
                "Native Android system, complete Google services, pure system experience."
            ] + [f"This is a detailed description of product{i}, including various functional features and usage scenarios." for i in range(11, 101)],
            'category': ['phone'] * 10 + ['computer'] * 10 + ['clothing'] * 10 + ['appliance'] * 20 + ['other'] * 50,
            'tags': [
                "smartphone,photography,high-end", "5G,Huawei,flagship", "Leica,photography,Snapdragon", "Hasselblad,imaging,photography",
                "Zeiss,optics,night", "Samsung,S Pen,large screen", "OnePlus,gaming,performance", "Meizu,design,fashion",
                "Sony,display,professional", "Google,Android,pure", "Lenovo,gaming laptop,high performance", "Dell,ultrabook,thin and light",
                "ASUS,esports,gaming", "HP,gaming,performance", "Lenovo,business,office", "Apple,professional,design",
                "Microsoft,certified,office", "Mechrevo,esports,gaming", "Shinelon,gaming,high-end", "Hasee,cost-effective,gaming",
                "Nike,basketball,sports", "Adidas,running,sports", "New Balance,retro,running", "Converse,canvas,trendy",
                "Vans,skateboard,street", "Puma,retro,classic", "Anta,basketball,professional", "Li-Ning,basketball,professional",
                "361 Degrees,running,professional", "Xtep,marathon,running", "Midea,air conditioner,energy saving", "Gree,air conditioner,home use",
                "Haier,smart,air conditioner", "AUX,inverter,air conditioner", "TCL,cooling,air conditioner", "Hisense,inverter,smart",
                "Changhong,energy saving,eco-friendly", "Chigo,remote,smart", "Kelon,silent,comfortable", "Chunlan,classic,traditional",
                "Siemens,washing machine,drum", "Haier,washing machine,wave wheel", "Little Swan,laundry,high-end", "Midea,washer-dryer,smart",
                "Panasonic,Japanese,precision", "LG,steam,sterilization", "Bosch,imported,quality", "Whirlpool,American,large capacity",
                "Sanyo,wave wheel,practical", "Leader,cost-effective,practical"
            ] + [f"tag{i},function{i},feature{i}" for i in range(51, 101)]
        }
        
        return pd.DataFrame(items_data)
    
    def test_tfidf_implementation(self):
        """Test TF-IDF feature extraction implementation"""
        # Prepare test data
        items_df = self.create_items_data()

        # Train model
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        # Verify TF-IDF feature matrix generation
        assert self.recommender.item_features is not None, "Should generate TF-IDF feature matrix"
        assert self.recommender.tfidf_vectorizer is not None, "Should create TF-IDF vectorizer"

        # Verify feature matrix dimensions
        n_items = len(items_df)
        feature_matrix = self.recommender.item_features
        assert feature_matrix.shape[0] == n_items, f"Feature matrix rows should equal number of items {n_items}"

        # Verify feature matrix is not all zeros
        assert feature_matrix.sum() > 0, "Feature matrix should not be all zeros"

        # Verify similarity matrix generation
        assert self.recommender.item_similarity_matrix is not None, "Should generate item similarity matrix"
        assert self.recommender.item_similarity_matrix.shape == (n_items, n_items), "Similarity matrix dimensions should be correct"

        # Verify symmetry of similarity matrix
        similarity_matrix = self.recommender.item_similarity_matrix
        assert np.allclose(similarity_matrix, similarity_matrix.T), "Similarity matrix should be symmetric"

        # Verify diagonal is 1 (similarity with self)
        diagonal = np.diag(similarity_matrix)
        assert np.allclose(diagonal, 1.0), "Similarity matrix diagonal should be all 1s"
    
    def test_similarity_calculation(self):
        """Test similarity calculation accuracy"""
        items_df = self.create_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        # Test similarity of same category items
        phone_items = items_df[items_df['category'] == 'phone']['item_id'].values[:5]
        computer_items = items_df[items_df['category'] == 'computer']['item_id'].values[:5]

        # Calculate intra-phone category similarity
        phone_similarities = []
        for i in range(len(phone_items)):
            for j in range(i+1, len(phone_items)):
                sim = self.recommender.get_item_similarity(phone_items[i], phone_items[j])
                phone_similarities.append(sim)

        # Calculate phone-computer cross-category similarity
        cross_similarities = []
        for phone_id in phone_items:
            for computer_id in computer_items:
                sim = self.recommender.get_item_similarity(phone_id, computer_id)
                cross_similarities.append(sim)

        # Verify same category items have higher similarity
        avg_phone_sim = np.mean(phone_similarities)
        avg_cross_sim = np.mean(cross_similarities)

        assert avg_phone_sim > avg_cross_sim, "Same category items should have higher similarity than cross-category"
        assert avg_phone_sim > 0.1, "Same category items should have reasonable similarity values"
    
    def test_recommend_similar_items(self):
        """Test similar item recommendation function"""
        items_df = self.create_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        # Test similar item recommendation
        target_item_id = 1  # Apple iPhone
        similar_items = self.recommender.recommend_similar_items(target_item_id, top_n=5)

        # Verify recommendation results
        assert len(similar_items) <= 5, "Number of recommendations should not exceed top_n"
        assert len(similar_items) > 0, "Should have similar item recommendations"

        # Verify recommendation result format
        for item_id, similarity in similar_items:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(similarity, (float, np.floating)), "Similarity should be float"
            assert 0 <= similarity <= 1, "Similarity should be in [0,1] range"
            assert item_id != target_item_id, "Should not recommend the item itself"

        # Verify recommendations are sorted by similarity in descending order
        similarities = [sim for _, sim in similar_items]
        assert similarities == sorted(similarities, reverse=True), "Recommendations should be sorted by similarity in descending order"
    
    def test_user_profile_recommendation(self):
        """Test user profile-based recommendation"""
        items_df = self.create_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        # Create user preference profile
        user_preferences = {
            'interests': 'smartphone photography camera',
            'brand_preference': 'Apple Huawei',
            'category': 'phone digital'
        }

        # Get user profile-based recommendations
        recommendations = self.recommender.recommend_for_user_profile(
            user_preferences, items_df, top_n=10
        )

        # Verify recommendation results
        assert len(recommendations) <= 10, "Number of recommendations should not exceed top_n"
        assert len(recommendations) > 0, "Should have recommendation results"

        # Verify recommendation result format
        for item_id, score in recommendations:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(score, (float, np.floating)), "Recommendation score should be float"
            assert score >= 0, "Recommendation score should be non-negative"

        # Verify recommendations are sorted by score in descending order
        scores = [score for _, score in recommendations]
        assert scores == sorted(scores, reverse=True), "Recommendations should be sorted by score in descending order"

        # Verify recommended items are relevant to user preferences
        recommended_items = items_df[items_df['item_id'].isin([item_id for item_id, _ in recommendations])]
        phone_count = len(recommended_items[recommended_items['category'] == 'phone'])
        phone_ratio = phone_count / len(recommended_items) if len(recommended_items) > 0 else 0

        assert phone_ratio >= 0.3, "Phone category items should have a high ratio (≥30%) in recommendations"
    
    def test_tfidf_parameters(self):
        """Test TF-IDF parameter configuration"""
        items_df = self.create_items_data()

        # Test different parameter configurations
        recommender = ContentBasedRecommender()
        recommender.fit(items_df, text_columns=['title', 'description'])

        # Verify TF-IDF vectorizer parameters
        vectorizer = recommender.tfidf_vectorizer
        assert hasattr(vectorizer, 'max_features'), "Should configure max_features parameter"
        assert hasattr(vectorizer, 'min_df'), "Should configure min_df parameter"
        assert hasattr(vectorizer, 'max_df'), "Should configure max_df parameter"
        assert vectorizer.ngram_range == (1, 2), "Should use 1-2 gram"

        # Verify vocabulary size is reasonable
        feature_names = vectorizer.get_feature_names_out()
        assert len(feature_names) > 10, "Vocabulary should contain sufficient features"
        assert len(feature_names) < 10000, "Vocabulary size should be within reasonable range"
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Test empty data
        empty_df = pd.DataFrame(columns=['item_id', 'title', 'description'])

        with pytest.raises(Exception):
            self.recommender.fit(empty_df)

        # Test single item
        single_item_df = pd.DataFrame({
            'item_id': [1],
            'title': ['Test Product'],
            'description': ['This is a test product'],
            'tags': ['test,product']
        })

        self.recommender.fit(single_item_df)
        similar_items = self.recommender.recommend_similar_items(1, top_n=5)
        assert len(similar_items) == 0, "Single item should have no similar item recommendations"

        # Test non-existent item ID
        items_df = self.create_items_data()
        self.recommender.fit(items_df)

        similarity = self.recommender.get_item_similarity(999, 1000)
        assert similarity == 0.0, "Non-existent item ID similarity should be 0"

        similar_items = self.recommender.recommend_similar_items(999)
        assert len(similar_items) == 0, "Non-existent item ID should have no recommendation results"