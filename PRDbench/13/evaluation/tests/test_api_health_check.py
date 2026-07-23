"""
Test API health check endpoint
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


class TestAPIHealthCheck:
    @classmethod
    def setup_class(cls):
        """Start API server"""
        cls.port = 8005  # Use different port to avoid conflict
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
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            # Send GET request to health check endpoint
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=30)

            # Verify response status code
            assert response.status_code == 200, f"Health check endpoint status code error: {response.status_code}"

            # Parse response
            result = response.json()

            # Verify basic health status fields
            required_fields = ["status", "timestamp", "version", "uptime"]
            for field in required_fields:
                assert field in result, f"Health check response missing {field} field"

            # Verify status value
            assert result["status"] in ["healthy", "degraded", "unhealthy"], f"Invalid health status value: {result['status']}"
            assert isinstance(result["uptime"], (int, float)), "Uptime should be numeric type"
            assert result["uptime"] >= 0, "Uptime should be non-negative"

            # Collect system status indicators
            health_indicators = []

            # 1. Service running status
            if "status" in result and result["status"]:
                health_indicators.append("service_running_status")

            # 2. Model loading status
            if "models_loaded" in result:
                health_indicators.append("model_loading_status")
                assert isinstance(result["models_loaded"], bool), "Model loading status should be boolean type"

            # 3. Data status
            if "data_status" in result and result["data_status"]:
                health_indicators.append("data_status")
                data_status = result["data_status"]
                assert isinstance(data_status, dict), "Data status should be dictionary type"

                # Verify detailed data status information
                data_fields = ["status", "users_count", "items_count", "interactions_count"]
                for field in data_fields:
                    if field in data_status:
                        health_indicators.append(f"data_{field}")

            # 4. System metrics (CPU, memory, disk)
            if "system_metrics" in result and result["system_metrics"]:
                health_indicators.append("system_resource_monitoring")
                system_metrics = result["system_metrics"]
                assert isinstance(system_metrics, dict), "System metrics should be dictionary type"

                # Check CPU usage
                if "cpu_usage" in system_metrics:
                    health_indicators.append("cpu_usage")
                    cpu_usage = system_metrics["cpu_usage"]
                    assert isinstance(cpu_usage, (int, float)), "CPU usage should be numeric type"
                    assert 0 <= cpu_usage <= 100, f"CPU usage should be between 0-100: {cpu_usage}"

                # Check memory usage
                if "memory_usage" in system_metrics:
                    health_indicators.append("memory_usage")
                    memory_usage = system_metrics["memory_usage"]
                    assert isinstance(memory_usage, (int, float)), "Memory usage should be numeric type"
                    assert 0 <= memory_usage <= 100, f"Memory usage should be between 0-100: {memory_usage}"

                # Check disk usage
                if "disk_usage" in system_metrics:
                    health_indicators.append("disk_usage")
                    disk_usage = system_metrics["disk_usage"]
                    assert isinstance(disk_usage, (int, float)), "Disk usage should be numeric type"
                    assert 0 <= disk_usage <= 100, f"Disk usage should be between 0-100: {disk_usage}"

            # 5. Uptime metric
            if "uptime" in result:
                health_indicators.append("system_uptime")

            # 6. Version information
            if "version" in result:
                health_indicators.append("system_version")

            # Verify at least 4 indicators
            assert len(health_indicators) >= 4, f"Insufficient health check indicators, only found {len(health_indicators)} items: {health_indicators}"

            # Verify reasonableness of specific indicators
            if "system_metrics" in result:
                system_metrics = result["system_metrics"]

                # Ensure system metric values are within reasonable range
                if "cpu_usage" in system_metrics:
                    cpu_usage = system_metrics["cpu_usage"]
                    assert cpu_usage >= 0, "CPU usage cannot be negative"

                if "memory_usage" in system_metrics:
                    memory_usage = system_metrics["memory_usage"]
                    assert memory_usage > 0, "Memory usage should be greater than 0 (system is running)"

            print("✓ Health check API endpoint test passed")
            print(f"✓ System status: {result['status']}")
            print(f"✓ Found health indicators: {health_indicators}")
            print(f"✓ System uptime: {result['uptime']:.2f} seconds")
            print(f"✓ Model status: {'loaded' if result.get('models_loaded', False) else 'not loaded'}")

            if "system_metrics" in result:
                metrics = result["system_metrics"]
                if "cpu_usage" in metrics:
                    print(f"✓ CPU usage: {metrics['cpu_usage']:.1f}%")
                if "memory_usage" in metrics:
                    print(f"✓ Memory usage: {metrics['memory_usage']:.1f}%")
                if "disk_usage" in metrics:
                    print(f"✓ Disk usage: {metrics['disk_usage']:.1f}%")

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Health check request failed: {e}")
        except Exception as e:
            pytest.fail(f"Test execution failed: {e}")
    
    def test_health_endpoint_detailed(self):
        """Test health check endpoint detailed information"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            assert response.status_code == 200, "Health check endpoint should return 200 status code"

            result = response.json()

            # Verify timestamp format
            assert "timestamp" in result, "Should contain timestamp field"
            timestamp_str = result["timestamp"]

            # Try to parse ISO format timestamp
            try:
                from datetime import datetime
                parsed_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00') if timestamp_str.endswith('Z') else timestamp_str)
                assert isinstance(parsed_time, datetime), "Timestamp should be valid datetime object"
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {timestamp_str}")

            # Verify version information
            if "version" in result:
                version = result["version"]
                assert isinstance(version, str), "Version should be string type"
                assert len(version) > 0, "Version string should not be empty"

            # Verify data status detailed information
            if "data_status" in result:
                data_status = result["data_status"]

                # Verify user data
                if "users_count" in data_status:
                    assert isinstance(data_status["users_count"], int), "Users count should be integer"
                    assert data_status["users_count"] >= 0, "Users count should be non-negative"

                # Verify item data
                if "items_count" in data_status:
                    assert isinstance(data_status["items_count"], int), "Items count should be integer"
                    assert data_status["items_count"] >= 0, "Items count should be non-negative"

                # Verify interaction data
                if "interactions_count" in data_status:
                    assert isinstance(data_status["interactions_count"], int), "Interactions count should be integer"
                    assert data_status["interactions_count"] >= 0, "Interactions count should be non-negative"

            print("✓ Health check detailed information verification passed")
            print(f"✓ Response contains complete health status information")

        except Exception as e:
            pytest.fail(f"Health check detailed information test failed: {e}")
    
    def test_health_endpoint_response_time(self):
        """Test health check endpoint response time"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            response_time = time.time() - start_time

            assert response.status_code == 200, "Health check endpoint should return 200 status code"
            assert response_time < 5.0, f"Health check response time too long: {response_time:.2f} seconds"

            print(f"✓ Health check response time test passed: {response_time:.3f} seconds")

        except Exception as e:
            pytest.fail(f"Health check response time test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])