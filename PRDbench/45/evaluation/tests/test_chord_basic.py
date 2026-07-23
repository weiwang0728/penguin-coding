"""
Basic Chord DHT Algorithm Unit Tests
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from Node import Node
from Network import Network


def test_node_initialization():
    """Test node initialization"""
    Node.m = 4
    Node.ring_size = 16
    node = Node(5, 4)

    assert node.node_id == 5
    assert node.predecessor == node
    assert node.successor == node
    assert len(node.fingers_table) == 4
    assert isinstance(node.data, dict)


def test_network_initialization():
    """Test network initialization"""
    m = 4
    node_ids = [0, 4, 8, 12]
    network = Network(m, node_ids)

    assert network.m == 4
    assert network.ring_size == 16
    assert len(network.nodes) == 1  # Only first node is initialized
    assert network.first_node.node_id == 0


def test_hash_function():
    """Test hash function"""
    m = 4
    network = Network(m, [0])

    # Test same input produces same hash value
    hash1 = network.hash_function("test_data")
    hash2 = network.hash_function("test_data")
    assert hash1 == hash2

    # Test hash value is within valid range
    assert 0 <= hash1 < 2**m


def test_node_distance_calculation():
    """Test node distance calculation"""
    Node.m = 4
    Node.ring_size = 16
    node = Node(5, 4)

    # Test clockwise distance
    assert node.distance(5, 8) == 3
    # Test circular distance
    assert node.distance(12, 3) == 7


def test_finger_table_size():
    """Test finger table size"""
    Node.m = 6
    Node.ring_size = 64
    node = Node(10, 6)

    assert len(node.fingers_table) == 6
    # Initially all fingers point to itself
    for finger in node.fingers_table:
        assert finger == node


if __name__ == "__main__":
    pytest.main([__file__])
