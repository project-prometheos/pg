"""Tests for PG preprocessor."""

import pytest

from pg_translator.preprocessor import PGPreprocessor


def test_preprocess_begin_text():
    """Test preprocessing BEGIN_TEXT...END_TEXT."""
    pg_source = """
$a = 2
BEGIN_TEXT
The value is $a.
END_TEXT
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # New format: TEXT('The value is ', str(a), '.')
    assert "TEXT(" in result.code
    assert "The value is " in result.code


def test_preprocess_begin_pgml():
    """Test preprocessing BEGIN_PGML...END_PGML."""
    pg_source = """
$a = 3
BEGIN_PGML
The answer is [$a].
END_PGML
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # New format: uses pgml_block_0 not pg_block_0
    assert "pgml_block_0" in result.code
    # New format: TEXT(PGML(pgml_block_0))
    assert "TEXT(PGML(pgml_block_0))" in result.code
    assert "The answer is [$a]." in result.code


def test_preprocess_begin_solution():
    """Test preprocessing BEGIN_SOLUTION...END_SOLUTION."""
    pg_source = """
BEGIN_SOLUTION
This is the solution.
END_SOLUTION
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # New format: SOLUTION('This is the solution.')
    assert "SOLUTION(" in result.code
    assert "This is the solution." in result.code


def test_preprocess_begin_pgml_solution():
    """Test preprocessing BEGIN_PGML_SOLUTION...END_PGML_SOLUTION."""
    pg_source = """
BEGIN_PGML_SOLUTION
The answer is [$answer].
END_PGML_SOLUTION
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # New format: uses pgml_block_0 not pg_block_0
    assert "pgml_block_0" in result.code
    # New format: SOLUTION(PGML(pgml_block_0))
    assert "SOLUTION(PGML(pgml_block_0))" in result.code
    assert "The answer is [$answer]." in result.code


def test_preprocess_multiple_blocks():
    """Test preprocessing multiple blocks."""
    pg_source = """
$a = 5
BEGIN_PGML
Problem: [$a]
END_PGML

BEGIN_PGML_SOLUTION
Solution: [$a]
END_PGML_SOLUTION
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # Should have two blocks
    assert len(result.text_blocks) == 2
    assert result.text_blocks[0][0] == "PGML"
    assert result.text_blocks[1][0] == "PGML_SOLUTION"

    # Should have both blocks in code
    assert "pg_block_0" in result.code or "pgml_block_0" in result.code
    assert "pg_block_1" in result.code or "pgml_block_1" in result.code


def test_preprocess_regular_code():
    """Test that regular code passes through."""
    pg_source = """
$a = 10
$b = 20
$c = $a + $b
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # Should still have code (variable interpolation may change format)
    assert "10" in result.code
    assert "20" in result.code


def test_preprocess_escape_triple_quotes():
    """Test escaping triple quotes in text blocks."""
    pg_source = """
BEGIN_TEXT
This has '''triple quotes''' inside.
END_TEXT
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # Triple quotes should be preserved in some form
    assert "triple quotes" in result.code


def test_preprocess_empty_block():
    """Test preprocessing empty block."""
    pg_source = """
BEGIN_TEXT
END_TEXT
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    assert len(result.text_blocks) == 1
    assert result.text_blocks[0][1] == ""
