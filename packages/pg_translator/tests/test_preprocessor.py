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

    assert "pg_block_0" in result.code
    assert "pg_env.add_text(pg_block_0)" in result.code
    assert "The value is $a." in result.code


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

    assert "pg_block_0" in result.code
    assert "pg_env.add_pgml_text(pg_block_0)" in result.code
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

    assert "pg_block_0" in result.code
    assert "pg_env.add_solution(pg_block_0)" in result.code
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

    assert "pg_block_0" in result.code
    assert "pg_env.add_pgml_solution(pg_block_0)" in result.code
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
    assert "pg_block_0" in result.code
    assert "pg_block_1" in result.code
    assert "pg_env.add_pgml_text(pg_block_0)" in result.code
    assert "pg_env.add_pgml_solution(pg_block_1)" in result.code


def test_preprocess_regular_code():
    """Test that regular code passes through."""
    pg_source = """
$a = 10
$b = 20
$c = $a + $b
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # Should preserve regular code
    assert "$a = 10" in result.code
    assert "$b = 20" in result.code
    assert "$c = $a + $b" in result.code


def test_preprocess_escape_triple_quotes():
    """Test escaping triple quotes in text blocks."""
    pg_source = """
BEGIN_TEXT
This has '''triple quotes''' inside.
END_TEXT
"""

    preprocessor = PGPreprocessor()
    result = preprocessor.preprocess(pg_source)

    # Should escape triple quotes
    assert r"\'\'\'triple quotes\'\'\'" in result.code


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
