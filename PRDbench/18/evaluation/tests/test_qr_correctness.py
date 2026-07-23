# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.Gram_Schmidt import gram_schmidt
from utils import matrixFromFile

def test_qr_factorization_correctness():
    """Test correctness of QR factorization calculation results"""
    # Load test matrix
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/GramSchmidt.txt')
    matrix = matrixFromFile.load_array(input_file, 'QR')

    # Execute QR factorization
    Q, R = gram_schmidt(matrix)

    # Verify Q*R = A
    reconstructed = np.dot(Q, R)

    # Check reconstruction error
    error = np.linalg.norm(matrix - reconstructed)
    assert error < 1e-10, f"QR decomposition reconstruction error too large: {error}"

    # Verify Q is orthogonal matrix (Q^T * Q = I)
    m, n = Q.shape
    QTQ = np.dot(Q.T, Q)
    identity = np.eye(n)
    orthogonal_error = np.linalg.norm(QTQ - identity)
    assert orthogonal_error < 1e-10, f"Q matrix is not orthogonal: ||Q^T*Q - I|| = {orthogonal_error}"

    # Verify R is upper triangular matrix
    m, n = R.shape
    for i in range(1, m):
        for j in range(min(i, n)):
            assert abs(R[i, j]) < 1e-12, f"R matrix is not upper triangular: R[{i},{j}] = {R[i, j]}"

if __name__ == "__main__":
    test_qr_factorization_correctness()
    print("QR factorization correctness test passed")