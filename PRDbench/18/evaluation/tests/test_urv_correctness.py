# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.URV import URV_factorization
from utils import matrixFromFile

def test_urv_factorization_correctness():
    """Test correctness of URV factorization calculation results"""
    # Load test matrix
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/URV.txt')
    matrix = matrixFromFile.load_array(input_file, 'URV')

    # Execute URV factorization
    U, R, V = URV_factorization(matrix)

    # Verify U*R*V^T = A
    reconstructed = U.dot(R).dot(V.T)

    # Check reconstruction error
    error = np.linalg.norm(matrix - reconstructed)
    assert error < 1e-10, f"URV factorization reconstruction error too large: {error}"

    # Verify U is orthogonal matrix (U^T * U = I)
    m, n = U.shape
    UTU = np.dot(U.T, U)
    identity_u = np.eye(n)
    orthogonal_error_u = np.linalg.norm(UTU - identity_u)
    assert orthogonal_error_u < 1e-10, f"U matrix is not orthogonal: ||U^T*U - I|| = {orthogonal_error_u}"

    # Verify V is orthogonal matrix (V^T * V = I)
    m, n = V.shape
    VTV = np.dot(V.T, V)
    identity_v = np.eye(n)
    orthogonal_error_v = np.linalg.norm(VTV - identity_v)
    assert orthogonal_error_v < 1e-10, f"V matrix is not orthogonal: ||V^T*V - I|| = {orthogonal_error_v}"

if __name__ == "__main__":
    test_urv_factorization_correctness()
    print("URV factorization correctness test passed")