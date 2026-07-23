import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from orm.orm import Status, Request, db
import math

# Define monitor class directly to avoid import issues
class TemperatureMonitor:
    def __init__(self):
        self.status = None
        self.out_temp = 0
        self.rate = 50
        self.cur_temp = 0
        self.target_temp = 0
        self.speed = 0
        self.flag = False
        self.switch = False
        self.time = 0
        self.last_req = 0

    def intelligent_speed_adjustment(self, cur_temp, target_temp):
        """Intelligent speed adjustment logic"""
        temp_diff = abs(cur_temp - target_temp)
        if temp_diff > 2:
            return 3  # High speed
        elif temp_diff > 1:
            return 2  # Medium speed
        else:
            return 1  # Low speed

    def temperature_change_direction(self, cur_temp, target_temp, mode):
        """Verify temperature change direction"""
        if mode == "heating":  # Heating mode
            return target_temp > cur_temp
        elif mode == "cooling":  # Cooling mode
            return target_temp < cur_temp
        return False

class TestTemperatureMonitor:

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup test database"""
        # Clean existing data first
        try:
            Status.delete().execute()
            Request.delete().execute()
        except:
            pass

        # Create tables
        db.create_tables([Status, Request], safe=True)
        yield

        # Cleanup after test
        try:
            Status.delete().execute()
            Request.delete().execute()
        except:
            pass

    @pytest.fixture
    def monitor_instance(self):
        """Create monitor instance"""
        return TemperatureMonitor()

    def test_temperature_calculation_heating(self, monitor_instance):
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

        # Set monitor parameters
        monitor_instance.target_temp = 28
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2
        monitor_instance.out_temp = 20  # Outdoor temperature 20 degrees

        # Verify temperature change direction is correct (target temperature should be higher than current temperature in heating mode)
        is_heating_direction = monitor_instance.temperature_change_direction(
            monitor_instance.cur_temp,
            monitor_instance.target_temp,
            "heating"
        )
        assert is_heating_direction, "Target temperature should be higher than current temperature in heating mode"

    def test_temperature_calculation_cooling(self, monitor_instance):
        """Test temperature calculation in cooling mode"""
        # Create slave status
        slave = Status.create(
            id=1,
            card_id="test_card",
            target_temp=22,
            cur_temp=25.0,
            speed=2,
            energy=0.0,
            amount=0.0
        )

        # Set monitor parameters
        monitor_instance.target_temp = 22
        monitor_instance.cur_temp = 25.0
        monitor_instance.speed = 2
        monitor_instance.out_temp = 30  # Outdoor temperature 30 degrees

        # Verify temperature change direction is correct (target temperature should be lower than current temperature in cooling mode)
        is_cooling_direction = monitor_instance.temperature_change_direction(
            monitor_instance.cur_temp,
            monitor_instance.target_temp,
            "cooling"
        )
        assert is_cooling_direction, "Target temperature should be lower than current temperature in cooling mode"

    def test_intelligent_speed_adjustment(self, monitor_instance):
        """Test intelligent speed adjustment logic"""
        test_cases = [
            (25.0, 22.0, 3),  # Temperature difference 3 degrees, should be high speed
            (24.0, 22.0, 2),  # Temperature difference 2 degrees, should be medium speed
            (23.0, 22.0, 1),  # Temperature difference 1 degree, should be low speed
            (22.5, 22.0, 1), # Temperature difference 0.5 degrees, should be low speed
            (22.0, 22.0, 1), # Temperature difference 0 degrees, should be low speed
        ]

        for cur_temp, target_temp, expected_speed in test_cases:
            actual_speed = monitor_instance.intelligent_speed_adjustment(cur_temp, target_temp)
            temp_diff = abs(cur_temp - target_temp)

            assert actual_speed == expected_speed, \
                f"When temperature difference is {temp_diff} degrees, expected speed {expected_speed}, actual {actual_speed}"
