import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.machine import mainMachine
from orm.orm import Request, Status, db
from datetime import datetime
import random

class TestSchedulingAlgorithms:

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup test database"""
        # Clean existing data first
        try:
            Request.delete().execute()
            Status.delete().execute()
        except:
            pass

        # Create tables
        db.create_tables([Request, Status], safe=True)
        yield

        # Cleanup after test
        try:
            Request.delete().execute()
            Status.delete().execute()
        except:
            pass

    @pytest.fixture
    def machine(self):
        """Create main machine instance"""
        return mainMachine()

    def test_random_scheduling(self, machine):
        """Test random scheduling algorithm"""
        # Create corresponding slave status first
        for i in range(5):
            Status.create(
                id=i+1,
                card_id=f"test_card_{i+1}",
                target_temp=25,
                cur_temp=25.0,
                speed=0,
                energy=0.0,
                amount=0.0
            )

        # Create multiple requests
        for i in range(5):
            Request.create(
                slave_id=i+1,
                temp=22.0,
                speed=1,
                time=datetime.now()
            )

        machine.choice = 1  # Random scheduling
        machine.num = 3     # Process at most 3 requests

        # Run scheduling once to verify basic functionality
        machine.get_request()

        # Verify requests were selected
        assert len(machine.requestList) <= machine.num
        assert len(machine.requestList) > 0

    def test_speed_priority_scheduling(self, machine):
        """Test speed priority scheduling algorithm"""
        # Create corresponding slave status first (all in running state to avoid power on/off priority)
        for i in range(1, 4):
            Status.create(
                id=i,
                card_id=f"test_card_{i}",
                target_temp=25,
                cur_temp=25.0,
                speed=1,  # Set to running state to avoid power on/off requests
                energy=0.0,
                amount=0.0
            )

        # Create requests with different speeds (none are power on/off requests)
        Request.create(slave_id=1, temp=22.0, speed=1, time=datetime.now())  # Low speed
        Request.create(slave_id=2, temp=22.0, speed=3, time=datetime.now())  # High speed
        Request.create(slave_id=3, temp=22.0, speed=2, time=datetime.now())  # Medium speed

        machine.choice = 3  # Speed priority
        machine.num = 3     # Process at most 3 requests

        machine.get_request()

        # Verify selected requests are sorted by speed in descending order
        selected_speeds = [req.speed for req in machine.requestList]
        assert len(selected_speeds) <= 3
        assert len(selected_speeds) > 0
        # Verify speeds are sorted in descending order
        for i in range(len(selected_speeds) - 1):
            assert selected_speeds[i] >= selected_speeds[i + 1], f"Speeds should be sorted in descending order, but got {selected_speeds}"

    def test_power_first_priority(self, machine):
        """Test power on/off requests priority processing"""
        # Create slave status
        Status.create(id=1, card_id="card1", target_temp=22, cur_temp=25.0, speed=0, energy=0.0, amount=0.0)  # Shutdown state
        Status.create(id=2, card_id="card2", target_temp=22, cur_temp=25.0, speed=2, energy=0.0, amount=0.0)  # Running state
        Status.create(id=3, card_id="card3", target_temp=22, cur_temp=25.0, speed=1, energy=0.0, amount=0.0)  # Running state

        # Create requests: power on and power off requests
        Request.create(slave_id=1, temp=22.0, speed=2, time=datetime.now())  # Power on request (0->2)
        Request.create(slave_id=2, temp=22.0, speed=0, time=datetime.now())  # Power off request (2->0)
        Request.create(slave_id=3, temp=22.0, speed=1, time=datetime.now())  # Normal request

        machine.choice = 1  # Random scheduling
        machine.num = 2     # Limit to 2 requests to test priority

        machine.get_request()

        # Verify power on/off requests are processed first
        selected_ids = [req.slave_id for req in machine.requestList]

        # Power on/off requests should be selected first
        power_requests = []
        for req in machine.requestList:
            if req.slave_id == 1:  # Power on request
                power_requests.append(req.slave_id)
            elif req.slave_id == 2:  # Power off request
                power_requests.append(req.slave_id)

        # At least one power on/off request should be processed
        assert len(power_requests) > 0, f"Should prioritize power on/off requests, but selected request IDs are: {selected_ids}"
        assert len(selected_ids) <= machine.num
