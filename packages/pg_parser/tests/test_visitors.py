"""Unit tests for AST visitors."""

import math
import pytest

from pg_parser.ast import BinaryOp, Constant, FunctionCall, Number, UnaryOp, Variable
from pg_parser.parser import Parser
from pg_parser.visitors import EvalVisitor, StringVisitor, TeXVisitor


def test_string_visitor_simple():
    """Test StringVisitor with simple expressions."""
    parser = Parser()
    visitor = StringVisitor()

    ast = parser.parse("2 + 3")
    result = ast.accept(visitor)
    assert result == "2 + 3"


def test_string_visitor_precedence():
    """Test StringVisitor respects precedence."""
    parser = Parser()
    visitor = StringVisitor()

    # 2 + 3 * 4 should stay as is (no extra parens needed)
    ast = parser.parse("2 + 3 * 4")
    result = ast.accept(visitor)
    # The visitor adds spaces around operators
    assert "3 * 4" in result


def test_string_visitor_function():
    """Test StringVisitor with function calls."""
    parser = Parser()
    visitor = StringVisitor()

    ast = parser.parse("sin(x)")
    result = ast.accept(visitor)
    assert result == "sin(x)"


def test_tex_visitor_simple():
    """Test TeXVisitor with simple expressions."""
    parser = Parser()
    visitor = TeXVisitor()

    ast = parser.parse("2 + 3")
    result = ast.accept(visitor)
    assert "+" in result


def test_tex_visitor_power():
    """Test TeXVisitor formats powers correctly."""
    parser = Parser()
    visitor = TeXVisitor()

    ast = parser.parse("x^2")
    result = ast.accept(visitor)
    assert result == "x^{2}"


def test_tex_visitor_fraction():
    """Test TeXVisitor formats fractions."""
    parser = Parser()
    visitor = TeXVisitor()

    ast = parser.parse("1 / 2")
    result = ast.accept(visitor)
    assert r"\frac" in result


def test_tex_visitor_sqrt():
    """Test TeXVisitor formats square root."""
    parser = Parser()
    visitor = TeXVisitor()

    ast = parser.parse("sqrt(2)")
    result = ast.accept(visitor)
    assert r"\sqrt{2}" == result


def test_tex_visitor_greek():
    """Test TeXVisitor handles Greek letters."""
    parser = Parser()
    visitor = TeXVisitor()

    ast = parser.parse("theta")
    result = ast.accept(visitor)
    assert r"\theta" in result


def test_tex_visitor_constant_pi():
    """Test TeXVisitor formats pi."""
    parser = Parser()
    visitor = TeXVisitor()

    ast = parser.parse("pi")
    result = ast.accept(visitor)
    assert r"\pi" == result


def test_eval_visitor_addition():
    """Test EvalVisitor evaluates addition."""
    parser = Parser()
    visitor = EvalVisitor()

    ast = parser.parse("2 + 3")
    result = ast.accept(visitor)
    assert result == 5.0


def test_eval_visitor_precedence():
    """Test EvalVisitor respects precedence."""
    parser = Parser()
    visitor = EvalVisitor()

    ast = parser.parse("2 + 3 * 4")
    result = ast.accept(visitor)
    assert result == 14.0  # 2 + (3 * 4)


def test_eval_visitor_power():
    """Test EvalVisitor evaluates exponentiation."""
    parser = Parser()
    visitor = EvalVisitor()

    ast = parser.parse("2^3")
    result = ast.accept(visitor)
    assert result == 8.0


def test_eval_visitor_function():
    """Test EvalVisitor evaluates functions."""
    parser = Parser()
    visitor = EvalVisitor()

    ast = parser.parse("sin(0)")
    result = ast.accept(visitor)
    assert abs(result - 0.0) < 1e-10


def test_eval_visitor_constant():
    """Test EvalVisitor evaluates constants."""
    parser = Parser()
    visitor = EvalVisitor()

    ast = parser.parse("pi")
    result = ast.accept(visitor)
    assert abs(result - math.pi) < 1e-10


def test_eval_visitor_variable():
    """Test EvalVisitor with variable bindings."""
    parser = Parser()
    visitor = EvalVisitor(bindings={"x": 5.0})

    ast = parser.parse("2*x + 1")
    result = ast.accept(visitor)
    assert result == 11.0


def test_eval_visitor_undefined_variable():
    """Test EvalVisitor raises error for undefined variables."""
    parser = Parser()
    visitor = EvalVisitor()

    ast = parser.parse("x")
    with pytest.raises(ValueError, match="Undefined variable"):
        ast.accept(visitor)


def test_round_trip_string():
    """Test that parse -> string -> parse gives equivalent AST."""
    parser = Parser()
    visitor = StringVisitor()

    original = "2 + 3 * 4"
    ast1 = parser.parse(original)
    string_repr = ast1.accept(visitor)
    ast2 = parser.parse(string_repr)

    # Both ASTs should evaluate to the same value
    eval_visitor = EvalVisitor()
    result1 = ast1.accept(eval_visitor)
    result2 = ast2.accept(eval_visitor)

    assert result1 == result2
