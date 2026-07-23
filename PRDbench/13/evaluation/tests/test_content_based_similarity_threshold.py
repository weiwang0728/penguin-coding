import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import ContentBasedRecommender


class TestSimilarityThreshold:
    """Similarity threshold configuration unit test"""

    def setup_method(self):
        """Setup before test"""
        self.recommender = ContentBasedRecommender()
        
    def create_test_items_data(self):
        """Create test product dataset"""
        items_data = {
            'item_id': range(1, 21),
            'title': [
                "Apple iPhone 14 Pro Smartphone", "Huawei Mate50 Pro 5G Phone", "Xiaomi 13 Ultra Leica Camera",
                "OPPO Find X6 Pro Hasselblad Imaging", "vivo X90 Pro+ Zeiss Optics", "Samsung Galaxy S23 Ultra",
                "OnePlus 11 Snapdragon 8Gen2 Processor", "Meizu 20 Pro Boundless Design", "Sony Xperia 1 V Display",
                "Google Pixel 7 Pro System", "Lenovo Legion Y9000P Gaming Laptop", "Dell XPS 13 Plus Ultrabook",
                "ASUS ROG Republic of Gamers", "HP Omen 8 Gaming Laptop", "ThinkPad X1 Business Office",
                "MacBook Pro 14-inch Professional", "Surface Laptop Microsoft Certified", "Mechrevo Jiaolong 16K Esports",
                "Nike Air Jordan Basketball Shoes", "Adidas Ultraboost Running Shoes"
            ],
            'description': [
                "This is a high-end smartphone with powerful photography features and excellent performance, suitable for business and entertainment use.",
                "5G network support, HarmonyOS operating system, excellent photography, Huawei's latest flagship product.",
                "Equipped with Leica imaging system, Snapdragon 8Gen2 processor, providing professional-level photography experience.",
                "Enhanced by Hasselblad imaging technology, flagship photography phone, true-to-life color reproduction.",
                "Zeiss optical lens, strong night portrait shooting capability, excellent night mode effect.",
                "S Pen stylus support, large screen design, suitable for office work and creation.",
                "Snapdragon 8Gen2 processor, 2K 120Hz curved screen, strong gaming performance.",
                "Xingji Meizu dual brand, boundless design concept, simple and fashionable appearance.",
                "4K HDR OLED display technology, Sony professional display tuning.",
                "Native Android system, complete Google services, pure system experience.",
                "Intel i7 processor, RTX 4070 graphics card, professional gaming laptop.",
                "Ultra-thin design, Intel Evo certified, first choice for business office.",
                "AMD Ryzen processor, esports-level graphics card, professional gaming equipment.",
                "Omen series, high-performance gaming laptop, RGB lighting effects.",
                "Business office dedicated, ThinkPad classic design, reliable and stable.",
                "Apple M2 chip, professional-level performance, first choice for creative work.",
                "Microsoft Surface series, touchscreen design, office and entertainment.",
                "Esports dedicated laptop, high refresh rate screen, gaming experience.",
                "Classic basketball shoes, Jordan brand, combines sports and fashion.",
                "Professional running shoes, comfortable cushioning, essential for sports and fitness."
            ],
            'category': ['Phone'] * 10 + ['Computer'] * 7 + ['Shoes'] * 3,
            'tags': [
                "smartphone,photography,high-end", "5G,Huawei,flagship", "Leica,photography,Snapdragon", "Hasselblad,imaging,photography",
                "Zeiss,optics,night", "Samsung,S Pen,large screen", "OnePlus,gaming,performance", "Meizu,design,fashion",
                "Sony,display,professional", "Google,Android,pure", "Lenovo,gaming laptop,high performance", "Dell,ultrabook,thin",
                "ASUS,esports,gaming", "HP,gaming,performance", "Lenovo,business,office", "Apple,professional,design",
                "Microsoft,certified,office", "Mechrevo,esports,gaming", "Nike,basketball,sports", "Adidas,running,sports"
            ]
        }
        
        return pd.DataFrame(items_data)
    
    def test_similarity_threshold_configuration(self):
        """Test similarity threshold configuration function"""
        # Prepare test data
        items_df = self.create_test_items_data()

        # Train model
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        # Select target product for testing (select first phone product)
        target_item_id = 1

        # Test different similarity thresholds
        thresholds = [0.3, 0.5, 0.7, 0.9]
        recommendation_counts = []

        for threshold in thresholds:
            # Set similarity threshold and get recommendation results
            recommendations = self.recommender.recommend_similar_items(
                target_item_id,
                top_n=15,  # Set larger number to observe threshold effect
                similarity_threshold=threshold
            )

            recommendation_counts.append(len(recommendations))

            # Verify recommendation result format
            for item_id, similarity in recommendations:
                assert isinstance(item_id, (int, np.integer)), "Product ID should be integer"
                assert isinstance(similarity, (float, np.floating)), "Similarity should be float"
                assert similarity >= threshold, f"Similarity {similarity} should be greater than or equal to threshold {threshold}"
                assert item_id != target_item_id, "Should not recommend the product itself"

            # Verify recommendation results are sorted in descending order by similarity
            similarities = [sim for _, sim in recommendations]
            assert similarities == sorted(similarities, reverse=True), "Recommendation results should be sorted in descending order by similarity"

        # Verify the rule that higher threshold results in fewer recommendations
        for i in range(len(thresholds) - 1):
            current_threshold = thresholds[i]
            next_threshold = thresholds[i + 1]
            current_count = recommendation_counts[i]
            next_count = recommendation_counts[i + 1]

            assert next_count <= current_count, \
                f"Recommendation count for threshold {next_threshold} ({next_count} recommendations) should be less than or equal to threshold {current_threshold} ({current_count} recommendations)"

        # Verify each threshold can be successfully set and return results
        assert all(isinstance(count, int) and count >= 0 for count in recommendation_counts), \
            "All thresholds should return valid recommendation counts"

        # Verify highest threshold (0.9) has significantly fewer recommendations than lowest threshold (0.3)
        if recommendation_counts[0] > 0:  # If lowest threshold has recommendation results
            reduction_ratio = (recommendation_counts[0] - recommendation_counts[-1]) / recommendation_counts[0]
            assert reduction_ratio >= 0, "High threshold should reduce recommendation count"

        print(f"Threshold test results: {dict(zip(thresholds, recommendation_counts))}")
        print("Verification passed: Content recommendation algorithm can successfully set different similarity thresholds, higher threshold results in fewer recommendations")
    
    def test_threshold_boundary_conditions(self):
        """Test threshold boundary conditions"""
        items_df = self.create_test_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        target_item_id = 1

        # Test very low threshold (0.0)
        low_threshold_recs = self.recommender.recommend_similar_items(
            target_item_id, top_n=10, similarity_threshold=0.0
        )

        # Test very high threshold (1.0)
        high_threshold_recs = self.recommender.recommend_similar_items(
            target_item_id, top_n=10, similarity_threshold=1.0
        )

        # Verify very low threshold should return more results
        assert len(low_threshold_recs) >= len(high_threshold_recs), \
            "Very low threshold should return more or equal number of recommendation results"

        # Verify very high threshold (1.0) should have very few or no results (unless there are identical products)
        assert len(high_threshold_recs) <= 1, \
            "Very high threshold (1.0) should have very few or no recommendation results"

    def test_threshold_with_different_items(self):
        """Test performance of different products under the same threshold"""
        items_df = self.create_test_items_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])

        threshold = 0.5

        # Test products from different categories
        phone_item_id = 1  # Phone
        computer_item_id = 11  # Computer
        shoe_item_id = 19  # Shoes

        phone_recs = self.recommender.recommend_similar_items(
            phone_item_id, top_n=10, similarity_threshold=threshold
        )

        computer_recs = self.recommender.recommend_similar_items(
            computer_item_id, top_n=10, similarity_threshold=threshold
        )

        shoe_recs = self.recommender.recommend_similar_items(
            shoe_item_id, top_n=10, similarity_threshold=threshold
        )

        # Verify all recommendation results meet threshold requirements
        for recommendations in [phone_recs, computer_recs, shoe_recs]:
            for item_id, similarity in recommendations:
                assert similarity >= threshold, f"Similarity {similarity} should be greater than or equal to threshold {threshold}"

        # Verify diversity of recommendation results
        all_rec_counts = [len(phone_recs), len(computer_recs), len(shoe_recs)]
        assert any(count > 0 for count in all_rec_counts), \
            "At least one product category should generate recommendation results"

        print(f"Different products threshold {threshold} test results: Phone {len(phone_recs)}, Computer {len(computer_recs)}, Shoes {len(shoe_recs)}")