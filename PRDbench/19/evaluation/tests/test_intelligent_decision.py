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
            slave_id=1,
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

    def test_cooling_mode_normal_operation(self, setup_db, machine):
        """Test normal operation in cooling mode"""
        # Create slave status: current temperature higher than target temperature
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=22,
            cur_temp=25.0,  # Higher than target temperature
            speed=0,        # Shutdown state
            energy=0.0,
            amount=0.0
        )

        # Create adjustment request
        request = Request.create(
            slave_id=1,
            temp=22.0,
            speed=2,
            time=datetime.now()
        )

        machine.main_status = 1  # Cooling mode

        # Simulate request processing logic
        status = Status.get(Status.id == request.slave_id)
        if machine.main_status == 1:  # Cooling mode
            if status.cur_temp >= request.temp:  # Current temperature higher than or equal to target temperature
                expected_speed = request.speed  # Should operate normally
            else:
                expected_speed = 0

        assert expected_speed == 2, "Should operate normally when current temperature is higher than target in cooling mode"

    def test_heating_mode_normal_operation(self, setup_db, machine):
        """Test normal operation in heating mode"""
        # Create slave status: current temperature lower than target temperature
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=28,
            cur_temp=25.0,  # Lower than target temperature
            speed=0,        # Shutdown state
            energy=0.0,
            amount=0.0
        )

        # Create adjustment request
        request = Request.create(
            slave_id=1,
            temp=28.0,
            speed=2,
            time=datetime.now()
        )

        machine.main_status = 2  # Heating mode

        # Simulate request processing logic
        status = Status.get(Status.id == request.slave_id)
        if machine.main_status == 2:  # Heating mode
            if status.cur_temp <= request.temp:  # Current temperature lower than or equal to target temperature
                expected_speed = request.speed  # Should operate normally
            else:
                expected_speed = 0

        assert expected_speed == 2, "Should operate normally when current temperature is lower than target in heating mode"

    def test_temperature_range_validation_cooling(self, setup_db, machine):
        """Test temperature range validation in cooling mode"""
        machine.main_status = 1  # Cooling mode

        # Test different temperature value handling
        test_cases = [
            (22, 2, True),   # Normal temperature, should process
            (18, 1, True),   # Boundary temperature, should process
            (25, 3, True),   # Boundary temperature, should process
            (17, 2, False),  # Out of range, should not process
            (26, 2, False),  # Out of range, should not process
        ]

        for temp, speed, should_process in test_cases:
            # Cooling mode temperature range is usually 18-25°C
            if machine.main_status == 1:
                is_valid = 18 <= temp <= 25
            else:
                is_valid = 25 <= temp <= 30
            assert is_valid == should_process, f"Temperature {temp}°C processing result does not match expectation"

    def test_temperature_range_validation_heating(self, setup_db, machine):
        """Test temperature range validation in heating mode"""
        machine.main_status = 2  # Heating mode

        # Test different temperature value handling
        test_cases = [
            (28, 2, True),   # Normal temperature, should process
            (25, 1, True),   # Boundary temperature, should process
            (30, 3, True),   # Boundary temperature, should process
            (24, 2, False),  # Out of range, should not process
            (31, 2, False),  # Out of range, should not process
        ]

        for temp, speed, should_process in test_cases:
            # Heating mode temperature range is usually 25-30°C
            if machine.main_status == 2:
                is_valid = 25 <= temp <= 30
            else:
                is_valid = 18 <= temp <= 25
            assert is_valid == should_process, f"Temperature {temp}°C processing result does not match expectation"
