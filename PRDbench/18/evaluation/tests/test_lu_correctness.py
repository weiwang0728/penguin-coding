# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.LU import LU_factorization
from utils import matrixFromFile, auxiliary

def test_lu_factorization_correctness():
    """Test correctness of LU factorization calculation results"""
    # Load test matrix
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/LU.txt')
    matrix = matrixFromFile.load_array(input_file, 'LU')

    # Extract original matrix (remove row number column) and save a copy
    # Important: must save a copy before calling LU_factorization, as the function modifies the input matrix
    original_matrix = matrix[:, :-1].copy()
    m, n = original_matrix.shape

    # Execute LU factorization (note: this function modifies the input matrix)
    L, U, P = LU_factorization(matrix)

    # Verify returned matrices are not empty and have correct shapes
    assert L is not None and L.size > 0, "L matrix cannot be empty"
    assert U is not None and U.size > 0, "U matrix cannot be empty"
    assert P is not None and P.size > 0, "P matrix cannot be empty"

    # Verify matrix shapes
    assert L.shape == (m, n), f"L matrix shape error: expected {(m, n)}, actual {L.shape}"
    assert U.shape == (m, n), f"U matrix shape error: expected {(m, n)}, actual {U.shape}"
    assert P.shape == (m, n), f"P matrix shape error: expected {(m, n)}, actual {P.shape}"

    # Verify L is lower triangular matrix (diagonal elements are 1)
    for i in range(m):
        for j in range(i+1, n):
            assert abs(L[i, j]) < 1e-12, f"L matrix is not lower triangular: L[{i},{j}] = {L[i, j]}"
        assert abs(L[i, i] - 1.0) < 1e-12, f"L matrix diagonal should be 1: L[{i},{i}] = {L[i, i]}"

    # Verify U is upper triangular matrix
    for i in range(1, m):
        for j in range(i):
            assert abs(U[i, j]) < 1e-12, f"U matrix is not upper triangular: U[{i},{j}] = {U[i, j]}"

    # Verify P is permutation matrix (exactly one 1 per row and column)
    for i in range(m):
        row_sum = np.sum(P[i, :])
        assert abs(row_sum - 1.0) < 1e-12, f"P matrix row {i} sum is not 1: {row_sum}"

    for j in range(n):
        col_sum = np.sum(P[:, j])
        assert abs(col_sum - 1.0) < 1e-12, f"P matrix column {j} sum is not 1: {col_sum}"

    # Verify standard LU decomposition formula: PA = LU
    PA = P.dot(original_matrix)
    LU = L.dot(U)

    # Check error between PA and LU
    error = np.linalg.norm(PA - LU)
    assert error < 1e-6, f"LU decomposition verification failed: ||PA - LU|| = {error}"

    # Verify function runs normally and produces reasonable output
    assert not np.any(np.isnan(L)), "L matrix contains NaN values"
    assert not np.any(np.isnan(U)), "U matrix contains NaN values"
    assert not np.any(np.isnan(P)), "P matrix contains NaN values"
    assert not np.any(np.isnan(PA)), "PA matrix contains NaN values"
    assert not np.any(np.isnan(LU)), "LU matrix contains NaN values"

if __name__ == "__main__":
    test_lu_factorization_correctness()
    print("LU factorization correctness test passed")