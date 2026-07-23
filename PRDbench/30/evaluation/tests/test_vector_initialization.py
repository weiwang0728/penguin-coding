#!/usr/bin/env python3
"""
TransE Vector Initialization Test
"""

import sys
import os
import pytest
import numpy as np

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from transE import TransE


def test_vector_dimensions():
    """Test if vector dimensions are correct"""
    # Create test data
    entity_set = {'0', '1', '2'}
    relation_set = {'0', '1'}
    triple_list = [['0', '1', '0'], ['1', '2', '1']]

    # Create TransE model
    transE = TransE(entity_set, relation_set, triple_list,
                   embedding_dim=50, learning_rate=0.01, margin=1, L1=True)

    # Initialize vectors
    transE.emb_initialize()

    # Check entity vector dimensions
    for entity_id in entity_set:
        assert len(transE.entity[entity_id]) == 50, f"Entity vector dimension is incorrect: {len(transE.entity[entity_id])}"

    # Check relation vector dimensions
    for relation_id in relation_set:
        assert len(transE.relation[relation_id]) == 50, f"Relation vector dimension is incorrect: {len(transE.relation[relation_id])}"

    print("Vector dimension test passed: All vectors are 50-dimensional")


def test_vector_initialization_distribution():
    """Test if vector initialization uses uniform distribution"""
    entity_set = {'0', '1', '2'}
    relation_set = {'0', '1'}
    triple_list = [['0', '1', '0'], ['1', '2', '1']]

    transE = TransE(entity_set, relation_set, triple_list,
                   embedding_dim=50, learning_rate=0.01, margin=1, L1=True)

    transE.emb_initialize()

    # Check if vector values are within reasonable range (after uniform distribution initialization and normalization)
    for entity_id in entity_set:
        vector = np.array(transE.entity[entity_id])
        # Check if vector is normalized
        norm = np.linalg.norm(vector)
        assert abs(norm - 1.0) < 1e-6, f"Entity vector is not properly normalized: {norm}"

    for relation_id in relation_set:
        vector = np.array(transE.relation[relation_id])
        norm = np.linalg.norm(vector)
        assert abs(norm - 1.0) < 1e-6, f"Relation vector is not properly normalized: {norm}"

    print("Vector initialization distribution test passed: All vectors are properly normalized")


if __name__ == '__main__':
    test_vector_dimensions()
    test_vector_initialization_distribution()
    print("All tests passed!")
