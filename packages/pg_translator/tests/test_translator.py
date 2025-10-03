"""Tests for PG translator."""

import tempfile
from pathlib import Path

import pytest

from pg_translator import PGTranslator


def test_translate_source_simple():
    """Test translating simple PG source."""
    pg_source = """
a = 5
BEGIN_PGML
The value is [$a].
END_PGML

evaluator = num_cmp(5, tolerance=0.01)
ANS(evaluator, "answer1")
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=123)

    assert result.statement_html != ""
    assert "answer1" in result.answer_blanks
    assert result.errors is None or len(result.errors) == 0


def test_translate_source_with_formula():
    """Test translating problem with Formula."""
    pg_source = """
a = 2
f = Formula("x^2 + 1")

BEGIN_PGML
Differentiate [`[$f]`].

Answer: [_____]
END_PGML

evaluator = fun_cmp("2*x", variables=["x"])
ANS(evaluator)
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=123)

    assert result.statement_html != ""
    assert len(result.answer_blanks) > 0
    assert result.errors is None or len(result.errors) == 0


def test_translate_source_with_solution():
    """Test translating problem with solution."""
    pg_source = """
BEGIN_PGML
What is 2 + 2?

Answer: [_____]
END_PGML

evaluator = num_cmp(4)
ANS(evaluator)

BEGIN_PGML_SOLUTION
The answer is 4.
END_PGML_SOLUTION
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=123)

    assert result.statement_html != ""
    assert result.solution_html is not None
    assert "answer is 4" in result.solution_html


def test_translate_source_with_hint():
    """Test translating problem with hint."""
    pg_source = """
BEGIN_PGML
What is 2 + 2?
END_PGML

BEGIN_PGML_HINT
Think about basic addition.
END_PGML_HINT
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=123)

    assert result.statement_html != ""
    assert result.hint_html is not None
    assert "basic addition" in result.hint_html


def test_translate_source_with_answer_checking():
    """Test translating and checking answers."""
    pg_source = """
BEGIN_PGML
What is 5 + 5?

Answer: [_____]
END_PGML

evaluator = num_cmp(10)
ANS(evaluator, "sum")
"""

    translator = PGTranslator()

    # Correct answer
    result = translator.translate_source(pg_source, seed=123, inputs={"sum": "10"})

    assert result.answer_results is not None
    assert "sum" in result.answer_results
    assert result.answer_results["sum"].correct is True
    assert result.score == 1.0

    # Incorrect answer
    result = translator.translate_source(pg_source, seed=123, inputs={"sum": "11"})

    assert result.answer_results is not None
    assert "sum" in result.answer_results
    assert result.answer_results["sum"].correct is False
    assert result.score == 0.0


def test_translate_file():
    """Test translating from file."""
    pg_source = """
BEGIN_PGML
Test problem from file.
END_PGML
"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pg', delete=False) as f:
        f.write(pg_source)
        temp_path = f.name

    try:
        translator = PGTranslator()
        result = translator.translate(temp_path, seed=123)

        assert result.statement_html != ""
        assert "Test problem from file" in result.statement_html
    finally:
        # Clean up
        Path(temp_path).unlink()


def test_translate_file_not_found():
    """Test translating non-existent file."""
    translator = PGTranslator()
    result = translator.translate("/nonexistent/file.pg", seed=123)

    assert result.errors is not None
    assert len(result.errors) > 0
    assert "not found" in result.errors[0].lower()


def test_translate_syntax_error():
    """Test translating code with syntax error."""
    pg_source = """
this is not valid python syntax
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=123)

    assert result.errors is not None
    assert len(result.errors) > 0


def test_translate_runtime_error():
    """Test translating code with runtime error."""
    pg_source = """
x = undefined_variable
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=123)

    assert result.errors is not None
    assert len(result.errors) > 0


def test_translate_multiple_answers():
    """Test translating problem with multiple answers."""
    pg_source = """
BEGIN_PGML
Question 1: [_____]

Question 2: [_____]
END_PGML

ANS(num_cmp(5), "q1")
ANS(num_cmp(10), "q2")
"""

    translator = PGTranslator()

    # Check both correct
    result = translator.translate_source(
        pg_source,
        seed=123,
        inputs={"q1": "5", "q2": "10"}
    )

    assert result.score == 1.0

    # Check partial credit
    result = translator.translate_source(
        pg_source,
        seed=123,
        inputs={"q1": "5", "q2": "11"}  # q2 wrong
    )

    assert result.score == 0.5  # Average of 1.0 and 0.0


def test_translate_metadata():
    """Test that metadata is populated."""
    pg_source = """
BEGIN_PGML
Test problem.
END_PGML

ANS(num_cmp(42))
ANS(num_cmp(43))
"""

    translator = PGTranslator()
    result = translator.translate_source(pg_source, seed=456)

    assert result.metadata is not None
    assert result.metadata["seed"] == 456
    assert result.metadata["num_answers"] == 2
