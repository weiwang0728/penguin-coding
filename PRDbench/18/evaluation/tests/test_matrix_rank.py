# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.LU import LU_factorization
from model.Gram_Schmidt import gram_schmidt
from model.HouseHold import householder_reflection
from model.Givens import givens_rotation
from model.URV import URV_factorization
from utils import matrixFromFile, auxiliary

def test_lu_matrix_rank():
    """Test matrix rank calculation in LU factorization"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/LU.txt')
    matrix = matrixFromFile.load_array(input_file, 'LU')

    # Calculate matrix rank
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)

    # Verify correctness of rank calculation
    assert calculated_rank == expected_rank, f"Matrix rank calculation error: calculated={calculated_rank}, expected={expected_rank}"

    # Verify matrix is full rank (for square matrices)
    m, n = matrix.shape
    if m == n:
        assert calculated_rank == m, f"Square matrix should be full rank: rank={calculated_rank}, dimension={m}"

def test_qr_matrix_rank():
    """Test matrix rank calculation in QR factorization"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/GramSchmidt.txt')
    matrix = matrixFromFile.load_array(input_file, 'QR')

    # Calculate matrix rank
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)

    # Verify correctness of rank calculation
    assert calculated_rank == expected_rank, f"Matrix rank calculation error: calculated={calculated_rank}, expected={expected_rank}"

def test_hr_matrix_rank():
    """Test matrix rank calculation in Householder reflection"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Household.txt')
    matrix = matrixFromFile.load_array(input_file, 'HR')

    # Calculate matrix rank
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)

    # Verify correctness of rank calculation
    assert calculated_rank == expected_rank, f"Matrix rank calculation error: calculated={calculated_rank}, expected={expected_rank}"

def test_gr_matrix_rank():
    """Test matrix rank calculation in Givens rotation"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Givens.txt')
    matrix = matrixFromFile.load_array(input_file, 'GR')

    # Calculate matrix rank
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)

    # Verify correctness of rank calculation
    assert calculated_rank == expected_rank, f"Matrix rank calculation error: calculated={calculated_rank}, expected={expected_rank}"

def test_urv_matrix_rank():
    """Test matrix rank calculation in URV factorization"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/URV.txt')
    matrix = matrixFromFile.load_array(input_file, 'URV')

    # Calculate matrix rank
    calculated_rank = auxiliary.rank_of_matrix(matrix)
    expected_rank = np.linalg.matrix_rank(matrix)

    # Verify correctness of rank calculation
    assert calculated_rank == expected_rank, f"Matrix rank calculation error: calculated={calculated_rank}, expected={expected_rank}"

if __name__ == "__main__":
    test_lu_matrix_rank()
    test_qr_matrix_rank()
    test_hr_matrix_rank()
    test_gr_matrix_rank()
    test_urv_matrix_rank()
    print("All matrix rank calculation tests passed")