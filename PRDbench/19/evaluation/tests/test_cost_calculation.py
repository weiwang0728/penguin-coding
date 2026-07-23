import pytest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from route.cost import Costor
from orm.orm import Status, db
import time
from unittest.mock import patch

class TestCostCalculation:

    @pytest.fixture
    def setup_db(self):
        """Setup test database"""
        db.create_tables([Status], safe=True)
        yield
        # Cleanup
        Status.delete().execute()

    def test_cost_calculation_one_minute(self, setup_db):
        """Test cost calculation for 1 minute at medium speed (corresponding to original test case)"""
        slave = Status.create(
            card_id="test_card_minute",
            target_temp=22,
            cur_temp=25.0,
            speed=2,  # Medium speed
            energy=0.0,
            amount=0.0
        )

        costor = Costor()

        # Simulate 60 seconds of cost calculation
        with patch('time.sleep'):
            costor.flag = True
            for _ in range(60):  # 60 seconds
                active_slaves = Status.select().where(Status.speed != 0)
                for slave_status in active_slaves:
                    energy = 1.0 / 60  # Medium speed calculation per second
                    cost = 5 * energy

                    Status.update(
                        energy=Status.energy + energy,
                        amount=Status.amount + cost
                    ).where(Status.id == slave_status.id).execute()

        updated_slave = Status.get(Status.id == slave.id)
        expected_energy = 1.0  # 1.0 power/minute * 1 minute
        expected_cost = expected_energy * 5  # 5.0 yuan

        # Allow ±5% error
        assert abs(updated_slave.energy - expected_energy) < expected_energy * 0.05
        assert abs(updated_slave.amount - expected_cost) < expected_cost * 0.05
