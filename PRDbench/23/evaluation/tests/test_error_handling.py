import pytest
from src.reader import read
from src.expr import global_env

def test_error_messages():
    env = global_env.copy()
    
    # Test syntax error (unclosed parenthesis)
    with pytest.raises(SyntaxError) as excinfo:
        read("(")
    assert "Incomplete expression" in str(excinfo.value)
    
    # Test undefined variable
    expr = read("x")
    assert expr.eval(env) is None
    
    # Test type error
    with pytest.raises(TypeError) as excinfo:
        expr = read("add(1, lambda: 42)")
        expr.eval(env)
    assert "Invalid arguments" in str(excinfo.value)
    
    # Test invalid character
    with pytest.raises(SyntaxError) as excinfo:
        read("@#$")
    assert "is not a token" in str(excinfo.value)
