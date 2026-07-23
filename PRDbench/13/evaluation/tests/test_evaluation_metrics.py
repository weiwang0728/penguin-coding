import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.evaluation.metrics import EvaluationMetrics


class TestEvaluationMetrics:
    """Recommendation system evaluation metrics unit test"""

    def setup_method(self):
        """Setup before test"""
        self.metrics = EvaluationMetrics()

    def create_test_data(self):
        """Create test data"""
        # Create user recommendations and ground truth data
        user_recommendations = {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],  # Recommended product list
            2: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            3: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            4: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19],
            5: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        }

        user_ground_truth = {
            1: [1, 2, 11, 12, 21],  # Products user actually likes
            2: [5, 6, 15, 16, 25],
            3: [10, 11, 20, 21, 30],
            4: [1, 7, 13, 19, 31],
            5: [2, 8, 14, 20, 32]
        }

        # Create product feature data
        items_df = pd.DataFrame({
            'item_id': range(1, 33),
            'category': ['Electronics', 'Clothing', 'Books', 'Appliances', 'Food'] * 6 + ['Electronics', 'Clothing'],
            'brand': ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E'] * 6 + ['Brand A', 'Brand B'],
            'price': np.random.uniform(100, 1000, 32)
        })

        return user_recommendations, user_ground_truth, items_df
    
    def test_precision_at_k(self):
        """Test Precision@K metric"""
        # Test basic functionality
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]

        # Test Precision@5
        # predicted[:5] = [1, 2, 6, 7, 8], where [1, 2] are in actual
        precision_5 = self.metrics.precision_at_k(actual, predicted, 5)
        expected_precision_5 = 2 / 5  # 2 correct in first 5 predictions (not 3)
        assert abs(precision_5 - expected_precision_5) < 0.001, f"Precision@5 should be {expected_precision_5}, actual is {precision_5}"

        # Test Precision@10
        precision_10 = self.metrics.precision_at_k(actual, predicted, 10)
        expected_precision_10 = 4 / 9  # 4 correct in first 9 predictions (predicted only has 9)
        assert abs(precision_10 - expected_precision_10) < 0.001, f"Precision@10 should be {expected_precision_10}, actual is {precision_10}"

        # Test boundary conditions
        assert self.metrics.precision_at_k([], predicted, 5) == 0.0, "Empty actual list should return 0"
        assert self.metrics.precision_at_k(actual, [], 5) == 0.0, "Empty predicted list should return 0"
        assert self.metrics.precision_at_k(actual, predicted, 0) == 0.0, "K=0 should return 0"

    def test_recall_at_k(self):
        """Test Recall@K metric"""
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]

        # Test Recall@5
        # predicted[:5] = [1, 2, 6, 7, 8], where [1, 2] are in actual, actual has 5 total
        recall_5 = self.metrics.recall_at_k(actual, predicted, 5)
        expected_recall_5 = 2 / 5  # 2 of 5 actual products recommended in first 5 positions (not 3)
        assert abs(recall_5 - expected_recall_5) < 0.001, f"Recall@5 should be {expected_recall_5}, actual is {recall_5}"

        # Test Recall@10
        recall_10 = self.metrics.recall_at_k(actual, predicted, 10)
        expected_recall_10 = 4 / 5  # 4 of 5 actual products recommended
        assert abs(recall_10 - expected_recall_10) < 0.001, f"Recall@10 should be {expected_recall_10}, actual is {recall_10}"

        # Test boundary conditions
        assert self.metrics.recall_at_k([], predicted, 5) == 0.0, "Empty actual list should return 0"
        assert self.metrics.recall_at_k(actual, [], 5) == 0.0, "Empty predicted list should return 0"
        assert self.metrics.recall_at_k(actual, predicted, 0) == 0.0, "K=0 should return 0"

    def test_f1_score_at_k(self):
        """Test F1-Score@K metric"""
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]

        # Calculate F1@5
        precision_5 = self.metrics.precision_at_k(actual, predicted, 5)
        recall_5 = self.metrics.recall_at_k(actual, predicted, 5)
        f1_5 = self.metrics.f1_score_at_k(actual, predicted, 5)

        expected_f1_5 = 2 * (precision_5 * recall_5) / (precision_5 + recall_5)
        assert abs(f1_5 - expected_f1_5) < 0.001, f"F1@5 calculation error"

        # Test boundary conditions
        assert self.metrics.f1_score_at_k([], predicted, 5) == 0.0, "Empty actual list should return 0"
        assert self.metrics.f1_score_at_k(actual, [], 5) == 0.0, "Empty predicted list should return 0"

    def test_ndcg_at_k(self):
        """Test NDCG@K metric"""
        actual = [1, 2, 3, 4, 5]
        predicted = [1, 2, 6, 7, 8, 3, 4, 9, 10]

        # Test NDCG@5
        ndcg_5 = self.metrics.ndcg_at_k(actual, predicted, k=5)
        assert 0 <= ndcg_5 <= 1, f"NDCG@5 should be in [0,1] range, actual is {ndcg_5}"

        # Test perfect ranking case
        perfect_predicted = [1, 2, 3, 4, 5]
        perfect_ndcg = self.metrics.ndcg_at_k(actual, perfect_predicted, k=5)
        assert abs(perfect_ndcg - 1.0) < 0.001, "NDCG for perfect ranking should be close to 1.0"

        # Test different K values
        ndcg_10 = self.metrics.ndcg_at_k(actual, predicted, k=10)
        assert 0 <= ndcg_10 <= 1, "NDCG@10 should be in [0,1] range"

        # Test boundary conditions
        assert self.metrics.ndcg_at_k([], predicted, k=5) == 0.0, "Empty actual list should return 0"
        assert self.metrics.ndcg_at_k(actual, [], k=5) == 0.0, "Empty predicted list should return 0"
    
    def test_mean_average_precision(self):
        """Test MAP metric"""
        actual_list = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        predicted_list = [
            [1, 4, 2, 7, 3],
            [4, 1, 5, 8, 6],
            [7, 2, 8, 5, 9]
        ]

        map_score = self.metrics.mean_average_precision(actual_list, predicted_list, k=5)
        assert 0 <= map_score <= 1, f"MAP should be in [0,1] range, actual is {map_score}"

        # Test boundary conditions
        empty_actual = [[], [], []]
        map_empty = self.metrics.mean_average_precision(empty_actual, predicted_list, k=5)
        assert map_empty == 0.0, "MAP for empty actual list should be 0"

        # Test length mismatch
        with pytest.raises(ValueError):
            self.metrics.mean_average_precision([1, 2], [1, 2, 3], k=5)

    def test_diversity_score(self):
        """Test diversity metric"""
        # Test diversity of recommendation results
        recommendations = [
            {'category': 'A', 'brand': 'X'},
            {'category': 'B', 'brand': 'Y'},
            {'category': 'A', 'brand': 'Z'},
            {'category': 'C', 'brand': 'X'},
            {'category': 'B', 'brand': 'Y'}
        ]

        # Test category diversity
        category_diversity = self.metrics.diversity_score(recommendations, 'category')
        assert 0 <= category_diversity <= 1, f"Category diversity should be in [0,1] range, actual is {category_diversity}"

        # Test brand diversity
        brand_diversity = self.metrics.diversity_score(recommendations, 'brand')
        assert 0 <= brand_diversity <= 1, f"Brand diversity should be in [0,1] range, actual is {brand_diversity}"

        # Test completely identical recommendation results
        same_recommendations = [
            {'category': 'A', 'brand': 'X'},
            {'category': 'A', 'brand': 'X'},
            {'category': 'A', 'brand': 'X'}
        ]
        same_diversity = self.metrics.diversity_score(same_recommendations, 'category')
        assert same_diversity < 0.5, "Diversity of completely identical recommendation results should be very low"

        # Test boundary conditions
        empty_diversity = self.metrics.diversity_score([], 'category')
        assert empty_diversity == 0.0, "Empty recommendation list should return 0.0"

        print("✓ Diversity metric test passed")
        print(f"✓ Category diversity: {category_diversity:.3f}")
        print(f"✓ Brand diversity: {brand_diversity:.3f}")
    
    def test_coverage_score(self):
        """Test coverage metric"""
        recommendations = [
            [1, 2, 3, 4, 5],
            [3, 4, 5, 6, 7],
            [5, 6, 7, 8, 9]
        ]

        all_items = set(range(1, 21))  # Total 20 products

        coverage_metrics = self.metrics.coverage_score(recommendations, all_items)

        # Verify coverage metrics
        assert 'item_coverage' in coverage_metrics, "Should include item coverage"
        assert 'recommendation_coverage' in coverage_metrics, "Should include recommendation coverage"

        item_coverage = coverage_metrics['item_coverage']
        assert 0 <= item_coverage <= 1, f"Item coverage should be in [0,1] range, actual is {item_coverage}"

        # Verify calculation correctness
        unique_recommended = len(set([item for rec in recommendations for item in rec]))
        expected_coverage = unique_recommended / len(all_items)
        assert abs(item_coverage - expected_coverage) < 0.001, "Item coverage calculation error"

    def test_novelty_score(self):
        """Test novelty metric"""
        recommendations = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        # Set product popularity (normalized values)
        item_popularity = {
            1: 0.9, 2: 0.8, 3: 0.7,  # High popularity
            4: 0.5, 5: 0.4, 6: 0.3,  # Medium popularity
            7: 0.2, 8: 0.1, 9: 0.05  # Low popularity (novel)
        }

        novelty = self.metrics.novelty_score(recommendations, item_popularity)

        # Verify novelty score
        assert 0 <= novelty <= 1, f"Novelty score should be in [0,1] range, actual is {novelty}"

        # Verify calculation logic: novelty = 1 - popularity
        expected_novelty = 1 - np.mean(list(item_popularity.values()))
        assert abs(novelty - expected_novelty) < 0.1, "Novelty calculation logic is correct"

    def test_long_tail_coverage(self):
        """Test long tail coverage"""
        recommendations = [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10]
        ]

        # Create popularity distribution (simulate long tail distribution)
        item_popularity = {}
        for i in range(1, 21):
            # First 5 products have high popularity, last 15 products have low popularity (long tail)
            if i <= 5:
                item_popularity[i] = 1.0 - (i - 1) * 0.1  # 1.0, 0.9, 0.8, 0.7, 0.6
            else:
                item_popularity[i] = 0.3 - (i - 6) * 0.02  # Decreasing low popularity

        long_tail_cov = self.metrics.long_tail_coverage(
            recommendations, item_popularity, tail_threshold=0.2
        )

        # Verify long tail coverage
        assert 0 <= long_tail_cov <= 1, f"Long tail coverage should be in [0,1] range, actual is {long_tail_cov}"

        # Test boundary conditions
        empty_coverage = self.metrics.long_tail_coverage([], item_popularity)
        assert empty_coverage == 0.0, "Long tail coverage of empty recommendation list should be 0"
    
    def test_comprehensive_evaluation(self):
        """Test comprehensive evaluation function"""
        user_recommendations, user_ground_truth, items_df = self.create_test_data()

        # Perform comprehensive evaluation
        evaluation_results = self.metrics.evaluate_recommendations(
            user_recommendations, user_ground_truth, items_df, k_values=[5, 10, 20]
        )

        # Verify evaluation result structure
        expected_metrics = [
            'precision_at_k', 'recall_at_k', 'f1_at_k',
            'ndcg_at_k', 'map_at_k', 'hit_rate_at_k'
        ]

        for metric in expected_metrics:
            assert metric in evaluation_results, f"Should include {metric} metric"
            assert isinstance(evaluation_results[metric], dict), f"{metric} should be a dictionary"

            for k in [5, 10, 20]:
                assert k in evaluation_results[metric], f"{metric} should include K={k} results"
                value = evaluation_results[metric][k]
                assert 0 <= value <= 1, f"{metric}@{k} should be in [0,1] range, actual is {value}"

        # Verify diversity and coverage metrics
        assert 'diversity' in evaluation_results, "Should include diversity metric"
        assert 'coverage' in evaluation_results, "Should include coverage metric"
        assert 'novelty' in evaluation_results, "Should include novelty metric"
        assert 'long_tail_coverage' in evaluation_results, "Should include long tail coverage metric"

        # Verify metric value reasonableness
        novelty = evaluation_results['novelty']
        assert 0 <= novelty <= 1, f"Novelty should be in [0,1] range, actual is {novelty}"

        long_tail_cov = evaluation_results['long_tail_coverage']
        assert 0 <= long_tail_cov <= 1, f"Long tail coverage should be in [0,1] range, actual is {long_tail_cov}"

    def test_evaluation_report_generation(self):
        """Test evaluation report generation"""
        user_recommendations, user_ground_truth, items_df = self.create_test_data()

        # Perform evaluation
        evaluation_results = self.metrics.evaluate_recommendations(
            user_recommendations, user_ground_truth, items_df, k_values=[5, 10]
        )

        # Generate report
        report = self.metrics.generate_evaluation_report(
            evaluation_results, algorithm_name="Test Recommendation Algorithm"
        )

        # Verify report content
        assert isinstance(report, str), "Report should be a string"
        assert len(report) > 0, "Report should not be empty"
        assert "Test Recommendation Algorithm" in report, "Report should include algorithm name"
        assert "Evaluation Metrics Summary" in report, "Report should include metrics summary"
        assert "Precision@K" in report, "Report should include Precision metric"
        assert "Diversity and Coverage" in report, "Report should include diversity analysis"

        # Verify report format
        lines = report.split('\n')
        assert len(lines) > 10, "Report should include multiple lines of content"

        # Verify Markdown format
        has_table_header = any('|' in line and ('K' in line) for line in lines)
        assert has_table_header, "Report should include metrics in table format"

    def test_edge_cases_and_robustness(self):
        """Test edge cases and robustness"""
        # Test empty data
        empty_user_recs = {}
        empty_ground_truth = {}
        items_df = pd.DataFrame({
            'item_id': [1, 2, 3],
            'category': ['A', 'B', 'C'],
            'brand': ['X', 'Y', 'Z']
        })

        empty_results = self.metrics.evaluate_recommendations(
            empty_user_recs, empty_ground_truth, items_df
        )

        # Verify empty data handling
        for metric_dict in empty_results.values():
            if isinstance(metric_dict, dict) and metric_dict:
                for value in metric_dict.values():
                    if isinstance(value, (int, float)):
                        assert 0 <= value <= 1, "Metric values for empty data should be in reasonable range"

        # Test single user data
        single_user_recs = {1: [1, 2, 3, 4, 5]}
        single_ground_truth = {1: [2, 3, 6, 7, 8]}

        single_results = self.metrics.evaluate_recommendations(
            single_user_recs, single_ground_truth, items_df, k_values=[3, 5]
        )

        # Verify single user handling
        assert single_results['precision_at_k'][3] > 0, "Single user should be able to correctly calculate precision"
        assert single_results['recall_at_k'][3] > 0, "Single user should be able to correctly calculate recall"

        # Test mismatched user IDs
        mismatched_recs = {1: [1, 2, 3], 2: [4, 5, 6]}
        mismatched_truth = {3: [1, 2], 4: [4, 5]}  # User IDs don't match

        mismatched_results = self.metrics.evaluate_recommendations(
            mismatched_recs, mismatched_truth, items_df
        )

        # Mismatched case should have reasonable handling
        assert isinstance(mismatched_results, dict), "Mismatched data should return result dictionary"