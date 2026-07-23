import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import globalvar as gl
from rider import Rider
from order_model import Order

def test_rider_history():
    # Metrics 6.3a, 6.3b
    gl._init()
    rider = Rider(1)
    order = Order(res_pos=(100, 100), cus_pos=(200, 200))
    
    # Assign order and transition states
    rider.orders.append(order)
    rider.move() # idle -> to_pickup
    rider.x, rider.y = 100, 100
    rider.move() # to_pickup -> to_deliver
    rider.x, rider.y = 200, 200
    rider.move() # to_deliver -> idle
    
    assert len(rider.log) >= 4 # spawn, accepted, arrived_at_merchant, delivered
    
    events = [log['event'] for log in rider.log]
    assert "spawn" in events
    assert "accepted_order" in events
    assert "arrived_at_merchant" in events
    assert "delivered_to_customer" in events
    
    # Check details of one log entry
    accepted_log = next(log for log in rider.log if log['event'] == 'accepted_order')
    assert accepted_log['order_id'] == order.id