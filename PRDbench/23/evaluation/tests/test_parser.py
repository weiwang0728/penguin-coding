import pytest
from src.reader import read
from src.expr import Literal, Name, CallExpr, LambdaExpr

def test_number_parsing():
    expr = read("42")
    assert isinstance(expr, Literal)
    assert expr.value == 42
    expr = read("3.14")
    assert isinstance(expr, Literal)
    assert expr.value == 3.14

def test_name_parsing():
    expr = read("x")
    assert isinstance(expr, Name)
    assert expr.string == 'x'

def test_basic_function_call():
    expr = read("add(1, 2)")
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.operator, Name)
    assert expr.operator.string == 'add'
    assert len(expr.operands) == 2
    assert isinstance(expr.operands[0], Literal)
    assert expr.operands[0].value == 1
    assert isinstance(expr.operands[1], Literal)
    assert expr.operands[1].value == 2

def test_nested_function_call():
    expr = read("mul(add(1, 2), 3)")
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.operator, Name)
    assert expr.operator.string == 'mul'
    assert len(expr.operands) == 2
    assert isinstance(expr.operands[0], CallExpr)
    assert isinstance(expr.operands[1], Literal)
    assert expr.operands[1].value == 3

def test_no_arg_lambda():
    expr = read("lambda: 42")
    assert isinstance(expr, LambdaExpr)
    assert expr.parameters == []
    assert isinstance(expr.body, Literal)
    assert expr.body.value == 42

def test_arg_lambda():
    expr = read("lambda x: add(x, 1)")
    assert isinstance(expr, LambdaExpr)
    assert expr.parameters == ['x']
    assert isinstance(expr.body, CallExpr)

def test_parser_error_handling():
    with pytest.raises(SyntaxError) as excinfo:
        read("(")
    assert "Incomplete expression" in str(excinfo.value)
    
    with pytest.raises(SyntaxError) as excinfo:
        read("lambda x y: 10")
    assert "expected ':' but got 'y'" in str(excinfo.value)