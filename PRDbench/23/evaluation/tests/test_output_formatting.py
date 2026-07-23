import pytest
from src.reader import read
from src.expr import global_env
from src.repl import REPL

def test_output_formatting():
    # Test normal output formatting
    env = global_env.copy()
    expr = read("add(1, 2)")
    result = expr.eval(env)
    assert str(result) == "3"  # Simple clean output
    
    # Test error output formatting
    with pytest.raises(TypeError) as excinfo:
        expr = read("add(1, lambda: 1)")
        expr.eval(env)
    error_msg = str(excinfo.value)
    assert "Invalid arguments" in error_msg  # Error indicator
    
    # Test REPL prompt formatting
    repl = REPL()
    assert repl.prompt == "> "  # Simple consistent prompt
    
    # Test multiline output formatting
    expr = read("max(1, 2, 3, 4, 5)")
    result = expr.eval(env)
    assert "\n" not in str(result)  # No unexpected newlines

