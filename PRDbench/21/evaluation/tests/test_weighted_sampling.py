# -*- coding: utf-8 -*-
"""
Weighted Random Sampling Tests
"""

import sys
import os
import pytest
import numpy as np
from collections import Counter

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from modules.lottery_engine import LotteryEngine

class TestWeightedSampling:
    """Weighted Random Sampling Test Class"""

    def setup_method(self):
        """Setup before tests"""
        self.engine = LotteryEngine()

    def test_score_weighted_lottery(self):
        """Test score-weighted lottery"""
        # Prepare test data: distinct high-score and low-score employees
        employees = [
            {'name': 'HighScore1', 'employee_id': '0101001', 'score': 200, 'tenure': 24},
            {'name': 'HighScore2', 'employee_id': '0101002', 'score': 190, 'tenure': 18},
            {'name': 'HighScore3', 'employee_id': '0101003', 'score': 180, 'tenure': 36},
            {'name': 'LowScore1', 'employee_id': '0102001', 'score': 50, 'tenure': 12},
            {'name': 'LowScore2', 'employee_id': '0102002', 'score': 60, 'tenure': 30},
            {'name': 'LowScore3', 'employee_id': '0102003', 'score': 55, 'tenure': 15}
        ]

        # Configure score-weighted prize
        prizes = [
            {
                'name': 'Test Prize',
                'quantity': 1,
                'weight_rule': 'score',
                'allow_duplicate': True
            }
        ]

        # Execute multiple lotteries for statistics
        high_score_wins = 0
        low_score_wins = 0
        total_tests = 100

        # Temporarily disable print output
        import io
        import contextlib

        for _ in range(total_tests):
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            if 'Test Prize' in results and results['Test Prize']:
                winner = results['Test Prize'][0]
                if winner['score'] >= 180:
                    high_score_wins += 1
                elif winner['score'] <= 60:
                    low_score_wins += 1

        # Verify high-score employees win significantly more often than low-score employees
        high_score_rate = high_score_wins / total_tests
        low_score_rate = low_score_wins / total_tests

        print(f"High score employee win rate: {high_score_rate:.2%}")
        print(f"Low score employee win rate: {low_score_rate:.2%}")

        # Assertion: High-score employee win rate should be significantly higher than low-score
        # Considering randomness, require high-score win rate at least 1.5 times low-score
        assert high_score_rate > low_score_rate * 1.5, f"Weighting effect not obvious: high score {high_score_rate:.2%} vs low score {low_score_rate:.2%}"

    def test_equal_weight_lottery(self):
        """Test equal weight lottery"""
        employees = [
            {'name': 'Employee1', 'employee_id': '0101001', 'score': 100, 'tenure': 24},
            {'name': 'Employee2', 'employee_id': '0101002', 'score': 200, 'tenure': 18},
            {'name': 'Employee3', 'employee_id': '0101003', 'score': 50, 'tenure': 36}
        ]

        prizes = [
            {
                'name': 'Equal Weight Prize',
                'quantity': 1,
                'weight_rule': 'equal',
                'allow_duplicate': True
            }
        ]

        # Execute multiple lotteries to verify each employee has roughly equal winning probability
        win_counts = Counter()
        total_tests = 300

        import io
        import contextlib

        for _ in range(total_tests):
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            if 'Equal Weight Prize' in results and results['Equal Weight Prize']:
                winner_id = results['Equal Weight Prize'][0]['employee_id']
                win_counts[winner_id] += 1

        # Verify each employee's win count is roughly equal (allow 35% deviation)
        expected_wins = total_tests / len(employees)
        for emp_id, wins in win_counts.items():
            deviation = abs(wins - expected_wins) / expected_wins
            print(f"Employee {emp_id}: {wins} times (expected {expected_wins:.1f} times, deviation {deviation:.1%})")
            assert deviation < 0.35, f"Employee {emp_id} win count deviation too large: {wins} vs expected {expected_wins:.1f}"

    def test_tenure_weighted_lottery(self):
        """Test tenure-weighted lottery"""
        employees = [
            {'name': 'OldEmployee1', 'employee_id': '0101001', 'score': 100, 'tenure': 60},
            {'name': 'OldEmployee2', 'employee_id': '0101002', 'score': 100, 'tenure': 48},
            {'name': 'NewEmployee1', 'employee_id': '0102001', 'score': 100, 'tenure': 6},
            {'name': 'NewEmployee2', 'employee_id': '0102002', 'score': 100, 'tenure': 12}
        ]

        prizes = [
            {
                'name': 'Tenure Prize',
                'quantity': 1,
                'weight_rule': 'tenure',
                'allow_duplicate': True
            }
        ]

        # Execute multiple lotteries for statistics
        old_employee_wins = 0
        new_employee_wins = 0
        total_tests = 100

        import io
        import contextlib

        for _ in range(total_tests):
            with contextlib.redirect_stdout(io.StringIO()):
                results = self.engine.execute_lottery(employees, prizes)
            if 'Tenure Prize' in results and results['Tenure Prize']:
                winner = results['Tenure Prize'][0]
                if winner['tenure'] >= 48:
                    old_employee_wins += 1
                elif winner['tenure'] <= 12:
                    new_employee_wins += 1

        # Verify old employees win more often than new employees
        old_rate = old_employee_wins / total_tests
        new_rate = new_employee_wins / total_tests

        print(f"Old employee win rate: {old_rate:.2%}")
        print(f"New employee win rate: {new_rate:.2%}")

        assert old_rate > new_rate * 1.2, f"Tenure weighting effect not obvious: old employees {old_rate:.2%} vs new employees {new_rate:.2%}"
