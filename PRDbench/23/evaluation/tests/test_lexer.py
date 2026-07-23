import pytest
from src.reader import tokenize, next_token
from src.buffer import Buffer

def test_integer_lexing():
    tokens = tokenize("42 -7")
    assert tokens == [42, -7]

def test_float_lexing():
    tokens = tokenize("3.14 -0.5")
    assert tokens == [3.14, -0.5]

def test_identifier_lexing():
    tokens = tokenize("x var1")
    assert tokens == ['x', 'var1']

def test_underscore_identifier_lexing():
    tokens = tokenize("_y _var2")
    assert tokens == ['_y', '_var2']

def test_lexer_error_handling():
    with pytest.raises(SyntaxError) as excinfo:
        tokenize("@#$")
    assert "'@' is not a token" in str(excinfo.value)
    
    with pytest.raises(SyntaxError) as excinfo:
        tokenize("1.2.3")
    assert "'1.2.3' is not a numeral" in str(excinfo.value)
