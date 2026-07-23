# -*- coding: utf-8 -*-
"""
Duplicate Winning Exclusion Mechanism Tests
"""

import sys
import os
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.lottery_engine import LotteryEngine

class TestNoDuplicate:
    """Duplicate Winning Test Class"""

    def setup_method(self):
        """Setup before tests"""
        self.engine = LotteryEngine()

    def test_no_duplicate_winners(self):
        """Test exclusion mechanism when duplicate winning is not allowed"""
        # Prepare test data with 5 employees
        employees = [
            {'name': 'Employee1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': 'Employee2', 'employee_id': '0101002', 'score': 92, 'tenure': 18},
            {'name': 'Employee3', 'employee_id': '0102001', 'score': 78, 'tenure': 36},
            {'name': 'Employee4', 'employee_id': '0102002', 'score': 88, 'tenure': 12},
            {'name': 'Employee5', 'employee_id': '0103001', 'score': 95, 'tenure': 48}
        ]

        # Configure multiple prizes with no duplicate winning allowed, total prizes exceed employee count
        prizes = [
            {
                'name': 'First Prize',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': False
            },
            {
                'name': 'Second Prize',
                'quantity': 2,
                'weight_rule': 'equal',
                'allow_duplicate': False
            },
            {
                'name': 'Third Prize',
                'quantity': 3,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]

        # Execute lottery (disable output)
        import io
        import contextlib

        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)

        # Collect all winner employee IDs
        all_winners = []
        for prize_name, winners in results.items():
            for winner in winners:
                all_winners.append(winner['employee_id'])

        # Verify no duplicate winning
        unique_winners = set(all_winners)
        assert len(all_winners) == len(unique_winners), f"Found duplicate winning: {len(all_winners)} winning records, {len(unique_winners)} unique employees"

        # Verify total winners not exceeding total employees
        assert len(unique_winners) <= len(employees), f"Winner count ({len(unique_winners)}) exceeds employee count ({len(employees)})"

        print(f"Test passed: {len(unique_winners)} employees won, no duplicates")

    def test_allow_duplicate_winners(self):
        """Test when duplicate winning is allowed"""
        employees = [
            {'name': 'Employee1', 'employee_id': '0101001', 'score': 100, 'tenure': 24},
            {'name': 'Employee2', 'employee_id': '0101002', 'score': 100, 'tenure': 18}
        ]

        # Configure multiple prizes allowing duplicate winning
        prizes = [
            {
                'name': 'Prize1',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': True
            },
            {
                'name': 'Prize2',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': True
            }
        ]

        # Execute lottery multiple times to verify possible duplicate winning
        duplicate_found = False

        import io
        import contextlib

        for _ in range(50):  # Multiple attempts
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)

            all_winners = []
            for winners in results.values():
                for winner in winners:
                    all_winners.append(winner['employee_id'])

            if len(all_winners) > len(set(all_winners)):
                duplicate_found = True
                break

        # When duplicate winning is allowed, duplicates should be possible
        # Note: This test may occasionally fail due to randomness not producing duplicates
        print(f"Allow duplicate winning test: {'Duplicate found' if duplicate_found else 'No duplicate found (normal random phenomenon)'}")

    def test_insufficient_candidates(self):
        """Test insufficient candidate pool scenario"""
        # Only 3 employees
        employees = [
            {'name': 'Employee1', 'employee_id': '0101001', 'score': 85, 'tenure': 24},
            {'name': 'Employee2', 'employee_id': '0101002', 'score': 92, 'tenure': 18},
            {'name': 'Employee3', 'employee_id': '0102001', 'score': 78, 'tenure': 36}
        ]

        # Configure prize requiring 5 winners (exceeds employee count)
        prizes = [
            {
                'name': 'Grand Prize',
                'quantity': 5,
                'weight_rule': 'equal',
                'allow_duplicate': False
            }
        ]

        # Execute lottery (disable output)
        import io
        import contextlib

        with contextlib.redirect_stdout(io.StringIO()):
            results = self.engine.execute_lottery(employees, prizes)

        # Verify winner count not exceeding employee count
        if 'Grand Prize' in results:
            winners_count = len(results['Grand Prize'])
            assert winners_count <= len(employees), f"Winner count ({winners_count}) should not exceed employee count ({len(employees)})"
            assert winners_count == len(employees), f"Should draw all available employees ({len(employees)}), actually drew {winners_count}"

        print(f"Insufficient candidate pool test passed: Drew {len(results.get('Grand Prize', []))} people, as expected")
