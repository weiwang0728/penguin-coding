import sys
import os
# Add src directory to Python path for module import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from lottery_system.models import User, Prize
from lottery_system.services.lottery_manager import LotteryManager


def test_chenru_group_guarantee_mechanism():
    """
    Test Chengru Group guarantee mechanism:
    When Ma Jiaqi draws and the first two rounds have no Chengru Group members winning,
    the prize pool should be forcibly limited to Chengru Group members, even if the prize has avoid settings for Chengru Group.
    """
    # Prepare test data: Create users including Chengru Group and other groups
    users = [
        User("Zhang San", "Tech Department"),
        User("Li Si", "Product Department"),
        User("Wang Wu", "Marketing Department"),
        User("Cheng Ru", "Chengru Group"),
        User("Chen Qixian", "Chengru Group"),
        User("Jin Duo", "Chengru Group")
    ]

    # Create lottery manager instance
    lottery_manager = LotteryManager(users)

    # Simulate the first two draws with no Chengru Group members winning
    lottery_manager.last_two_draw_results = [False, False]

    # Create a prize drawn by "Ma Jiaqi" and avoiding "Chengru Group"
    prize_majiaqi = Prize(
        name="Test Prize C",
        quantity=1,
        avoid_groups=["Chengru Group"],  # Set to avoid Chengru Group
        associated_drawer="Ma Jiaqi"
    )

    # Get eligible prize pool
    eligible_pool = lottery_manager._get_eligible_pool(prize_majiaqi)

    # Assert: Despite the prize avoiding Chengru Group, due to guarantee mechanism,
    # the pool should only contain Chengru Group members
    assert len(eligible_pool) == 3  # Should have 3 Chengru Group members
    assert all(user.department == "Chengru Group" for user in eligible_pool)

    # Verify returned user list
    expected_names = {"Cheng Ru", "Chen Qixian", "Jin Duo"}
    actual_names = {user.name for user in eligible_pool}
    assert actual_names == expected_names


def test_chenru_group_guarantee_not_triggered():
    """
    Test Chengru Group guarantee mechanism not being triggered:
    When previous draws have Chengru Group members winning, guarantee mechanism should not be triggered.
    """
    users = [
        User("Zhang San", "Tech Department"),
        User("Cheng Ru", "Chengru Group")
    ]

    lottery_manager = LotteryManager(users)

    # Simulate previous two draws with Chengru Group members winning
    lottery_manager.last_two_draw_results = [False, True]  # Second draw has Chengru Group winning

    # Create prize drawn by "Ma Jiaqi" and avoiding "Chengru Group"
    prize_majiaqi = Prize(
        name="Test Prize",
        quantity=1,
        avoid_groups=["Chengru Group"],
        associated_drawer="Ma Jiaqi"
    )

    # Get eligible prize pool
    eligible_pool = lottery_manager._get_eligible_pool(prize_majiaqi)

    # Assert: Guarantee mechanism not triggered, avoidance rules take effect normally
    # Should only have Zhang San from Tech Department eligible
    assert len(eligible_pool) == 1
    assert eligible_pool[0].name == "Zhang San"
    assert eligible_pool[0].department == "Tech Department"


def test_chenru_group_guarantee_no_chenru_members():
    """
    Test guarantee mechanism behavior when there are no Chengru Group members.
    """
    users = [
        User("Zhang San", "Tech Department"),
        User("Li Si", "Product Department")
    ]

    lottery_manager = LotteryManager(users)
    lottery_manager.last_two_draw_results = [False, False]

    prize_majiaqi = Prize(
        name="Test Prize",
        quantity=1,
        avoid_groups=[],
        associated_drawer="Ma Jiaqi"
    )

    eligible_pool = lottery_manager._get_eligible_pool(prize_majiaqi)

    # Assert: Since there are no Chengru Group members, guarantee mechanism does not take effect,
    # returns normal prize pool
    assert len(eligible_pool) == 2
    expected_names = {"Zhang San", "Li Si"}
    actual_names = {user.name for user in eligible_pool}
    assert actual_names == expected_names