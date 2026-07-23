import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import globalvar as gl
from rider import Rider
from order_model import Order

def test_order_completion():
    # Metric 8.1
    gl._init()
    rider = Rider(1)
    order = Order(res_pos=(100, 100), cus_pos=(200, 200))
    order.assign_to(rider.num)
    rider.orders.append(order)
    rider.state = 2 # Manually set to delivering
    rider.x, rider.y = 200, 200 # Manually set to customer location
    
    rider.move()
    
    assert rider.state == 0 # Rider should be idle
    assert not rider.orders # Order list should be empty
    assert order.status == "completed" # Order status should be completed