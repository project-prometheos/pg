"""Tests for PGML tokenizer."""

import pytest

from pg_pgml.tokenizer import PGMLTokenizer, Token, TokenType


def test_tokenize_plain_text():
    """Test tokenizing plain text."""
    tokenizer = PGMLTokenizer("Hello world")
    tokens = tokenizer.tokenize()

    assert len(tokens) == 2  # text + EOF
    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Hello world"
    assert tokens[-1].type == TokenType.EOF


def test_tokenize_variable():
    """Test tokenizing variable interpolation."""
    tokenizer = PGMLTokenizer("Value: [$x]")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Value: "
    assert tokens[1].type == TokenType.VAR_START
    assert tokens[1].value == "[$"
    assert tokens[2].type == TokenType.TEXT
    assert tokens[2].value == "x"
    assert tokens[3].type == TokenType.VAR_END
    assert tokens[3].value == "]"


def test_tokenize_answer_blank():
    """Test tokenizing answer blank."""
    tokenizer = PGMLTokenizer("Answer: [_____]")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Answer: "
    assert tokens[1].type == TokenType.ANSWER_BLANK
    assert tokens[1].value == "[_____]"


def test_tokenize_code_execution():
    """Test tokenizing code execution."""
    tokenizer = PGMLTokenizer("[@ $result = 2 + 2 @]")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.CODE_START
    assert tokens[0].value == "[@"
    assert tokens[1].type == TokenType.TEXT
    assert tokens[1].value == " $result = 2 + 2 "
    assert tokens[2].type == TokenType.CODE_END
    assert tokens[2].value == "@]"


def test_tokenize_math_block():
    """Test tokenizing display math block."""
    tokenizer = PGMLTokenizer("[```x^2 + y^2 = r^2```]")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.MATH_BLOCK_START
    assert tokens[0].value == "[```"
    assert tokens[1].type == TokenType.TEXT
    assert tokens[1].value == "x^2 + y^2 = r^2"
    assert tokens[2].type == TokenType.MATH_BLOCK_END
    assert tokens[2].value == "```]"


def test_tokenize_math_inline():
    """Test tokenizing inline math."""
    tokenizer = PGMLTokenizer("The formula [``x^2``] is quadratic")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "The formula "
    assert tokens[1].type == TokenType.MATH_INLINE_START
    assert tokens[1].value == "[``"
    assert tokens[2].type == TokenType.TEXT
    assert tokens[2].value == "x^2"
    assert tokens[3].type == TokenType.MATH_INLINE_END
    assert tokens[3].value == "``]"


def test_tokenize_list_item():
    """Test tokenizing unordered list item."""
    tokenizer = PGMLTokenizer("[* First item]")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.LIST_ITEM
    assert tokens[0].value == "[* First item]"


def test_tokenize_ordered_list_item():
    """Test tokenizing ordered list item."""
    tokenizer = PGMLTokenizer("[1. First step]")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.ORDERED_ITEM
    assert tokens[0].value == "[1. First step]"


def test_tokenize_newlines():
    """Test tokenizing newlines and blank lines."""
    tokenizer = PGMLTokenizer("Line 1\nLine 2\n\nLine 3")
    tokens = tokenizer.tokenize()

    assert tokens[0].type == TokenType.TEXT
    assert tokens[0].value == "Line 1"
    assert tokens[1].type == TokenType.NEWLINE
    assert tokens[2].type == TokenType.TEXT
    assert tokens[2].value == "Line 2"
    assert tokens[3].type == TokenType.BLANK_LINE
    assert tokens[4].type == TokenType.TEXT
    assert tokens[4].value == "Line 3"


def test_tokenize_complex_document():
    """Test tokenizing a complex PGML document."""
    pgml = """
Solve for [$x]:

[```x^2 + [$a]x + [$b] = 0```]

Answer: [_____]

[* Hint: Use the quadratic formula
[* Remember to simplify
"""

    tokenizer = PGMLTokenizer(pgml)
    tokens = tokenizer.tokenize()

    # Check key tokens are present
    token_types = [t.type for t in tokens]
    assert TokenType.VAR_START in token_types
    assert TokenType.MATH_BLOCK_START in token_types
    assert TokenType.ANSWER_BLANK in token_types
    assert TokenType.LIST_ITEM in token_types


def test_line_column_tracking():
    """Test line and column tracking."""
    tokenizer = PGMLTokenizer("Line 1\n  [$x]")
    tokens = tokenizer.tokenize()

    # First token at line 1, column 1
    assert tokens[0].line == 1
    assert tokens[0].column == 1

    # Newline at line 1
    newline_token = next(t for t in tokens if t.type == TokenType.NEWLINE)
    assert newline_token.line == 1

    # Variable start at line 2, column 3 (after 2 spaces)
    var_token = next(t for t in tokens if t.type == TokenType.VAR_START)
    assert var_token.line == 2
    assert var_token.column == 3
