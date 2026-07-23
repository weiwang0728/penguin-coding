import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from lottery_engine import LotteryEngine
from participant_manager import ParticipantManager
from lottery_config import LotteryConfigManager
from result_manager import ResultManager
from models import Participant, LotteryRoundConfig
import tempfile

class TestLotteryEngine:
    def setup_method(self):
        """Setup executed before each test method runs"""
        # Create temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, "data")

        # Initialize each module
        self.participant_manager = ParticipantManager(data_dir=self.data_dir)
        self.config_manager = LotteryConfigManager(self.participant_manager, data_dir=self.data_dir)
        self.result_manager = ResultManager(data_dir=self.data_dir)
        self.lottery_engine = LotteryEngine(self.participant_manager, self.config_manager, self.result_manager)

        # Add test participants
        self.participant_manager.participants = [
            Participant(name="Zhang San", department="Technical Department", weight=1.0),
            Participant(name="Li Si", department="Technical Department", weight=1.0),
            Participant(name="Wang Wu", department="Marketing Department", weight=2.0),  # High weight
            Participant(name="Zhao Liu", department="Marketing Department", weight=1.0),
        ]

        # Add test round configurations
        self.config_manager.rounds = [
            LotteryRoundConfig(
                round_id="round_1",
                name="Test Round 1",
                draw_count=1,
                scope_type="all",
                scope_value="",
                allow_repeat=False,
                participant_weights={}
            ),
            LotteryRoundConfig(
                round_id="round_2",
                name="Test Round 2",
                draw_count=2,
                scope_type="all",
                scope_value="",
                allow_repeat=True,
                participant_weights={}
            )
        ]

    def teardown_method(self):
        """Cleanup executed after each test method runs"""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_weighted_probability(self):
        """Test weight application accuracy"""
        # Prepare a high weight participant
        round_config = LotteryRoundConfig(
            round_id="test_round",
            name="Weight Test",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )

        # Execute lottery multiple times
        high_weight_wins = 0
        total_runs = 1000

        for _ in range(total_runs):
            result = self.lottery_engine.execute_single_round(round_config)
            if result.winners[0]['name'] == "Wang Wu":  # Wang Wu weight is 2.0, others 1.0
                high_weight_wins += 1

        # Assert high weight participant wins significantly more often
        # Theoretically Wang Wu win probability is about 2/(1+1+2+1) = 2/5 = 0.4
        # Other participants win probability is about 1/5 = 0.2
        # We expect Wang Wu to win significantly more than others
        expected_high_weight_win_rate = 0.4
        actual_high_weight_win_rate = high_weight_wins / total_runs

        # Allow certain error range
        assert actual_high_weight_win_rate > expected_high_weight_win_rate * 0.8, \
            f"High weight participant win rate did not meet expectation: Expected > {expected_high_weight_win_rate * 0.8}, Actual {actual_high_weight_win_rate}"

        print(f"High weight participant win rate: {actual_high_weight_win_rate}")

    def test_no_repeat_logic(self):
        """Test duplicate win prevention logic"""
        # Configure two rounds of lottery, first round draws 1 person with 'no repeat win' mode
        round1_config = LotteryRoundConfig(
            round_id="round_1",
            name="First Round",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )

        # Second round draws remaining participants
        round2_config = LotteryRoundConfig(
            round_id="round_2",
            name="Second Round",
            draw_count=3,  # Draw the remaining 3 people
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )

        # Execute first round lottery
        result1 = self.lottery_engine.execute_single_round(round1_config)
        first_winner = result1.winners[0]['name']

        # Execute second round lottery, passing first round winners list
        result2 = self.lottery_engine.execute_single_round(round2_config, previous_winners=[first_winner])

        # Assert second round winners list does not contain first round winner
        second_winners = [winner['name'] for winner in result2.winners]
        assert first_winner not in second_winners, \
            f"No repeat win mode failed: First round winner {first_winner} appears in second round winners list"

        print(f"First round winner: {first_winner}")
        print(f"Second round winners: {second_winners}")
def test_weighted_probability():
    """Test weight application accuracy - standalone function version"""
    import tempfile
    import shutil

    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, "data")

    try:
        # Initialize each module
        participant_manager = ParticipantManager(data_dir=data_dir)
        config_manager = LotteryConfigManager(participant_manager, data_dir=data_dir)
        result_manager = ResultManager(data_dir=data_dir)
        lottery_engine = LotteryEngine(participant_manager, config_manager, result_manager)

        # Add test participants
        participant_manager.participants = [
            Participant(name="Zhang San", department="Technical Department", weight=1.0),
            Participant(name="Li Si", department="Technical Department", weight=1.0),
            Participant(name="Wang Wu", department="Marketing Department", weight=2.0),  # High weight
            Participant(name="Zhao Liu", department="Marketing Department", weight=1.0),
        ]

        # Prepare a high weight participant
        round_config = LotteryRoundConfig(
            round_id="test_round",
            name="Weight Test",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )

        # Execute lottery multiple times
        high_weight_wins = 0
        total_runs = 1000

        for _ in range(total_runs):
            result = lottery_engine.execute_single_round(round_config)
            if result.winners[0]['name'] == "Wang Wu":  # Wang Wu weight is 2.0, others 1.0
                high_weight_wins += 1

        # Assert high weight participant wins significantly more often
        # Theoretically Wang Wu win probability is about 2/(1+1+2+1) = 2/5 = 0.4
        # Other participants win probability is about 1/5 = 0.2
        # We expect Wang Wu to win significantly more than others
        expected_high_weight_win_rate = 0.4
        actual_high_weight_win_rate = high_weight_wins / total_runs

        # Allow certain error range
        assert actual_high_weight_win_rate > expected_high_weight_win_rate * 0.8, \
            f"High weight participant win rate did not meet expectation: Expected > {expected_high_weight_win_rate * 0.8}, Actual {actual_high_weight_win_rate}"

        print(f"High weight participant win rate: {actual_high_weight_win_rate}")

    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir, ignore_errors=True)
def test_no_repeat_logic():
    """Test duplicate win prevention logic - standalone function version"""
    import tempfile
    import shutil

    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, "data")

    try:
        # Initialize each module
        participant_manager = ParticipantManager(data_dir=data_dir)
        config_manager = LotteryConfigManager(participant_manager, data_dir=data_dir)
        result_manager = ResultManager(data_dir=data_dir)
        lottery_engine = LotteryEngine(participant_manager, config_manager, result_manager)

        # Add test participants
        participant_manager.participants = [
            Participant(name="Zhang San", department="Technical Department", weight=1.0),
            Participant(name="Li Si", department="Technical Department", weight=1.0),
            Participant(name="Wang Wu", department="Marketing Department", weight=2.0),
            Participant(name="Zhao Liu", department="Marketing Department", weight=1.0),
        ]

        # Configure two rounds of lottery, first round draws 1 person with 'no repeat win' mode
        round1_config = LotteryRoundConfig(
            round_id="round_1",
            name="First Round",
            draw_count=1,
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )

        # Second round draws remaining participants
        round2_config = LotteryRoundConfig(
            round_id="round_2",
            name="Second Round",
            draw_count=3,  # Draw the remaining 3 people
            scope_type="all",
            scope_value="",
            allow_repeat=False,
            participant_weights={}
        )

        # Execute first round lottery
        result1 = lottery_engine.execute_single_round(round1_config)
        first_winner = result1.winners[0]['name']

        # Execute second round lottery, passing first round winners list
        result2 = lottery_engine.execute_single_round(round2_config, previous_winners=[first_winner])

        # Assert second round winners list does not contain first round winner
        second_winners = [winner['name'] for winner in result2.winners]
        assert first_winner not in second_winners, \
            f"No repeat win mode failed: First round winner {first_winner} appears in second round winners list"

        print(f"First round winner: {first_winner}")
        print(f"Second round winners: {second_winners}")

    finally:
        # Clean up temporary directory
        shutil.rmtree(test_dir, ignore_errors=True)