import pytest
from src.reader import read
from src.expr import global_env, Number

def test_basic_arithmetic():
    env = global_env.copy()
    # Test add
    expr = read("add(5, 3)")
    assert expr.eval(env).value == 8
    
    # Test sub
    expr = read("sub(5, 3)")
    assert expr.eval(env).value == 2
    
    # Test mul
    expr = read("mul(5, 3)")
    assert expr.eval(env).value == 15
    
    # Test truediv
    expr = read("truediv(6, 3)")
    assert expr.eval(env).value == 2

def test_advanced_arithmetic():
    env = global_env.copy()
    # Test floordiv
    expr = read("floordiv(7, 2)")
    assert expr.eval(env).value == 3
    
    # Test mod
    expr = read("mod(7, 3)")
    assert expr.eval(env).value == 1
    
    # Test pow
    expr = read("pow(2, 3)")
    assert expr.eval(env).value == 8

def test_abs_min_max():
    env = global_env.copy()
    # Test abs
    expr = read("abs(-5)")
    assert expr.eval(env).value == 5
    
    # Test max
    expr = read("max(1, 5, 3)")
    assert expr.eval(env).value == 5
    
    # Test min
    expr = read("min(1, 5, 3)")
    assert expr.eval(env).value == 1

def test_type_conversion():
    env = global_env.copy()
    # Test int
    expr = read("int(3.14)")
    assert expr.eval(env).value == 3
    
    # Test float
    expr = read("float(42)")
    assert expr.eval(env).value == 42.0
