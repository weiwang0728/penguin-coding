import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import globalvar as gl
from rider import Rider
from order_model import Order

def test_rider_movement():
    # Metric 5.2
    gl._init()
    rider = Rider(1)
    rider.x, rider.y = 0, 0
    order = Order(res_pos=(100, 100), cus_pos=(200, 200))
    rider.orders.append(order)
    
    rider.move() # State becomes 1
    
    # Move towards restaurant
    rider.move()
    assert rider.y == 20
    assert rider.x == 0