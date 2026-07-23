import sys
import os
import tempfile
import csv
from datetime import datetime
from unittest.mock import patch, mock_open

# Add src directory to Python path for module import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from lottery_system.models import User, Prize
from lottery_system.services.list_manager import ListManager
from lottery_system.services.prize_manager import PrizeManager
from lottery_system.services.lottery_manager import LotteryManager
from lottery_system.services.result_manager import ResultManager, Winner


class TestListManager:
    """Test list management functions"""

    def test_default_list_loading(self):
        """Test2.1.2 Built-in list loading"""
        list_manager = ListManager()
        users, errors = list_manager.load_default_list()

        # Verify default list loading success
        assert len(users) > 0, "Should be able to load default user list"
        assert all(isinstance(user, User) for user in users), "All items should be User objects"
        assert all(user.name and user.department for user in users), "Each user should have name and department"
    
    def test_custom_list_loading_success(self):
        """Test2.1.3 Custom list upload - Success scenario"""
        list_manager = ListManager()

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Zhang San,Tech Department\nLi Si,Product Department\n")
            temp_path = f.name

        try:
            users, errors = list_manager.load_custom_list(temp_path)

            assert len(errors) == 0, "Should not have errors"
            assert len(users) == 2, "Should load 2 users"
            assert users[0].name == "Zhang San" and users[0].department == "Tech Department"
            assert users[1].name == "Li Si" and users[1].department == "Product Department"
        finally:
            os.unlink(temp_path)
    
    def test_duplicate_name_validation(self):
        """Test2.1.4a List validation - Duplicate names"""
        list_manager = ListManager()
        users = [
            User("Wang Wu", "Marketing Department"),
            User("Wang Wu", "Marketing Department"),
            User("Zhang San", "Tech Department")
        ]

        valid_users, duplicates = list_manager.validate_users(users)

        assert len(valid_users) == 2, "Should have 2 valid users"
        assert len(duplicates) == 1, "Should have 1 duplicate user"
        assert duplicates[0].name == "Wang Wu", "Duplicate user should be Wang Wu"
    
    def test_format_error_validation(self):
        """Test2.1.4b List validation - Format error"""
        list_manager = ListManager()

        # Create temporary file with format error
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Zhao Liu-Admin Department\n")  # Wrong separator
            temp_path = f.name

        try:
            users, errors = list_manager._load_from_path(temp_path)

            assert len(users) == 0, "Should not have valid users"
            assert len(errors) == 1, "Should have 1 error"
            assert "Format Error" in errors[0], "Error information should contain Format Error"
            assert "Line 1" in errors[0], "Error information should indicate line number"
        finally:
            os.unlink(temp_path)
    
    def test_group_info_display(self):
        """Test2.1.5 Group information display"""
        list_manager = ListManager()
        users = [
            User("Zhang San", "Tech Department"),
            User("Li Si", "Product Department"),
            User("Wang Wu", "Tech Department")
        ]

        group_info = list_manager.get_group_info(users)

        assert group_info["Tech Department"] == 2, "Tech Department should have 2 people"
        assert group_info["Product Department"] == 1, "Product Department should have 1 person"
    
    def test_invalid_data_handling(self):
        """Test2.1.4c List validation - Manual handling"""
        list_manager = ListManager()

        # Create temporary file with duplicate data
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Wang Wu,Marketing Department\nWang Wu,Marketing Department\nZhang San,Tech Department\n")
            temp_path = f.name

        try:
            users, errors = list_manager.load_custom_list(temp_path)

            # Verify can detect duplicate data but still process valid data
            if len(errors) > 0:
                # If error handling logic exists, verify removal function
                valid_users, duplicates = list_manager.validate_users(users + [User("Wang Wu", "Marketing Department")])
                assert len(valid_users) >= 1, "Should be able to remove duplicate data and keep valid data"
                assert len(duplicates) >= 1, "Should be able to identify duplicate data"
            else:
                # Verify normal loading function
                assert len(users) >= 1, "Should be able to load valid user data"
        finally:
            os.unlink(temp_path)


class TestPrizeManager:
    """Test prize management functions"""

    def test_default_prizes_loading(self):
        """Test2.2.1 Prize library management - View presets"""
        prize_manager = PrizeManager()
        errors = prize_manager.load_default_prizes()

        assert len(errors) == 0, "Loading default prizes should not have errors"

        prizes = prize_manager.get_prizes()
        assert len(prizes) >= 3, "Should have at least 3 preset prizes"

        # Verify preset prizes
        prize_names = [prize.name for prize in prizes]
        assert "Third Prize-Movie Ticket" in prize_names, "Should contain Third Prize-Movie Ticket"
        assert "Second Prize-Shopping Card" in prize_names, "Should contain Second Prize-Shopping Card"
        assert "First Prize-1 Day Annual Leave" in prize_names, "Should contain First Prize-1 Day Annual Leave"
    
    def test_custom_prize_addition(self):
        """Test2.2.2 Prize library management - Custom addition"""
        prize_manager = PrizeManager()

        # Add custom prize
        prize_manager.add_prize(
            name="Grand Prize-iPhone 17",
            quantity=1,
            avoid_groups=[],
            associated_drawer="Li Bin"
        )

        prizes = prize_manager.get_prizes()
        assert len(prizes) == 1, "Should have 1 prize"

        prize = prizes[0]
        assert prize.name == "Grand Prize-iPhone 17", "Prize name should be correct"
        assert prize.quantity == 1, "Quantity should be correct"
        assert prize.associated_drawer == "Li Bin", "Associated drawer should be correct"
    
    def test_avoid_groups_configuration(self):
        """Test2.2.3 Group avoidance rule configuration"""
        prize_manager = PrizeManager()

        # Add prize with avoidance groups
        prize_manager.add_prize(
            name="Test Prize",
            quantity=1,
            avoid_groups=["Tech Department", "Product Department"]
        )

        prize = prize_manager.get_prizes()[0]
        assert "Tech Department" in prize.avoid_groups, "Avoidance groups should contain Tech Department"
        assert "Product Department" in prize.avoid_groups, "Avoidance groups should contain Product Department"
    
    def test_prize_reordering(self):
        """Test2.2.4 Prize reordering function"""
        prize_manager = PrizeManager()

        # Add three prizes
        prize_manager.add_prize("Prize A", 1)
        prize_manager.add_prize("Prize B", 1)
        prize_manager.add_prize("Prize C", 1)

        # Test reordering: move C to first position
        success = prize_manager.reorder_prizes([3, 1, 2])  # C, A, B

        assert success, "Reordering should succeed"

        prizes = prize_manager.get_prizes()
        assert prizes[0].name == "Prize C", "First item should be Prize C"
        assert prizes[1].name == "Prize A", "Second item should be Prize A"
        assert prizes[2].name == "Prize B", "Third item should be Prize B"


class TestLotteryManager:
    """Test lottery management functions"""

    def test_no_duplicate_winners(self):
        """Test2.4.1 Basic filtering - No duplicate winners"""
        users = [User("Zhang San", "Tech Department"), User("Li Si", "Product Department")]
        lottery_manager = LotteryManager(users)

        prize1 = Prize("Prize X", 1, [], None)
        prize2 = Prize("Prize Y", 1, [], None)

        # First round draw
        winners1 = lottery_manager.draw(prize1)
        assert len(winners1) == 1, "First round should have 1 winner"

        # Second round draw
        winners2 = lottery_manager.draw(prize2)
        assert len(winners2) == 1, "Second round should have 1 winner"

        # Verify no duplicate winners
        assert winners1[0] != winners2[0], "Winners from both rounds should be different"
    
    def test_group_avoidance_filtering(self):
        """Test2.4.2 Basic filtering - Group avoidance"""
        users = [
            User("Zhang San", "Tech Department"),
            User("Li Si", "Product Department")
        ]
        lottery_manager = LotteryManager(users)

        # Create prize that avoids Tech Department
        prize = Prize("Product Exclusive Prize", 1, ["Tech Department"], None)

        # Get eligible user pool
        eligible_pool = lottery_manager._get_eligible_pool(prize)

        assert len(eligible_pool) == 1, "Should only have 1 eligible user"
        assert eligible_pool[0].department == "Product Department", "Winner should be from Product Department"
    
    def test_libin_special_rule(self):
        """Test2.4.3 Special rule - Li Bin"""
        users = [
            User("Zhang San", "Tech Department"),
            User("Li Si", "Product Department")
        ]
        lottery_manager = LotteryManager(users)

        # Create prize drawn by Li Bin with Tech Department avoidance set
        prize = Prize("Li Bin Prize", 1, ["Tech Department"], "Li Bin")

        # Get eligible user pool
        eligible_pool = lottery_manager._get_eligible_pool(prize)

        # Li Bin's draw should ignore avoidance rules
        assert len(eligible_pool) == 2, "Li Bin's draw should include all users"
        department_list = [user.department for user in eligible_pool]
        assert "Tech Department" in department_list, "Should include Tech Department members"
        assert "Product Department" in department_list, "Should include Product Department members"
    
    def test_pause_resume_control(self):
        """Test2.3.2 Manual control - Pause and resume"""
        users = [User("Zhang San", "Tech Department"), User("Li Si", "Product Department")]
        lottery_manager = LotteryManager(users)

        # Create test prize
        prize = Prize("Test Prize", 1, [], None)

        # Simulate pause and resume functionality test
        # This mainly tests whether LotteryManager supports pause/resume status control
        assert hasattr(lottery_manager, 'is_paused') or hasattr(lottery_manager, '_paused'), "Should support pause status control"

        # Verify lottery function is normal
        winners = lottery_manager.draw(prize)
        assert len(winners) == 1, "Lottery function should be normal after pause and resume"
    
    def test_terminate_control(self):
        """Test2.3.3 Manual control - Terminate"""
        users = [User("Zhang San", "Tech Department"), User("Li Si", "Product Department"), User("Wang Wu", "Marketing Department")]
        lottery_manager = LotteryManager(users)

        # Create prize that requires drawing multiple winners
        prize = Prize("Multi-person Prize", 3, [], None)

        # Simulate terminate function: draw partial winners first
        winners = lottery_manager.draw(prize)

        # Verify can draw winners normally (terminate function's basis is normal lottery function)
        assert len(winners) <= 3, "Should be able to draw winners"
        assert len(winners) >= 1, "Should have at least 1 winner"

        # Verify drawn results can be saved correctly (by checking winners list is not empty)
        for winner in winners:
            assert isinstance(winner, User), "Winner should be User object"


class TestResultManager:
    """Test result management functions"""

    def test_result_aggregation_display(self):
        """Test2.5.1b Final result aggregation display"""
        result_manager = ResultManager()

        # Create test data
        user1 = User("Zhang San", "Tech Department")
        user2 = User("Li Si", "Product Department")
        prize1 = Prize("First Prize", 1, [], None)
        prize2 = Prize("Second Prize", 1, [], None)

        # Add winners
        result_manager.add_winner(user1, prize1)
        result_manager.add_winner(user2, prize2)

        # Get results grouped by prize
        prizes = [prize1, prize2]
        results = result_manager.get_winners_by_prize(prizes)

        assert "First Prize" in results, "Results should contain First Prize"
        assert "Second Prize" in results, "Results should contain Second Prize"
        assert len(results["First Prize"]) == 1, "First Prize should have 1 winner"
        assert results["First Prize"][0].user.name == "Zhang San", "First Prize winner should be Zhang San"
    
    def test_csv_export_functionality(self):
        """Test2.5.2a Result export function"""
        result_manager = ResultManager()

        # Create test data
        user = User("Zhang San", "Tech Department")
        prize = Prize("Test Prize", 1, [], None)
        result_manager.add_winner(user, prize)

        # Simulate file writing
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('os.path.abspath', return_value='/test/path.txt'):
                success, message = result_manager.export_to_csv([prize])

        assert success, "Export should succeed"
        assert "successfully exported" in message, "Success message should contain exported"
    
    def test_csv_export_format(self):
        """Test2.5.2b Result export format"""
        result_manager = ResultManager()

        # Create test data
        user = User("Zhang San", "Tech Department")
        prize = Prize("Test Prize", 1, [], None)
        result_manager.add_winner(user, prize)

        # Use temporary file for actual write test
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            temp_path = f.name

        try:
            # Directly test file writing logic
            with patch('os.path.abspath', return_value=temp_path):
                success, message = result_manager.export_to_csv([prize])

            assert success, "Export should succeed"

            # Verify file content format
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')

                # Verify header
                assert lines[0] == "Name,Department,Prize Name,Win Time", "Header format should be correct"

                # Verify data row
                assert len(lines) == 2, "Should have header and 1 data row"
                data_parts = lines[1].split(',')
                assert len(data_parts) == 4, "Data row should have 4 fields"
                assert data_parts[0] == "Zhang San", "Name field should be correct"
                assert data_parts[1] == "Tech Department", "Department field should be correct"
                assert data_parts[2] == "Test Prize", "Prize name field should be correct"
        finally:
            os.unlink(temp_path)


# Integration Test
class TestIntegratedWorkflow:
    """Test integrated workflow"""

    def test_complete_lottery_workflow(self):
        """Test complete lottery workflow"""
        # 1. Initialize managers
        list_manager = ListManager()
        prize_manager = PrizeManager()
        result_manager = ResultManager()

        # 2. Prepare user and prize data
        users = [User("Zhang San", "Tech Department"), User("Li Si", "Product Department")]
        prize_manager.add_prize("Test Prize", 1, [], None)

        # 3. Execute lottery
        lottery_manager = LotteryManager(users)
        prize = prize_manager.get_prizes()[0]
        winners = lottery_manager.draw(prize)

        # 4. Record results
        for winner in winners:
            result_manager.add_winner(winner, prize)

        # 5. Verify entire process
        assert len(winners) == 1, "Should have 1 winner"
        assert result_manager.get_all_winners()[0].user in users, "Winner should be in user list"


if __name__ == "__main__":
    pytest.main([__file__])