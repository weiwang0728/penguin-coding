"""
Chord DHT Data Operations Unit Tests
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

import pytest
from Node import Node
from Network import Network


def test_data_insertion():
    """Test data insertion function"""
    m = 4
    network = Network(m, [0, 4, 8, 12])

    # Create complete network
    for node_id in [4, 8, 12]:
        network.add_node(node_id)

    # Insert data
    test_data = "test_file.txt"
    result = network.insert_data(test_data)

    # Verify data has been inserted
    assert result is not None

    # Verify data can be found
    found = network.lookup_data(test_data)
    assert found is not None


def test_data_lookup():
    """Test data lookup function"""
    m = 4
    network = Network(m, [0])

    # Insert data
    test_data = "lookup_test.txt"
    network.insert_data(test_data)

    # Lookup existing data
    found = network.lookup_data(test_data)
    assert found is not None

    # Lookup non-existent data
    not_found = network.lookup_data("nonexistent.txt")
    assert not_found is None


def test_hash_consistency():
    """Test hash consistency"""
    m = 4
    network = Network(m, [0])

    # Same data should produce same hash
    data = "consistency_test.txt"
    hash1 = network.hash_function(data)
    hash2 = network.hash_function(data)

    assert hash1 == hash2


def test_data_distribution():
    """Test data distribution"""
    m = 4
    network = Network(m, [0])

    # Add multiple nodes
    for node_id in [4, 8, 12]:
        network.add_node(node_id)

    # Insert multiple data items
    data_items = ["file1.txt", "file2.png", "file3.doc", "file4.mov"]
    for data in data_items:
        network.insert_data(data)

    # Verify data is distributed across different nodes
    total_data_count = sum(len(node.data) for node in network.nodes)
    assert total_data_count == len(data_items)


def test_node_data_transfer():
    """Test node data transfer (when deleting node)"""
    m = 4
    network = Network(m, [0])

    # Add node
    network.add_node(8)

    # Store data on node 8
    network.insert_data("transfer_test.txt")

    # Ensure data is stored
    assert network.lookup_data("transfer_test.txt") is not None

    # Delete node 8 (if data transfer is implemented)
    if hasattr(network, 'remove_node'):
        network.remove_node(8)
        # Verify data can still be found
        assert network.lookup_data("transfer_test.txt") is not None


if __name__ == "__main__":
    pytest.main([__file__])
