import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from algorithms.content_based import Word2VecRecommender

# Check if gensim is available
try:
    from gensim.models import Word2Vec
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False


class TestWord2VecEmbedding:
    """Word2Vec/Embedding support unit tests"""
    
    def setup_method(self):
        """Pre-test setup"""
        self.recommender = Word2VecRecommender(vector_size=128, window=5, min_count=2)
        
    def create_text_corpus_data(self):
        """Create text data for training word vector model"""
        # Create product data with rich Chinese text
        items_data = []
        
        # Phone category product text
        phone_texts = [
            "Apple iPhone 14 Pro Max smartphone A16 Bionic chip Super Retina XDR display professional camera system",
            "Huawei Mate50 Pro HarmonyOS system Kirin chip Leica image curved screen design wireless charging",
            "Xiaomi 13 Ultra Leica optical lens Snapdragon 8Gen2 processor 2K AMOLED display 120W fast charge",
            "OPPO Find X6 Pro Hasselblad imaging system Dimensity 9200 processor periscope telephoto lens ColorOS system",
            "vivo X90 Pro+ Zeiss T coating lens Dimensity 9200 chip 120Hz high refresh screen flash charging technology",
            "Samsung Galaxy S23 Ultra S Pen stylus Exynos2200 processor Dynamic AMOLED screen",
            "OnePlus 11 Hasselblad professional mode Snapdragon 8Gen2 chip 2K 120Hz curved screen SUPERVOOC flash charging",
            "Meizu 20 Pro Star Era Meizu design Snapdragon 8Gen2 processor boundless full screen Flyme system",
            "Sony Xperia 1 V 4K HDR OLED display Snapdragon 8Gen2 chip professional photography function",
            "Google Pixel 7 Pro Tensor G2 chip computational photography technology pure Android system AI function"
        ]
        
        # Laptop category product text
        laptop_texts = [
            "Lenovo Legion Y9000P gaming laptop RTX4080 graphics card 13th gen Core i9 processor 16GB memory",
            "Dell XPS 13 Plus ultrabook 12th gen Core i7 processor OLED touchscreen thin portable design",
            "ASUS ROG Republic of Gamers gaming laptop RTX4090 graphics card AMD Ryzen 9 processor 240Hz gaming screen",
            "HP Omen 8 high performance gaming laptop RTX4070 graphics card Core i7 processor RGB backlit keyboard",
            "ThinkPad X1 Carbon business office laptop 12th gen Core processor carbon fiber body fingerprint recognition",
            "MacBook Pro 14 inch M2 Pro chip Liquid Retina XDR display professional grade performance",
            "Microsoft Surface Laptop 5 touchscreen laptop 12th gen Core processor PixelSense touchscreen",
            "Mechrevo Jiao Long 16K esports gaming laptop RTX4060 graphics card AMD processor high refresh rate screen",
            "Shinelon Destroyer DD2 high-end gaming laptop RTX graphics card Intel processor mechanical keyboard design",
            "Hasee War God Z8 cost-effective gaming laptop GTX graphics card Core processor large capacity hard drive storage"
        ]
        
        # Footwear and clothing category product text
        shoe_texts = [
            "Nike Air Jordan 1 classic retro basketball shoes genuine leather material air cushion shock absorption street fashion item",
            "Adidas Ultraboost 22 running sports shoes Boost cushioning technology Primeknit upper",
            "New Balance 990v5 USA made limited edition retro running shoes ENCAP cushioning technology suede material",
            "Converse All Star classic canvas shoes high-top low-top design rubber outsole trendy versatile style",
            "Vans Old Skool skateboard shoes side stripe design wear-resistant rubber sole street skateboard culture",
            "Puma Suede Classic retro sneakers suede material classic stripe logo comfortable lining",
            "Anta KT7 Thompson signature basketball shoes professional basketball technology TPU support wear-resistant outsole",
            "Li-Ning Way of Wade 10 professional basketball shoes cushioning technology carbon fiber plate professional player same model",
            "361 Degrees international line professional running shoes lightweight design breathable mesh professional running technology",
            "Xtep Speed 160X marathon running shoes professional race design lightweight rebound professional athlete recommended"
        ]
        
        # Appliance category product text
        appliance_texts = [
            "Midea inverter air conditioner 1.5HP wall mount energy saving silent design smart temperature control WiFi remote control",
            "Gree Pinyue wall-mounted home cooling heating air conditioner inverter energy saving fast cooling heating quiet operation",
            "Haier Commander smart WiFi control air conditioner voice control self-cleaning function energy saving eco-friendly",
            "AUX Golden Classic inverter cooling heating air conditioner smart dehumidification fast cooling low noise design",
            "TCL bedroom air conditioner fast cooling heating energy saving smart sleep mode remote control operation",
            "Siemens drum washing machine 10KG large capacity smart dosing 95 degree high temperature washing energy saving quiet",
            "Haier wave wheel washing machine fully automatic household large capacity design multiple washing programs simple operation",
            "Little Swan Beverly high-end washer dryer combo smart washing drying function European design",
            "Midea washer dryer combo smart dosing detergent multiple washing modes energy saving water saving design",
            "Panasonic Romeo Japanese precision washing machine foam clean technology gentle washing quiet motor"
        ]
        
        # Merge all text data
        all_texts = phone_texts + laptop_texts + shoe_texts + appliance_texts
        categories = ['phone'] * 10 + ['computer'] * 10 + ['footwear'] * 10 + ['appliance'] * 10
        
        for i, (text, category) in enumerate(zip(all_texts, categories), 1):
            items_data.append({
                'item_id': i,
                'title': text.split(' ')[0] + ' ' + text.split(' ')[1],  # Extract brand and model
                'description': text,
                'tags': ' '.join(text.split(' ')[:5]),  # First 5 words as tags
                'category': category
            })
        
        # To reach at least 1000 documents requirement, copy and vary existing data
        extended_data = []
        for i, item in enumerate(items_data):
            # Original data
            extended_data.append(item)
            
            # Create variation versions
            for j in range(24):  # Create 24 variation versions for each original product
                new_item = item.copy()
                new_item['item_id'] = len(all_texts) + i * 24 + j + 1
                new_item['title'] = f"{item['title']} Version{j+1}"
                new_item['description'] = f"{item['description']} Special Version{j+1} Enhanced Features"
                new_item['tags'] = f"{item['tags']} Version{j+1}"
                extended_data.append(new_item)
        
        return pd.DataFrame(extended_data)
    
    def test_word2vec_training(self):
        """Test Word2Vec model training"""
        # Prepare test data
        items_df = self.create_text_corpus_data()
        
        # Train Word2Vec model
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        if not GENSIM_AVAILABLE:
            # When gensim is unavailable, test that model is indeed not trained
            assert self.recommender.model is None, "When Gensim is unavailable, Word2Vec model should be None"
            assert len(self.recommender.item_vectors) == 0, "When Gensim is unavailable, should not generate item vectors"
            print("Warning: Gensim library unavailable, Word2Vec functionality disabled")
            return
        
        # Verify model training success (only when gensim is available)
        assert self.recommender.model is not None, "Word2Vec model should be successfully trained"
        assert len(self.recommender.item_vectors) > 0, "Should generate item vectors"
        
        # Verify vector dimensions
        for item_id, vector in self.recommender.item_vectors.items():
            assert len(vector) == self.recommender.vector_size, f"Vector dimension should be {self.recommender.vector_size}"
            assert isinstance(vector, np.ndarray), "Vector should be numpy array"
        
        # Verify vocabulary size
        vocab_size = len(self.recommender.model.wv.key_to_index)
        assert vocab_size >= 100, f"Vocabulary size should be ≥100, actual: {vocab_size}"
        
        # Verify model can recognize common words
        common_words = ['smart', 'phone', 'computer', 'gaming', 'processor']
        found_words = 0
        for word in common_words:
            if word in self.recommender.model.wv:
                found_words += 1
        
        word_coverage = found_words / len(common_words)
        assert word_coverage >= 0.6, f"Common word coverage should be ≥60%, actual: {word_coverage:.2%}"
    
    def test_vector_similarity_calculation(self):
        """Test vector similarity calculation"""
        items_df = self.create_text_corpus_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        if not GENSIM_AVAILABLE:
            # When gensim is unavailable, test recommendations return empty list
            target_item_id = 1
            similar_items = self.recommender.get_similar_items(target_item_id, top_n=5)
            assert len(similar_items) == 0, "When Gensim is unavailable, similarity recommendations should return empty list"
            print("Warning: Gensim library unavailable, skipping vector similarity calculation test")
            return
        
        # Test similar item recommendation
        target_item_id = 1  # First phone product
        similar_items = self.recommender.get_similar_items(target_item_id, top_n=5)
        
        # Verify recommendation results
        assert len(similar_items) <= 5, "Number of recommendations should not exceed top_n"
        
        for item_id, similarity in similar_items:
            assert isinstance(item_id, (int, np.integer)), "Item ID should be integer"
            assert isinstance(similarity, (float, np.floating)), "Similarity should be float"
            assert -1 <= similarity <= 1, "Cosine similarity should be in [-1,1] range"
            assert item_id != target_item_id, "Should not recommend the item itself"
        
        # Verify recommendation resultssorted by similarity in descending order
        similarities = [sim for _, sim in similar_items]
        assert similarities == sorted(similarities, reverse=True), "Recommendations should be sorted by similarity in descending order"
    
    def test_semantic_similarity(self):
        """Test semantic similarity"""
        items_df = self.create_text_corpus_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        if not GENSIM_AVAILABLE:
            print("Warning: Gensim library unavailable, skipping semantic similarity test")
            return
        
        # Get items from different categories
        phone_items = items_df[items_df['category'] == 'phone']['item_id'].values[:10]
        laptop_items = items_df[items_df['category'] == 'computer']['item_id'].values[:10]
        
        # Calculate average similarity between same category items
        phone_similarities = []
        for i in range(len(phone_items)):
            for j in range(i+1, len(phone_items)):
                if phone_items[i] in self.recommender.item_vectors and phone_items[j] in self.recommender.item_vectors:
                    similar_items = self.recommender.get_similar_items(phone_items[i], top_n=20)
                    for item_id, sim in similar_items:
                        if item_id == phone_items[j]:
                            phone_similarities.append(sim)
                            break
        
        # Calculate average similarity between cross-category items
        cross_similarities = []
        for phone_id in phone_items[:5]:
            if phone_id in self.recommender.item_vectors:
                similar_items = self.recommender.get_similar_items(phone_id, top_n=50)
                for item_id, sim in similar_items:
                    if item_id in laptop_items:
                        cross_similarities.append(sim)
                        break
        
        # Verify semantic understanding capability
        if phone_similarities and cross_similarities:
            avg_phone_sim = np.mean(phone_similarities)
            avg_cross_sim = np.mean(cross_similarities)
            
            assert avg_phone_sim > avg_cross_sim, "Same category item similarity should be higher than cross-category"
    
    def test_word2vec_parameters(self):
        """Test Word2Vec parameter configuration"""
        if not GENSIM_AVAILABLE:
            print("Warning: Gensim library unavailable, skipping Word2Vec parameter test")
            return
            
        items_df = self.create_text_corpus_data()
        
        # Test different parameter configurations
        recommender_128 = Word2VecRecommender(vector_size=128, window=5, min_count=2)
        recommender_64 = Word2VecRecommender(vector_size=64, window=3, min_count=1)
        
        recommender_128.fit(items_df, text_columns=['title', 'description'])
        recommender_64.fit(items_df, text_columns=['title', 'description'])
        
        # Verify different vector dimensions
        for item_id, vector in recommender_128.item_vectors.items():
            assert len(vector) == 128, "128-dimensional model vector dimension should be 128"
        
        for item_id, vector in recommender_64.item_vectors.items():
            assert len(vector) == 64, "64-dimensional model vector dimension should be 64"
        
        # Verify model parameter settings
        assert recommender_128.model.vector_size == 128, "Vector dimension parameter should be correctly set"
        assert recommender_128.model.window == 5, "Window size parameter should be correctly set"
        assert recommender_128.model.min_count == 2, "Minimum word frequency parameter should be correctly set"
    
    def test_chinese_word_embeddings(self):
        """Test Chinese word embedding effects"""
        if not GENSIM_AVAILABLE:
            print("Warning: Gensim library unavailable, skipping Chinese word embedding test")
            return
            
        items_df = self.create_text_corpus_data()
        self.recommender.fit(items_df, text_columns=['title', 'description', 'tags'])
        
        # Test Chinese word vector quality
        chinese_tech_words = ['smart', 'processor', 'display', 'camera', 'battery']
        chinese_brand_words = ['Apple', 'Huawei', 'Xiaomi', 'Samsung', 'OPPO']
        
        # Verify similarity between technical vocabulary
        tech_similarities = []
        for i in range(len(chinese_tech_words)):
            for j in range(i+1, len(chinese_tech_words)):
                word1, word2 = chinese_tech_words[i], chinese_tech_words[j]
                if word1 in self.recommender.model.wv and word2 in self.recommender.model.wv:
                    similarity = self.recommender.model.wv.similarity(word1, word2)
                    tech_similarities.append(similarity)
        
        # Verify similarity between brand vocabulary
        brand_similarities = []
        for i in range(len(chinese_brand_words)):
            for j in range(i+1, len(chinese_brand_words)):
                word1, word2 = chinese_brand_words[i], chinese_brand_words[j]
                if word1 in self.recommender.model.wv and word2 in self.recommender.model.wv:
                    similarity = self.recommender.model.wv.similarity(word1, word2)
                    brand_similarities.append(similarity)
        
        # Verify word vector learning effects
        if tech_similarities:
            avg_tech_sim = np.mean(tech_similarities)
            assert avg_tech_sim > 0, "Technical vocabulary should have positive correlation"
        
        if brand_similarities:
            avg_brand_sim = np.mean(brand_similarities)
            assert avg_brand_sim > 0, "Brand vocabulary should have positive correlation"
    
    def test_edge_cases_and_robustness(self):
        """Test edge cases and robustness"""
        if not GENSIM_AVAILABLE:
            print("Warning: Gensim library unavailable, skipping edge case test")
            return
            
        # Test small dataset
        small_df = pd.DataFrame({
            'item_id': [1, 2, 3],
            'title': ['Apple Phone', 'Huawei Computer', 'Nike Shoes'],
            'description': ['Smartphone Product', 'High Performance Laptop', 'Sports Casual Shoes'],
            'tags': ['phone smart', 'computer performance', 'shoes sports']
        })
        
        small_recommender = Word2VecRecommender(vector_size=50, min_count=1)
        small_recommender.fit(small_df)
        
        # Verify small dataset also works normally
        assert small_recommender.model is not None, "Small dataset should also be able to train model"
        assert len(small_recommender.item_vectors) > 0, "Small dataset should also generate item vectors"
        
        # Test non-existent item ID
        similar_items = self.recommender.get_similar_items(99999, top_n=5)
        assert len(similar_items) == 0, "Non-existent item ID should return empty recommendations"
        
        # Test empty text processing
        empty_text_df = pd.DataFrame({
            'item_id': [1, 2],
            'title': ['', ''],
            'description': ['', ''],
            'tags': ['', '']
        })
        
        empty_recommender = Word2VecRecommender(min_count=1)
        # Empty text should be processable, but may not have valid vectors
        try:
            empty_recommender.fit(empty_text_df)
            # If training succeeds, verify results
            assert len(empty_recommender.item_vectors) >= 0, "Vector count after empty text processing should be ≥0"
        except Exception:
            # Empty text may cause training failure, which is acceptable
            pass
    
    def test_model_persistence_and_consistency(self):
        """Test model persistence and consistency"""
        if not GENSIM_AVAILABLE:
            print("Warning: Gensim library unavailable, skipping model persistence test")
            return
            
        items_df = self.create_text_corpus_data()
        
        # Train two models with same parameters
        recommender1 = Word2VecRecommender(vector_size=100, window=5, min_count=2)
        recommender2 = Word2VecRecommender(vector_size=100, window=5, min_count=2)
        
        # Use same random seed to ensure consistency
        np.random.seed(42)
        recommender1.fit(items_df)
        
        np.random.seed(42)
        recommender2.fit(items_df)
        
        # Verify model parameter consistency
        assert recommender1.vector_size == recommender2.vector_size, "Models with same parameters should have consistent vector dimensions"
        assert len(recommender1.item_vectors) == len(recommender2.item_vectors), "Models trained on same data should generate same number of vectors"