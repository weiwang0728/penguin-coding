import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import globalvar as gl
from rider import Rider
from order_model import Order

def test_rider_state_transition():
    # Metric 4.2
    gl._init()
    rider = Rider(1)
    order = Order(res_pos=(100, 100), cus_pos=(200, 200))
    rider.orders.append(order)
    
    # Initial state should be 0 (idle)
    assert rider.state == 0
    
    # After first move, state should be 1 (to_pickup)
    rider.move()
    assert rider.state == 1
    
    # Move rider to restaurant
    rider.x, rider.y = 100, 100
    rider.move()
    # Now state should be 2 (to_deliver)
    assert rider.state == 2
    
    # Move rider to customer
    rider.x, rider.y = 200, 200
    rider.move()
    # Now state should be 0 (idle)
    assert rider.state == 0
    assert not rider.orders # Order should be completed and removed