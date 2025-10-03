"""Tests for answer evaluators."""

import pytest

from pg_answer.evaluators import (
    FormulaEvaluator,
    NumericEvaluator,
    StringEvaluator,
    VectorEvaluator,
)
from pg_math import Formula, Real, Vector


# Numeric Evaluator Tests


def test_numeric_evaluator_correct():
    """Test numeric evaluator with correct answer."""
    evaluator = NumericEvaluator(42.0, tolerance=0.001)
    result = evaluator.evaluate("42")

    assert result.correct is True
    assert result.score == 1.0
    assert result.type == "numeric"


def test_numeric_evaluator_incorrect():
    """Test numeric evaluator with incorrect answer."""
    evaluator = NumericEvaluator(42.0, tolerance=0.001)
    result = evaluator.evaluate("40")

    assert result.correct is False
    assert result.score == 0.0


def test_numeric_evaluator_fuzzy():
    """Test numeric evaluator with fuzzy tolerance."""
    evaluator = NumericEvaluator(1.0, tolerance=0.01)  # 1% tolerance
    result = evaluator.evaluate("1.005")  # Within 1%

    assert result.correct is True


def test_numeric_evaluator_expression():
    """Test numeric evaluator with expression."""
    evaluator = NumericEvaluator("2*pi", tolerance=0.001)
    result = evaluator.evaluate("6.283185")

    assert result.correct is True


def test_numeric_evaluator_blank():
    """Test numeric evaluator with blank answer."""
    evaluator = NumericEvaluator(42.0)
    result = evaluator.evaluate("")

    assert result.error_flag is True
    assert "blank" in result.error_message.lower()


def test_numeric_evaluator_parse_error():
    """Test numeric evaluator with invalid input."""
    evaluator = NumericEvaluator(42.0)
    result = evaluator.evaluate("not a number")

    assert result.error_flag is True
    assert "parse" in result.error_message.lower()


def test_numeric_evaluator_complex():
    """Test numeric evaluator with complex numbers."""
    evaluator = NumericEvaluator("1+2j", tolerance=0.001)  # Python uses j for imaginary
    result = evaluator.evaluate("1+2j")

    assert result.correct is True


def test_numeric_evaluator_infinity():
    """Test numeric evaluator with infinity."""
    evaluator = NumericEvaluator("inf", tolerance=0.001)
    result = evaluator.evaluate("infinity")

    assert result.correct is True


# Formula Evaluator Tests


def test_formula_evaluator_correct():
    """Test formula evaluator with correct answer."""
    evaluator = FormulaEvaluator("x^2", variables=["x"])
    result = evaluator.evaluate("x^2")

    assert result.correct is True
    assert result.type == "formula"


def test_formula_evaluator_equivalent():
    """Test formula evaluator with equivalent formula."""
    evaluator = FormulaEvaluator("x^2 - 1", variables=["x"])
    result = evaluator.evaluate("(x-1)*(x+1)")

    assert result.correct is True


def test_formula_evaluator_incorrect():
    """Test formula evaluator with incorrect formula."""
    evaluator = FormulaEvaluator("x^2", variables=["x"])
    result = evaluator.evaluate("x^3")

    assert result.correct is False


def test_formula_evaluator_simplified():
    """Test formula evaluator with simplified vs expanded."""
    evaluator = FormulaEvaluator("2*x", variables=["x"])
    result = evaluator.evaluate("x + x")

    assert result.correct is True


def test_formula_evaluator_blank():
    """Test formula evaluator with blank answer."""
    evaluator = FormulaEvaluator("x^2", variables=["x"])
    result = evaluator.evaluate("")

    assert result.error_flag is True


# String Evaluator Tests


def test_string_evaluator_exact():
    """Test string evaluator with exact match."""
    evaluator = StringEvaluator("Hello World", case_sensitive=True)
    result = evaluator.evaluate("Hello World")

    assert result.correct is True
    assert result.type == "string"


def test_string_evaluator_case_insensitive():
    """Test string evaluator case insensitive."""
    evaluator = StringEvaluator("Hello World", case_sensitive=False)
    result = evaluator.evaluate("hello world")

    assert result.correct is True


def test_string_evaluator_case_sensitive():
    """Test string evaluator case sensitive."""
    evaluator = StringEvaluator("Hello World", case_sensitive=True)
    result = evaluator.evaluate("hello world")

    assert result.correct is False


def test_string_evaluator_whitespace():
    """Test string evaluator with whitespace trimming."""
    evaluator = StringEvaluator("answer", trim_whitespace=True)
    result = evaluator.evaluate("  answer  ")

    assert result.correct is True


def test_string_evaluator_regex():
    """Test string evaluator with regex matching."""
    evaluator = StringEvaluator(r"\d{3}-\d{4}", regex_match=True)
    result = evaluator.evaluate("123-4567")

    assert result.correct is True


def test_string_evaluator_regex_fail():
    """Test string evaluator regex non-match."""
    evaluator = StringEvaluator(r"\d{3}-\d{4}", regex_match=True)
    result = evaluator.evaluate("12-34")

    assert result.correct is False


# Vector Evaluator Tests


def test_vector_evaluator_correct():
    """Test vector evaluator with correct answer."""
    evaluator = VectorEvaluator([1, 2, 3], tolerance=0.001)
    result = evaluator.evaluate("<1, 2, 3>")

    assert result.correct is True
    assert result.type == "vector"


def test_vector_evaluator_incorrect():
    """Test vector evaluator with incorrect answer."""
    evaluator = VectorEvaluator([1, 2, 3], tolerance=0.001)
    result = evaluator.evaluate("<1, 2, 4>")

    assert result.correct is False


def test_vector_evaluator_fuzzy():
    """Test vector evaluator with fuzzy tolerance."""
    evaluator = VectorEvaluator([1.0, 2.0], tolerance=0.01)
    result = evaluator.evaluate("<1.005, 2.005>")

    assert result.correct is True


# Integration Tests


def test_evaluator_metadata():
    """Test that evaluators include metadata."""
    evaluator = NumericEvaluator(42.0, tolerance=0.01, tolerance_mode="relative")
    result = evaluator.evaluate("42")

    assert "tolerance" in result.metadata
    assert result.metadata["tolerance"] == 0.01
    assert result.metadata["tolerance_mode"] == "relative"


def test_evaluator_preview():
    """Test that evaluators generate preview."""
    evaluator = NumericEvaluator(42.0)
    result = evaluator.evaluate("2*21")

    assert result.preview  # Should have LaTeX preview


def test_evaluator_original_answer():
    """Test that original student answer is preserved."""
    evaluator = NumericEvaluator(42.0)
    result = evaluator.evaluate("  42  ")

    assert result.original_student_answer == "  42  "
    assert result.student_answer == "42"  # Normalized
