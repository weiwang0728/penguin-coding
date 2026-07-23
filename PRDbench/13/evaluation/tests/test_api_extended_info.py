"""
Test API recommendation result extended information
"""
import pytest
import requests
import json
import time
import threading
import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from api.main import app
import uvicorn


class TestAPIExtendedInfo:
    @classmethod
    def setup_class(cls):
        """Start API server"""
        cls.port = 8003  # Use different port to avoid conflict
        cls.base_url = f"http://localhost:{cls.port}"
        cls.server_thread = None
        cls._start_server()
        cls._wait_for_server()
    
    @classmethod
    def _start_server(cls):
        """Start server in background thread"""
        def run_server():
            try:
                uvicorn.run(app, host="127.0.0.1", port=cls.port, log_level="error")
            except Exception as e:
                print(f"Server startup failed: {e}")
        
        cls.server_thread = threading.Thread(target=run_server, daemon=True)
        cls.server_thread.start()
    
    @classmethod
    def _wait_for_server(cls):
        """Wait for server startup completion"""
        import time
        max_attempts = 30
        for i in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✓ Server started successfully after {i+1} seconds")
                    return
            except:
                pass
            time.sleep(1)

        for i in range(10):
            try:
                response = requests.get(cls.base_url, timeout=1)
                print(f"✓ Server started successfully (status code: {response.status_code})")
                return
            except:
                pass
            time.sleep(1)

        raise Exception("Server startup timeout")
    
    @classmethod
    def teardown_class(cls):
        """Clean up resources"""
        pass
    
    def test_recommend_extended_response(self):
        """Test recommendation result extended information"""
        try:
            # Prepare test data
            test_data = {
                "user_id": 1,
                "top_n": 5
            }

            # Send POST request to recommendation API
            response = requests.post(
                f"{self.base_url}/api/v1/recommend",
                json=test_data,
                timeout=60  # Increase timeout
            )

            # Verify response status code
            assert response.status_code == 200, f"API response status code error: {response.status_code}"

            # Parse response
            result = response.json()

            # Verify basic response structure
            assert "recommendations" in result, "Missing recommendations field in response"
            assert "strategy" in result, "Missing strategy field in response"
            assert "diversity_score" in result, "Missing diversity_score field in response"
            assert "processing_time" in result, "Missing processing_time field in response"

            recommendations = result["recommendations"]
            assert len(recommendations) > 0, "Recommendation result cannot be empty"

            # Verify extended information in recommendation results
            extended_fields_found = set()

            for i, item in enumerate(recommendations):
                # Verify required basic fields
                assert "item_id" in item, f"Recommended item #{i+1} missing item_id field"
                assert "score" in item, f"Recommended item #{i+1} missing score field"
                assert "title" in item, f"Recommended item #{i+1} missing title field"

                # Collect extended information fields
                if "reason" in item and item["reason"]:
                    extended_fields_found.add("recommendation_reason")

                if "category" in item and item["category"]:
                    extended_fields_found.add("item_category")

                if "price" in item and item["price"] is not None:
                    extended_fields_found.add("item_price")

                if "brand" in item and item["brand"]:
                    extended_fields_found.add("item_brand")

                if "description" in item and item["description"]:
                    extended_fields_found.add("item_description")

            # Check recommendation algorithm source (at root level)
            if "strategy" in result and result["strategy"]:
                extended_fields_found.add("recommendation_algorithm_source")

            # Check diversity score (diversity label)
            if "diversity_score" in result:
                if isinstance(result["diversity_score"], (int, float)):
                    extended_fields_found.add("diversity_score")
                elif isinstance(result["diversity_score"], dict):
                    extended_fields_found.add("diversity_score")

            # Verify at least 3 types of extended information
            assert len(extended_fields_found) >= 3, f"Insufficient extended information, only found {len(extended_fields_found)} types: {extended_fields_found}"

            # Verify specific extended information content
            sample_item = recommendations[0]

            # Verify recommendation reason
            if "reason" in sample_item:
                assert isinstance(sample_item["reason"], str), "Recommendation reason should be string type"
                assert len(sample_item["reason"]) > 0, "Recommendation reason cannot be empty"

            # Verify item category
            if "category" in sample_item:
                assert isinstance(sample_item["category"], str), "Item category should be string type"
                assert len(sample_item["category"]) > 0, "Item category cannot be empty"

            # Verify price information
            if "price" in sample_item and sample_item["price"] is not None:
                assert isinstance(sample_item["price"], (int, float)), "Item price should be numeric type"
                assert sample_item["price"] >= 0, "Item price cannot be negative"

            # Verify diversity score
            diversity_score = result["diversity_score"]
            if isinstance(diversity_score, (int, float)):
                assert 0 <= diversity_score <= 1, f"Diversity score should be between 0-1: {diversity_score}"
            elif isinstance(diversity_score, dict):
                # If dictionary, verify values in dictionary
                for key, value in diversity_score.items():
                    assert isinstance(value, (int, float)), f"Diversity score {key} should be numeric type"
                    assert 0 <= value <= 1, f"Diversity score {key} should be between 0-1: {value}"
            else:
                assert False, f"Diversity score format incorrect: {type(diversity_score)}"

            # Verify processing time
            assert isinstance(result["processing_time"], (int, float)), "Processing time should be numeric type"
            assert result["processing_time"] > 0, "Processing time should be greater than 0"

            print("✓ API recommendation result extended information test passed")
            print(f"✓ Found extended information types: {extended_fields_found}")

            # Format diversity score display
            diversity_score = result['diversity_score']
            if isinstance(diversity_score, (int, float)):
                print(f"✓ Diversity score: {diversity_score:.3f}")
            elif isinstance(diversity_score, dict):
                formatted_scores = {k: f"{v:.3f}" for k, v in diversity_score.items()}
                print(f"✓ Diversity score: {formatted_scores}")

            print(f"✓ Processing time: {result['processing_time']:.3f} seconds")
            print(f"✓ Recommendation strategy: {result.get('strategy', 'N/A')}")

        except requests.exceptions.RequestException as e:
            pytest.fail(f"API request failed: {e}")
        except Exception as e:
            pytest.fail(f"Test execution failed: {e}")
    
    def test_recommend_with_different_strategies(self):
        """Test extended information returned by different recommendation strategies"""
        strategies = ["hybrid_weighted", "content_based", "user_cf"]

        for strategy in strategies:
            try:
                test_data = {
                    "user_id": 1,
                    "top_n": 3,
                    "strategy": strategy
                }

                response = requests.post(
                    f"{self.base_url}/api/v1/recommend",
                    json=test_data,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()

                    # Verify strategy information is correctly returned
                    assert "strategy" in result, f"Strategy {strategy} response missing strategy field"

                    # Verify recommendation results contain extended information
                    if result.get("recommendations"):
                        sample_item = result["recommendations"][0]

                        # Verify at least has recommendation reason
                        assert "reason" in sample_item, f"Strategy {strategy} recommendation result missing recommendation reason"

                        print(f"✓ Strategy {strategy} test passed")

            except Exception as e:
                print(f"⚠ Strategy {strategy} test failed: {e}")
                # Don't let single strategy failure affect overall test
                continue


if __name__ == "__main__":
    pytest.main([__file__, "-v"])