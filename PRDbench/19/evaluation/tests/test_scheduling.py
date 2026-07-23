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

    @pytest.fixture
    def setup_db(self):
        """Setup test database"""
        db.create_tables([Request, Status], safe=True)
        yield
        # Cleanup
        Request.delete().execute()
        Status.delete().execute()

    @pytest.fixture
    def machine(self):
        """Create main machine instance"""
        return mainMachine()

    def test_random_scheduling(self, setup_db, machine):
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

        # Run random scheduling multiple times to verify randomness
        results = []
        for _ in range(10):
            # Recreate requests (because get_request will delete processed requests)
            Request.delete().execute()
            for i in range(5):
                Request.create(
                    slave_id=i+1,
                    temp=22.0,
                    speed=1,
                    time=datetime.now()
                )

            machine.get_request()
            # Record selected request IDs
            selected_ids = [req.slave_id for req in machine.requestList]
            results.append(tuple(sorted(selected_ids)))

        # Verify results have some randomness (not always exactly the same)
        unique_results = set(results)
        assert len(unique_results) > 1, "Random scheduling should produce different results"

    def test_speed_priority_scheduling(self, setup_db, machine):
        """Test speed priority scheduling algorithm"""
        # Create requests with different speeds
        Request.create(slave_id=1, temp=22.0, speed=1, time=datetime.now())  # Low speed
        Request.create(slave_id=2, temp=22.0, speed=3, time=datetime.now())  # High speed
        Request.create(slave_id=3, temp=22.0, speed=2, time=datetime.now())  # Medium speed

        machine.choice = 3  # Speed priority
        machine.num = 3     # Process at most 3 requests

        machine.get_request()

        # Verify selected requests are sorted by speed in descending order
        selected_speeds = [req.speed for req in machine.requestList]
        assert len(selected_speeds) <= 3
        assert selected_speeds == sorted(selected_speeds, reverse=True)

    def test_power_first_priority(self, setup_db, machine):
        """Test power on/off requests priority processing"""
        # Create slave status
        Status.create(id=1, card_id="card1", target_temp=22, cur_temp=25.0, speed=0, energy=0.0, amount=0.0)  # Shutdown state
        Status.create(id=2, card_id="card2", target_temp=22, cur_temp=25.0, speed=2, energy=0.0, amount=0.0)  # Running state

        # Create requests: power on and power off requests
        Request.create(slave_id=1, temp=22.0, speed=2, time=datetime.now())  # Power on request (0->2)
        Request.create(slave_id=2, temp=22.0, speed=0, time=datetime.now())  # Power off request (2->0)
        Request.create(slave_id=3, temp=22.0, speed=1, time=datetime.now())  # Normal request

        machine.choice = 1  # Random scheduling
        machine.num = 2     # Process at most 2 requests

        machine.get_request()

        # Verify power on/off requests are processed first
        selected_ids = [req.slave_id for req in machine.requestList]
        assert 1 in selected_ids  # Power on request
        assert 2 in selected_ids  # Power off request
        assert len(selected_ids) == 2
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.machine import mainMachine
from orm.orm import Request, Status, db
from datetime import datetime
import random

class TestSchedulingAlgorithms:

    @pytest.fixture
    def setup_db(self):
        """Setup test database"""
        db.create_tables([Request, Status], safe=True)
        yield
        # Cleanup
        Request.delete().execute()
        Status.delete().execute()

    @pytest.fixture
    def machine(self):
        """Create main machine instance"""
        return mainMachine()

    def test_random_scheduling(self, setup_db, machine):
        """Test random scheduling algorithm"""
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

        # Run random scheduling multiple times to verify randomness
        results = []
        for _ in range(10):
            # Recreate requests (because get_request will delete processed requests)
            Request.delete().execute()
            for i in range(5):
                Request.create(
                    slave_id=i+1,
                    temp=22.0,
                    speed=1,
                    time=datetime.now()
                )

            machine.get_request()
            # Record selected request IDs
            selected_ids = [req.slave_id for req in machine.requestList]
            results.append(tuple(sorted(selected_ids)))

        # Verify results have some randomness (not always exactly the same)
        unique_results = set(results)
        assert len(unique_results) > 1, "Random scheduling should produce different results"

    def test_speed_priority_scheduling(self, setup_db, machine):
        """Test speed priority scheduling algorithm"""
        # Create requests with different speeds
        Request.create(slave_id=1, temp=22.0, speed=1, time=datetime.now())  # Low speed
        Request.create(slave_id=2, temp=22.0, speed=3, time=datetime.now())  # High speed
        Request.create(slave_id=3, temp=22.0, speed=2, time=datetime.now())  # Medium speed

        machine.choice = 3  # Speed priority
        machine.num = 3     # Process at most 3 requests

        machine.get_request()

        # Verify selected requests are sorted by speed in descending order
        selected_speeds = [req.speed for req in machine.requestList]
        assert len(selected_speeds) <= 3
        assert selected_speeds == sorted(selected_speeds, reverse=True)

    def test_power_first_priority(self, setup_db, machine):
        """Test power on/off requests priority processing"""
        # Create slave status
        Status.create(id=1, card_id="card1", target_temp=22, cur_temp=25.0, speed=0, energy=0.0, amount=0.0)  # Shutdown state
        Status.create(id=2, card_id="card2", target_temp=22, cur_temp=25.0, speed=2, energy=0.0, amount=0.0)  # Running state

        # Create requests: power on and power off requests
        Request.create(slave_id=1, temp=22.0, speed=2, time=datetime.now())  # Power on request (0->2)
        Request.create(slave_id=2, temp=22.0, speed=0, time=datetime.now())  # Power off request (2->0)
        Request.create(slave_id=3, temp=22.0, speed=1, time=datetime.now())  # Normal request

        machine.choice = 1  # Random scheduling
        machine.num = 2     # Process at most 2 requests

        machine.get_request()

        # Verify power on/off requests are processed first
        selected_ids = [req.slave_id for req in machine.requestList]
        assert 1 in selected_ids  # Power on request
        assert 2 in selected_ids  # Power off request
        assert len(selected_ids) == 2
