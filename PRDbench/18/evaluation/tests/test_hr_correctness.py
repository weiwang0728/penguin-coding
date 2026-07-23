# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.HouseHold import householder_reflection
from utils import matrixFromFile

def test_hr_factorization_correctness():
    """Test correctness of Householder reflection (mirror symmetric transformation) factorization calculation results"""
    # Load test matrix
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Household.txt')
    matrix = matrixFromFile.load_array(input_file, 'HR')

    # Execute Householder reflection factorization
    Q, R = householder_reflection(matrix)

    # Verify Q*R = A
    reconstructed = np.dot(Q, R)

    # Check reconstruction error
    error = np.linalg.norm(matrix - reconstructed)
    assert error < 1e-10, f"Householder reflection factorization reconstruction error too large: {error}"

    # Verify Q is orthogonal matrix (Q^T * Q = I)
    m, n = Q.shape
    QTQ = np.dot(Q.T, Q)
    identity = np.eye(m)  # Householder typically produces square matrix Q
    orthogonal_error = np.linalg.norm(QTQ - identity)
    assert orthogonal_error < 1e-10, f"Q matrix is not orthogonal: ||Q^T*Q - I|| = {orthogonal_error}"

    # Verify R is upper triangular matrix
    m, n = R.shape
    for i in range(1, m):
        for j in range(min(i, n)):
            assert abs(R[i, j]) < 1e-12, f"R matrix is not upper triangular: R[{i},{j}] = {R[i, j]}"

if __name__ == "__main__":
    test_hr_factorization_correctness()
    print("Householder reflection factorization correctness test passed")