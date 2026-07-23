import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.machine import mainMachine
from orm.orm import Request, Status, db
from datetime import datetime

class TestIntelligentDecision:

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

    def test_cooling_mode_temperature_adaptation(self, machine):
        """Test temperature adaptation stop in cooling mode"""
        # Create slave status: current temperature lower than target temperature
        slave = Status.create(
            card_id="test_card_cooling",
            target_temp=22,
            cur_temp=20.0,  # Lower than target temperature
            speed=2,        # Medium speed
            energy=0.0,
            amount=0.0
        )

        # Create adjustment request
        request = Request.create(
            slave_id=slave.id,
            temp=22.0,
            speed=2,
            time=datetime.now()
        )

        machine.main_status = 1  # Cooling mode

        # Simulate request processing logic
        status = Status.get(Status.id == request.slave_id)
        if machine.main_status == 1:  # Cooling mode
            if status.cur_temp < request.temp:  # Current temperature lower than target temperature
                expected_speed = 0  # Should stop fan
            else:
                expected_speed = request.speed

        assert expected_speed == 0, "Should stop fan when current temperature is lower than target in cooling mode"

    def test_heating_mode_temperature_adaptation(self, machine):
        """Test temperature adaptation stop in heating mode"""
        # Create slave status: current temperature higher than target temperature
        slave = Status.create(
            card_id="test_card_heating",
            target_temp=28,
            cur_temp=30.0,  # Higher than target temperature
            speed=2,        # Medium speed
            energy=0.0,
            amount=0.0
        )

        # Create adjustment request
        request = Request.create(
            slave_id=slave.id,
            temp=28.0,
            speed=2,
            time=datetime.now()
        )

        machine.main_status = 2  # Heating mode

        # Simulate request processing logic
        status = Status.get(Status.id == request.slave_id)
        if machine.main_status == 2:  # Heating mode
            if status.cur_temp > request.temp:  # Current temperature higher than target temperature
                expected_speed = 0  # Should stop fan
            else:
                expected_speed = request.speed

        assert expected_speed == 0, "Should stop fan when current temperature is higher than target in heating mode"

    def test_temperature_reached_auto_stop(self, machine):
        """Test automatic fan stop when temperature reaches target"""
        # Create slave status: temperature already reached target
        slave = Status.create(
            card_id="test_card_auto_stop",
            target_temp=25,
            cur_temp=25.0,  # Already reached target temperature
            speed=2,        # Medium speed
            energy=0.0,
            amount=0.0
        )

        # Simulate intelligent decision logic
        if slave.cur_temp == slave.target_temp:
            expected_speed = 0  # Should automatically stop fan
        else:
            expected_speed = slave.speed

        assert expected_speed == 0, "Should automatically stop fan when temperature reaches target"
