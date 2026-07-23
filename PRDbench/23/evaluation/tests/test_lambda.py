import pytest
from src.reader import read
from src.expr import global_env, Number

def test_no_arg_lambda():
    env = global_env.copy()
    expr = read("(lambda: 42)()")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 42

def test_single_arg_lambda():
    env = global_env.copy()
    expr = read("(lambda x: add(x, 1))(5)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 6

def test_multi_arg_lambda():
    env = global_env.copy()
    expr = read("(lambda x, y: add(x, y))(3, 4)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 7

def test_lambda_closure():
    env = global_env.copy()
    expr = read("(lambda x: (lambda y: add(x, y)))(5)(3)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 8

def test_function_as_arg():
    env = global_env.copy()
    expr = read("(lambda f, x: f(x))(lambda y: add(y, 1), 5)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 6

def test_function_as_return():
    env = global_env.copy()
    expr = read("(lambda x: lambda y: add(x, y))(5)(3)")
    result = expr.eval(env)
    assert isinstance(result, Number)
    assert result.value == 8
