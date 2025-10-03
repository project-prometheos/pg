"""Unit tests for the tokenizer."""

import pytest

from pg_parser.context import Context
from pg_parser.tokenizer import Token, TokenType, Tokenizer


def test_tokenize_number():
    """Test tokenizing numbers."""
    tokenizer = Tokenizer()

    # Integer
    tokens = tokenizer.tokenize("42")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == "42"

    # Float
    tokens = tokenizer.tokenize("3.14")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == "3.14"

    # Scientific notation
    tokens = tokenizer.tokenize("1.5e-10")
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].value == "1.5e-10"


def test_tokenize_variable():
    """Test tokenizing variables."""
    tokenizer = Tokenizer()

    tokens = tokenizer.tokenize("x")
    assert tokens[0].type == TokenType.VARIABLE
    assert tokens[0].value == "x"

    tokens = tokenizer.tokenize("alpha")
    assert tokens[0].type == TokenType.VARIABLE
    assert tokens[0].value == "alpha"


def test_tokenize_constant():
    """Test tokenizing constants."""
    tokenizer = Tokenizer()

    tokens = tokenizer.tokenize("pi")
    assert tokens[0].type == TokenType.CONSTANT
    assert tokens[0].value == "pi"

    tokens = tokenizer.tokenize("e")
    assert tokens[0].type == TokenType.CONSTANT
    assert tokens[0].value == "e"


def test_tokenize_operators():
    """Test tokenizing operators."""
    tokenizer = Tokenizer()

    # Arithmetic
    for op, token_type in [("+", TokenType.PLUS), ("-", TokenType.MINUS),
                            ("*", TokenType.MULTIPLY), ("/", TokenType.DIVIDE),
                            ("^", TokenType.POWER)]:
        tokens = tokenizer.tokenize(op)
        assert tokens[0].type == token_type

    # Comparison
    tokens = tokenizer.tokenize("<=")
    assert tokens[0].type == TokenType.LE

    tokens = tokenizer.tokenize(">=")
    assert tokens[0].type == TokenType.GE


def test_tokenize_function():
    """Test tokenizing function calls."""
    tokenizer = Tokenizer()

    tokens = tokenizer.tokenize("sin(x)")
    assert tokens[0].type == TokenType.FUNCTION
    assert tokens[0].value == "sin"


def test_tokenize_expression():
    """Test tokenizing a complete expression."""
    tokenizer = Tokenizer()

    tokens = tokenizer.tokenize("2*x + 3")
    types = [t.type for t in tokens if t.type != TokenType.EOF]

    assert types == [
        TokenType.NUMBER,
        TokenType.MULTIPLY,
        TokenType.VARIABLE,
        TokenType.PLUS,
        TokenType.NUMBER,
    ]


def test_implicit_multiplication():
    """Test implicit multiplication insertion."""
    tokenizer = Tokenizer()

    # 2x should become 2 * x
    tokens = tokenizer.tokenize("2x")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert types == [TokenType.NUMBER, TokenType.MULTIPLY, TokenType.VARIABLE]

    # (x+1)(x-1) should have multiplication
    tokens = tokenizer.tokenize("(x+1)(x-1)")
    # Should have multiplication after first closing paren
    has_mult = any(
        t.type == TokenType.MULTIPLY
        for t in tokens
    )
    assert has_mult


def test_tokenize_parentheses():
    """Test tokenizing different parenthesis types."""
    tokenizer = Tokenizer()

    tokens = tokenizer.tokenize("(1, 2)")
    types = [t.type for t in tokens if t.type != TokenType.EOF]
    assert TokenType.LPAREN in types
    assert TokenType.RPAREN in types
    assert TokenType.COMMA in types


def test_invalid_character():
    """Test that invalid characters raise an error."""
    tokenizer = Tokenizer()

    with pytest.raises(ValueError, match="Invalid character"):
        tokenizer.tokenize("2 & 3")
