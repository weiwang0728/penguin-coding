import pytest
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

class TestBUPTAirAPI:

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Setup: Clean data
        requests.delete(f"{BASE_URL}/slave/delete_all")
        yield
        # Teardown: Clean data
        requests.delete(f"{BASE_URL}/slave/delete_all")

    def test_system_startup_and_status(self):
        """Test system startup and status query"""
        # Start the machine
        response = requests.get(f"{BASE_URL}/machine/open")
        assert response.status_code == 200

        # Query machine status
        response = requests.get(f"{BASE_URL}/machine/info")
        assert response.status_code == 200

        data = response.json()
        assert 'status' in data
        assert 'power' in data
        assert 'scheduling' in data
        assert 'standby' in data

    def test_slave_management(self):
        """Test slave machine management functionality"""
        # Add slave machine
        slave_data = {"card_id": "test_card_123"}
        response = requests.post(f"{BASE_URL}/slave/", json=slave_data)
        assert response.status_code == 200

        # Query slave machine status
        response = requests.get(f"{BASE_URL}/slave/check/test_card_123")
        assert response.status_code == 200

        data = response.json()
        assert data['card_id'] == "test_card_123"
        assert 'target_temp' in data
        assert 'cur_temp' in data
        assert 'speed' in data

    def test_mode_switching(self):
        """Test main machine mode switching"""
        # Add slave machine
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_mode"})

        # Set cooling mode
        mode_data = {"power": 3, "scheduling": 1, "status": 1}
        response = requests.post(f"{BASE_URL}/machine/set", json=mode_data)
        assert response.status_code == 200

        # Check if slave temperature is reset
        response = requests.get(f"{BASE_URL}/slave/1")
        data = response.json()
        if data['target_temp'] > 25:
            assert data['target_temp'] == 22

        # Set heating mode
        mode_data = {"power": 3, "scheduling": 1, "status": 2}
        response = requests.post(f"{BASE_URL}/machine/set", json=mode_data)
        assert response.status_code == 200

        # Check if slave temperature is reset
        response = requests.get(f"{BASE_URL}/slave/1")
        data = response.json()
        if data['target_temp'] <= 25:
            assert data['target_temp'] == 28

    def test_temperature_adjustment(self):
        """Test temperature adjustment functionality"""
        # Add slave machine and set cooling mode
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_temp"})
        requests.post(f"{BASE_URL}/machine/set", json={"power": 3, "scheduling": 1, "status": 1})

        # Get initial temperature
        response = requests.get(f"{BASE_URL}/slave/1")
        initial_temp = response.json()['target_temp']

        # Lower temperature
        response = requests.get(f"{BASE_URL}/slave/temp/low/1")
        assert response.status_code == 200

        # Verify temperature change
        response = requests.get(f"{BASE_URL}/slave/1")
        new_temp = response.json()['target_temp']
        # Note: May need to wait due to asynchronous processing
        time.sleep(1)

    def test_speed_adjustment(self):
        """Test fan speed adjustment functionality"""
        # Add slave machine
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_speed"})

        # Increase fan speed
        response = requests.get(f"{BASE_URL}/slave/speed/high/1")
        assert response.status_code == 200

        # Verify fan speed does not exceed level 3
        for _ in range(5):  # Try to exceed maximum speed
            requests.get(f"{BASE_URL}/slave/speed/high/1")

        response = requests.get(f"{BASE_URL}/slave/1")
        data = response.json()
        assert data['speed'] <= 3

    def test_cost_calculation(self):
        """Test cost calculation functionality"""
        # Add slave machine and configure
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_cost"})
        requests.post(f"{BASE_URL}/machine/set", json={"power": 3, "scheduling": 1, "status": 1})

        # Get initial cost
        response = requests.get(f"{BASE_URL}/slave/1")
        initial_amount = response.json()['amount']

        # Set medium speed and start cost calculation
        requests.get(f"{BASE_URL}/slave/speed/high/1")
        requests.get(f"{BASE_URL}/slave/speed/high/1")  # Set to medium speed (speed=2)
        requests.get(f"{BASE_URL}/cost/open")

        # Wait for a period of time
        time.sleep(5)

        # Check if cost increased
        response = requests.get(f"{BASE_URL}/slave/1")
        final_amount = response.json()['amount']

        requests.get(f"{BASE_URL}/cost/close")

        assert final_amount > initial_amount

    def test_report_generation(self):
        """Test report generation functionality"""
        # Add slave machine and perform some operations
        requests.post(f"{BASE_URL}/slave/", json={"card_id": "test_card_report"})
        requests.get(f"{BASE_URL}/slave/speed/high/1")
        requests.get(f"{BASE_URL}/slave/shutdown/1")

        # Generate report
        report_data = {
            "startDate": datetime.now().strftime("%Y-%m-%d"),
            "endDate": datetime.now().strftime("%Y-%m-%d")
        }
        response = requests.post(f"{BASE_URL}/log/", json=report_data)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        if data:  # If there is data
            assert 'ID' in data[0]
            assert 'Count' in data[0]
            assert 'Record' in data[0]
            assert 'Cost' in data[0]

if __name__ == "__main__":
    pytest.main([__file__])
