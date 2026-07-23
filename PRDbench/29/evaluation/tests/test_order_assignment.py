import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import globalvar as gl
from rider import Rider
from order_model import Order
from order import find_best_rider_for_order

def test_find_best_rider_for_order():
    # Metric 4.1
    gl._init()
    
    rider1 = Rider(1)
    rider1.x, rider1.y = 100, 100
    
    rider2 = Rider(2)
    rider2.x, rider2.y = 500, 500
    
    gl.set_value('riders', [rider1, rider2])
    
    order = Order(res_pos=(150, 150), cus_pos=(200, 200))
    
    best_rider = find_best_rider_for_order(order)
    
    assert best_rider.num == 1, "Failed to assign order to the nearest rider"