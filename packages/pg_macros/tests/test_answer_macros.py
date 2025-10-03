"""Tests for answer macros."""

import pytest

from pg_macros import loadMacros


def test_num_cmp_basic():
    """Test basic num_cmp usage."""
    macros = loadMacros("PGanswermacros.pl")
    num_cmp = macros["num_cmp"]

    evaluator = num_cmp(42, tolerance=0.01)

    # Correct answer
    result = evaluator.evaluate("42")
    assert result.correct is True

    # Close enough (within tolerance)
    result = evaluator.evaluate("42.005")
    assert result.correct is True

    # Too far
    result = evaluator.evaluate("43")
    assert result.correct is False


def test_fun_cmp_basic():
    """Test basic fun_cmp usage."""
    macros = loadMacros("PGanswermacros.pl")
    fun_cmp = macros["fun_cmp"]

    evaluator = fun_cmp("x^2 + 1", var="x")

    # Equivalent expressions
    result = evaluator.evaluate("x**2 + 1")
    assert result.correct is True

    result = evaluator.evaluate("1 + x^2")
    assert result.correct is True

    # Different expression
    result = evaluator.evaluate("x^2 + 2")
    assert result.correct is False


def test_str_cmp_basic():
    """Test basic str_cmp usage."""
    macros = loadMacros("PGanswermacros.pl")
    str_cmp = macros["str_cmp"]

    # Case-sensitive
    evaluator = str_cmp("hello", case_sensitive=True)
    result = evaluator.evaluate("hello")
    assert result.correct is True

    result = evaluator.evaluate("HELLO")
    assert result.correct is False

    # Case-insensitive
    evaluator = str_cmp("hello", case_sensitive=False)
    result = evaluator.evaluate("HELLO")
    assert result.correct is True


def test_std_num_cmp():
    """Test std_num_cmp (0.1% tolerance)."""
    macros = loadMacros("PGanswermacros.pl")
    std_num_cmp = macros["std_num_cmp"]

    evaluator = std_num_cmp(100)

    # Within 0.1%
    result = evaluator.evaluate("100.05")
    assert result.correct is True

    # Outside 0.1%
    result = evaluator.evaluate("100.2")
    assert result.correct is False


def test_vector_cmp():
    """Test vector_cmp."""
    macros = loadMacros("PGanswermacros.pl")
    vector_cmp = macros["vector_cmp"]

    evaluator = vector_cmp("<1, 2, 3>", tolerance=0.01)

    result = evaluator.evaluate("<1, 2, 3>")
    assert result.correct is True

    result = evaluator.evaluate("<1.005, 2, 3>")
    assert result.correct is True


def test_interval_cmp():
    """Test interval_cmp."""
    macros = loadMacros("PGanswermacros.pl")
    interval_cmp = macros["interval_cmp"]

    evaluator = interval_cmp("[0, 1)", tolerance=0.01)

    result = evaluator.evaluate("[0, 1)")
    assert result.correct is True

    # Different interval type
    result = evaluator.evaluate("[0, 1]")
    assert result.correct is False
