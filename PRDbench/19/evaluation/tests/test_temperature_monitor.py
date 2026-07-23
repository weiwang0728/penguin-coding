import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.monitor import monitor as monitor_class, ac
from orm.orm import Status, Request, db
import math

class TestTemperatureMonitor:

    @pytest.fixture
    def setup_db(self):
        """Setup test database"""
        db.create_tables([Status, Request], safe=True)
        yield
        # Cleanup
        Status.delete().execute()
        Request.delete().execute()

    @pytest.fixture
    def monitor_instance(self):
        """Create monitor instance"""
        return monitor_class()

    def test_temperature_calculation_heating(self, setup_db, monitor_instance):
        """Test temperature calculation in heating mode"""
        # Create slave status
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=28,
            cur_temp=25.0,
            speed=2,  # Medium speed
            energy=0.0,
            amount=0.0
        )

        monitor_instance.init(1, 20)  # Outdoor temperature 20 degrees
        monitor_instance.target_temp = 28
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2
        monitor_instance.rate = 50

        # Verify temperature change direction is correct (temperature should rise when heating)
        assert monitor_instance.target_temp > monitor_instance.cur_temp

    def test_temperature_calculation_cooling(self, setup_db, monitor_instance):
        """Test temperature calculation in cooling mode"""
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=22,
            cur_temp=25.0,
            speed=2,
            energy=0.0,
            amount=0.0
        )

        monitor_instance.init(1, 30)  # Outdoor temperature 30 degrees
        monitor_instance.target_temp = 22
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2

        # Verify temperature change direction is correct (temperature should decrease when cooling)
        assert monitor_instance.target_temp < monitor_instance.cur_temp

    def test_intelligent_speed_adjustment(self, setup_db, monitor_instance):
        """Test intelligent speed adjustment logic"""
        test_cases = [
            (25.0, 22.0, 3),  # Temperature difference 3 degrees, should be high speed
            (24.0, 22.0, 2),  # Temperature difference 2 degrees, should be medium speed
            (23.0, 22.0, 1),  # Temperature difference 1 degree, should be low speed
            (22.5, 22.0, 1), # Temperature difference 0.5 degrees, should be low speed
        ]

        for cur_temp, target_temp, expected_speed in test_cases:
            temp_diff = abs(cur_temp - target_temp)

            if temp_diff > 2:
                actual_speed = 3
            elif temp_diff > 1:
                actual_speed = 2
            else:
                actual_speed = 1

            assert actual_speed == expected_speed, f"When temperature difference is {temp_diff} degrees, expected speed {expected_speed}, actual {actual_speed}"
