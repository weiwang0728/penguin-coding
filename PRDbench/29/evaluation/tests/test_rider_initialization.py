import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import pytest
from rider import Rider
import system
import globalvar as gl

# Test case for rider's initial position
def test_rider_initial_position():
    """
    Tests the initial position of a newly created rider.
    """
    system.init_system() # Reset global state and create initial rider
    rider = gl.get_value('riders')[0] # Get the first rider created by init_system
    # By default, a rider should be at (435, 385) as per current Rider class
    assert rider.x == 435 and rider.y == 385

# Test case for rider's initial speed
def test_rider_initial_speed():
    """
    Tests the initial speed of a newly created rider.
    """
    system.init_system() # Reset global state and create initial rider
    rider = gl.get_value('riders')[0] # Get the first rider created by init_system
    # By default, a rider should have a speed of 10 as per current Rider class
    assert rider.speed == 10

# Test case for rider's initial state
def test_rider_initial_state():
    """
    Tests the initial state of a newly created rider.
    """
    system.init_system() # Reset global state and create initial rider
    rider = gl.get_value('riders')[0] # Get the first rider created by init_system
    # By default, a rider should be idle (state 0) as per current Rider class
    assert rider.state == 0
