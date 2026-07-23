import pytest
from src.reader import read
from src.expr import global_env, Number

def test_add_sub():
    env = global_env.copy()
    # Test addition
    expr = read("add(1, 2)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 3
    
    # Test subtraction
    expr = read("sub(10, 5)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 5

def test_mul_div():
    env = global_env.copy()
    # Test multiplication
    expr = read("mul(3, 4)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 12
    
    # Test division
    expr = read("truediv(10, 2)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 5

def test_nested_calls():
    env = global_env.copy()
    expr = read("add(mul(2, 3), truediv(8, 4))")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 8

def test_multi_arg_calls():
    env = global_env.copy()
    expr = read("max(1, 2, 3, 4, 5)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 5

def test_type_error_handling():
    env = global_env.copy()
    with pytest.raises(TypeError) as excinfo:
        expr = read("add(1, lambda: 42)")
        expr.eval(env)
    assert "Invalid arguments" in str(excinfo.value)

def test_undefined_var_handling():
    env = global_env.copy()
    expr = read("x")
    assert expr.eval(env) is None
