"""Unit tests for the parser."""

import pytest

from pg_parser.ast import BinaryOp, Constant, FunctionCall, Number, Point, UnaryOp, Variable, Vector
from pg_parser.context import Context
from pg_parser.parser import Parser, ParseError


def test_parse_number():
    """Test parsing a simple number."""
    parser = Parser()
    ast = parser.parse("42")

    assert isinstance(ast, Number)
    assert ast.value == 42.0


def test_parse_variable():
    """Test parsing a variable."""
    parser = Parser()
    ast = parser.parse("x")

    assert isinstance(ast, Variable)
    assert ast.name == "x"


def test_parse_constant():
    """Test parsing a constant."""
    parser = Parser()
    ast = parser.parse("pi")

    assert isinstance(ast, Constant)
    assert ast.name == "pi"


def test_parse_addition():
    """Test parsing addition."""
    parser = Parser()
    ast = parser.parse("2 + 3")

    assert isinstance(ast, BinaryOp)
    assert ast.op == "+"
    assert isinstance(ast.left, Number)
    assert ast.left.value == 2.0
    assert isinstance(ast.right, Number)
    assert ast.right.value == 3.0


def test_parse_precedence():
    """Test operator precedence."""
    parser = Parser()

    # 2 + 3 * 4 should parse as 2 + (3 * 4)
    ast = parser.parse("2 + 3 * 4")

    assert isinstance(ast, BinaryOp)
    assert ast.op == "+"
    assert isinstance(ast.left, Number)
    assert isinstance(ast.right, BinaryOp)
    assert ast.right.op == "*"


def test_parse_power():
    """Test parsing exponentiation."""
    parser = Parser()

    # 2 ^ 3 ^ 4 should parse as 2 ^ (3 ^ 4) (right associative)
    ast = parser.parse("2 ^ 3 ^ 4")

    assert isinstance(ast, BinaryOp)
    assert ast.op == "^"
    assert isinstance(ast.left, Number)
    assert ast.left.value == 2.0
    assert isinstance(ast.right, BinaryOp)
    assert ast.right.op == "^"


def test_parse_unary_minus():
    """Test parsing unary minus."""
    parser = Parser()
    ast = parser.parse("-x")

    assert isinstance(ast, UnaryOp)
    assert ast.op == "-"
    assert isinstance(ast.operand, Variable)


def test_parse_function_call():
    """Test parsing function calls."""
    parser = Parser()
    ast = parser.parse("sin(x)")

    assert isinstance(ast, FunctionCall)
    assert ast.name == "sin"
    assert len(ast.args) == 1
    assert isinstance(ast.args[0], Variable)


def test_parse_function_multiple_args():
    """Test parsing function with multiple arguments."""
    parser = Parser()
    ast = parser.parse("max(1, 2, 3)")

    assert isinstance(ast, FunctionCall)
    assert ast.name == "max"
    assert len(ast.args) == 3


def test_parse_parentheses():
    """Test parsing parenthesized expressions."""
    parser = Parser()

    # (2 + 3) * 4 should parse with addition first
    ast = parser.parse("(2 + 3) * 4")

    assert isinstance(ast, BinaryOp)
    assert ast.op == "*"
    assert isinstance(ast.left, BinaryOp)
    assert ast.left.op == "+"


def test_parse_point():
    """Test parsing a point."""
    parser = Parser()
    ast = parser.parse("(1, 2)")

    assert isinstance(ast, Point)
    assert len(ast.coords) == 2


def test_parse_vector():
    """Test parsing a vector."""
    parser = Parser()
    ast = parser.parse("<1, 2, 3>")

    assert isinstance(ast, Vector)
    assert len(ast.components) == 3


def test_parse_complex_expression():
    """Test parsing a complex expression."""
    parser = Parser()
    ast = parser.parse("2*x^2 + 3*x + 1")

    assert isinstance(ast, BinaryOp)
    # Should be: (2*x^2 + 3*x) + 1 or 2*x^2 + (3*x + 1)
    # Either way, top level is +


def test_parse_implicit_multiplication():
    """Test parsing with implicit multiplication."""
    parser = Parser()
    ast = parser.parse("2x")

    assert isinstance(ast, BinaryOp)
    assert ast.op == "*"
    assert isinstance(ast.left, Number)
    assert isinstance(ast.right, Variable)


def test_parse_empty_expression():
    """Test that empty expression raises error."""
    parser = Parser()

    with pytest.raises(ParseError):
        parser.parse("")


def test_parse_invalid_syntax():
    """Test that invalid syntax raises error."""
    parser = Parser()

    with pytest.raises(ParseError):
        parser.parse("2 +")  # Incomplete expression
