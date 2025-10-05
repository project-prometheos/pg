from textwrap import dedent

import pytest

from pg_translator.pg_preprocessor_pygment import PGPreprocessor, PreprocessResult


def _preprocess(source: str, **kwargs) -> PreprocessResult:
    preprocessor = PGPreprocessor()
    return preprocessor.preprocess(dedent(source), **kwargs)


def test_pygment_preprocess_text_block():
    result = _preprocess(
        """
        $a = 2
        BEGIN_TEXT
        The value is $a.
        END_TEXT
        """
    )

    assert "a = 2" in result.code
    # TEXT blocks are now transformed into inline Python function calls
    assert "TEXT(" in result.code
    assert "str(a)" in result.code
    assert result.text_blocks == [("TEXT", "The value is $a.")]


def test_pygment_preprocess_pgml_blocks():
    result = _preprocess(
        """
        BEGIN_PGML
        PGML content [$a]
        END_PGML
        BEGIN_PGML_SOLUTION
        PGML solution [$a]
        END_PGML_SOLUTION
        """
    )

    # PGML blocks are stored in variables and rendered at runtime
    assert "pgml_block_0" in result.code
    assert "TEXT(PGML(pgml_block_0))" in result.code
    assert "pgml_block_1" in result.code
    assert "SOLUTION(PGML(pgml_block_1))" in result.code
    assert result.text_blocks == [("PGML", "PGML content [$a]"), ("PGML_SOLUTION", "PGML solution [$a]")]


def test_pygment_preprocess_without_lark():
    source = dedent(
        """
        do {
            $i = $i + 1;
        } until ($i > 3);
        """
    )

    preprocessor = PGPreprocessor()
    preprocessor._parser = None
    preprocessor._transformer = None

    result = preprocessor.preprocess(source)

    # New format: do-until converts to while True with break condition
    assert "while True:" in result.code
    assert "if (i > 3):" in result.code
    assert "break" in result.code
    assert "$i" not in result.code

