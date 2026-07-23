# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import pytest
import io
from contextlib import redirect_stdout

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from model.LU import LU_factorization
from model.Gram_Schmidt import gram_schmidt
from model.HouseHold import householder_reflection
from model.Givens import givens_rotation
from model.URV import URV_factorization
from utils import matrixFromFile, auxiliary

def test_lu_output_format():
    """Test output format compliance of LU factorization"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/LU.txt')
    matrix = matrixFromFile.load_array(input_file, 'LU')

    L, U, P = LU_factorization(matrix)

    # Capture print_array output
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(L)
    output = f.getvalue()

    # Check output format: should contain 4 decimal places
    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            # Check number format in each line
            numbers = line.split(',')[:-1]  # Remove trailing empty comma
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    # Verify format is 8.4f
                    assert '.' in num_str, f"Number format error, missing decimal point: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"Decimal places not 4 digits: {num_str}"

def test_qr_output_format():
    """Test output format compliance of QR factorization"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/GramSchmidt.txt')
    matrix = matrixFromFile.load_array(input_file, 'QR')

    Q, R = gram_schmidt(matrix)

    # Test Q matrix format
    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(Q)
    output = f.getvalue()

    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"Number format error: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"Decimal places not 4 digits: {num_str}"

def test_hr_output_format():
    """Test output format compliance of Householder reflection"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Household.txt')
    matrix = matrixFromFile.load_array(input_file, 'HR')

    Q, R = householder_reflection(matrix)

    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(Q)
    output = f.getvalue()

    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"Number format error: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"Decimal places not 4 digits: {num_str}"

def test_gr_output_format():
    """Test output format compliance of Givens rotation"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/Givens.txt')
    matrix = matrixFromFile.load_array(input_file, 'GR')

    Q, R = givens_rotation(matrix)

    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(Q)
    output = f.getvalue()

    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"Number format error: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"Decimal places not 4 digits: {num_str}"

def test_urv_output_format():
    """Test output format compliance of URV factorization"""
    input_file = os.path.join(os.path.dirname(__file__), '../../src/data/URV.txt')
    matrix = matrixFromFile.load_array(input_file, 'URV')

    U, R, V = URV_factorization(matrix)

    f = io.StringIO()
    with redirect_stdout(f):
        auxiliary.print_array(U)
    output = f.getvalue()

    lines = output.strip().split('\n')
    for line in lines:
        if line.strip():
            numbers = line.split(',')[:-1]
            for num_str in numbers:
                num_str = num_str.strip()
                if num_str:
                    assert '.' in num_str, f"Number format error: {num_str}"
                    decimal_part = num_str.split('.')[1]
                    assert len(decimal_part) == 4, f"Decimal places not 4 digits: {num_str}"

if __name__ == "__main__":
    test_lu_output_format()
    test_qr_output_format()
    test_hr_output_format()
    test_gr_output_format()
    test_urv_output_format()
    print("All output format tests passed")