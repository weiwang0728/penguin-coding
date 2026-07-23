"""
Test API basic recommendation endpoint
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
src_path = str(Path(__file__).parent.parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from api.main import app
    import uvicorn
except ImportError as e:
    print(f"Import failed: {e}")
    print(f"Current Python path: {sys.path[:3]}")
    raise


class TestAPIBasicRecommend:
    @classmethod
    def setup_class(cls):
        """Start API server"""
        cls.port = 8002  # Use different port to avoid conflicts
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
        """Wait for server startup to complete"""
        import time
        max_attempts = 30  # Wait up to 30 seconds
        for i in range(max_attempts):
            try:
                response = requests.get(f"{cls.base_url}/health", timeout=1)
                if response.status_code == 200:
                    print(f"✓ Server started successfully after {i+1} seconds")
                    return
            except:
                pass
            time.sleep(1)

        # If health check fails, try testing root path directly
        for i in range(10):
            try:
                response = requests.get(cls.base_url, timeout=1)
                print(f"✓ Server startup successful (status code: {response.status_code})")
                return
            except:
                pass
            time.sleep(1)

        raise Exception("Server startup timeout")

    @classmethod
    def teardown_class(cls):
        """Clean up resources"""
        # Server thread will automatically terminate when test ends (daemon=True)
        pass
    
    def test_recommend_endpoint(self):
        """Test basic recommendation endpoint"""
        try:
            # Prepare test data
            test_data = {
                "user_id": 1,  # Use integer type for user_id
                "top_n": 10
            }

            # Send POST request to recommendation endpoint
            response = requests.post(
                f"{self.base_url}/api/v1/recommend",
                json=test_data,
                timeout=60  # Increase timeout to 60 seconds because recommendation system needs training time
            )

            # Verify response status code
            assert response.status_code == 200, f"API response status code error: {response.status_code}"

            # Verify response is JSON format
            try:
                result = response.json()
            except json.JSONDecodeError:
                pytest.fail("API response is not valid JSON format")

            # Verify response structure
            assert "recommendations" in result, "Response missing recommendations field"
            recommendations = result["recommendations"]

            # Verify recommendation count
            assert len(recommendations) == 10, f"Incorrect number of recommended items, expected 10, got {len(recommendations)}"

            # Verify fields for each recommended item
            required_fields = ["item_id", "score", "title"]
            for i, item in enumerate(recommendations):
                for field in required_fields:
                    assert field in item, f"Recommended item {i+1} missing {field} field"

                # Verify field types and values
                assert isinstance(item["item_id"], str), f"item_id should be string type"
                assert isinstance(item["score"], (int, float)), f"score should be numeric type"
                assert isinstance(item["title"], str), f"title should be string type"
                assert item["score"] >= 0, f"Recommendation score should be non-negative, actual value: {item['score']}"

            # Verify recommendations are sorted by score in descending order
            scores = [item["score"] for item in recommendations]
            assert scores == sorted(scores, reverse=True), "Recommendations should be sorted by score in descending order"

            print("✓ API basic recommendation endpoint test passed")
            print(f"✓ Successfully returned {len(recommendations)} recommended items")
            print(f"✓ Each item contains required fields: {required_fields}")
            print(f"✓ Recommendation score range: {min(scores):.3f} - {max(scores):.3f}")

        except requests.exceptions.RequestException as e:
            pytest.fail(f"API request failed: {e}")
        except Exception as e:
            pytest.fail(f"Test execution failed: {e}")
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            assert response.status_code == 200, "Health check endpoint should return 200 status code"

            result = response.json()
            assert "status" in result, "Health check response should include status field"
            assert result["status"] == "healthy", "Service status should be healthy"

            print("✓ API health check endpoint is normal")

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Health check request failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])