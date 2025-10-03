"""Tests for PGML parser."""

import pytest

from pg_pgml.parser import (
    AnswerBlank,
    Bold,
    Document,
    Italic,
    List,
    ListItem,
    MathBlock,
    MathInline,
    PGMLParser,
    Paragraph,
    Text,
    Variable,
)


def test_parse_plain_text():
    """Test parsing plain text into paragraph."""
    doc = PGMLParser.parse_text("Hello world")

    assert isinstance(doc, Document)
    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], Paragraph)

    para = doc.blocks[0]
    assert len(para.content) == 1
    assert isinstance(para.content[0], Text)
    assert para.content[0].content == "Hello world"


def test_parse_variable():
    """Test parsing variable interpolation."""
    doc = PGMLParser.parse_text("Value: [$x]")

    para = doc.blocks[0]
    assert len(para.content) == 2
    assert isinstance(para.content[0], Text)
    assert para.content[0].content == "Value: "
    assert isinstance(para.content[1], Variable)
    assert para.content[1].name == "x"


def test_parse_answer_blank():
    """Test parsing answer blank."""
    doc = PGMLParser.parse_text("Answer: [_____]")

    para = doc.blocks[0]
    assert len(para.content) == 2
    assert isinstance(para.content[0], Text)
    assert isinstance(para.content[1], AnswerBlank)
    assert para.content[1].width == 5


def test_parse_math_block():
    """Test parsing display math block."""
    doc = PGMLParser.parse_text("[```x^2 + y^2 = r^2```]")

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], MathBlock)
    assert doc.blocks[0].content == "x^2 + y^2 = r^2"


def test_parse_math_inline():
    """Test parsing inline math."""
    doc = PGMLParser.parse_text("The formula [``x^2``] is quadratic")

    para = doc.blocks[0]
    assert len(para.content) == 3
    assert isinstance(para.content[0], Text)
    assert isinstance(para.content[1], MathInline)
    assert para.content[1].content == "x^2"
    assert isinstance(para.content[2], Text)


def test_parse_unordered_list():
    """Test parsing unordered list."""
    pgml = """
[* First item
[* Second item
[* Third item
"""

    doc = PGMLParser.parse_text(pgml)

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], List)
    assert not doc.blocks[0].ordered

    lst = doc.blocks[0]
    assert len(lst.items) == 3
    assert isinstance(lst.items[0], ListItem)
    assert lst.items[0].content[0].content == "First item"


def test_parse_ordered_list():
    """Test parsing ordered list."""
    pgml = """
[1. First step
[2. Second step
[3. Third step
"""

    doc = PGMLParser.parse_text(pgml)

    assert len(doc.blocks) == 1
    assert isinstance(doc.blocks[0], List)
    assert doc.blocks[0].ordered

    lst = doc.blocks[0]
    assert len(lst.items) == 3
    assert lst.items[0].content[0].content == "First step"


def test_parse_multiple_paragraphs():
    """Test parsing multiple paragraphs separated by blank lines."""
    pgml = """First paragraph.

Second paragraph.

Third paragraph."""

    doc = PGMLParser.parse_text(pgml)

    assert len(doc.blocks) == 3
    assert all(isinstance(block, Paragraph) for block in doc.blocks)
    assert doc.blocks[0].content[0].content == "First paragraph."
    assert doc.blocks[1].content[0].content == "Second paragraph."
    assert doc.blocks[2].content[0].content == "Third paragraph."


def test_parse_paragraph_with_single_newline():
    """Test that single newlines within paragraph become spaces."""
    pgml = """First line
second line"""

    doc = PGMLParser.parse_text(pgml)

    para = doc.blocks[0]
    assert len(para.content) == 3
    assert para.content[0].content == "First line"
    assert para.content[1].content == " "  # newline becomes space
    assert para.content[2].content == "second line"


def test_parse_complex_document():
    """Test parsing a complex PGML document."""
    pgml = """
Solve for [$x]:

[```x^2 + [$a]x + [$b] = 0```]

Answer: [_____]

[* Use the quadratic formula
[* Simplify your answer
"""

    doc = PGMLParser.parse_text(pgml)

    # Should have 4 blocks: paragraph, math block, paragraph with blank, list
    assert len(doc.blocks) == 4

    # First block: paragraph with variable
    assert isinstance(doc.blocks[0], Paragraph)
    para1 = doc.blocks[0]
    var_nodes = [n for n in para1.content if isinstance(n, Variable)]
    assert len(var_nodes) == 1
    assert var_nodes[0].name == "x"

    # Second block: math block with variables (not parsed inside math)
    assert isinstance(doc.blocks[1], MathBlock)

    # Third block: paragraph with answer blank
    assert isinstance(doc.blocks[2], Paragraph)
    para3 = doc.blocks[2]
    blank_nodes = [n for n in para3.content if isinstance(n, AnswerBlank)]
    assert len(blank_nodes) == 1

    # Fourth block: unordered list
    assert isinstance(doc.blocks[3], List)
    assert not doc.blocks[3].ordered
    assert len(doc.blocks[3].items) == 2


def test_parse_nested_formatting():
    """Test parsing nested formatting (variables in list items)."""
    pgml = "[* The value is [$x]"

    doc = PGMLParser.parse_text(pgml)

    lst = doc.blocks[0]
    assert isinstance(lst, List)
    item = lst.items[0]
    assert len(item.content) == 2
    assert isinstance(item.content[0], Text)
    assert isinstance(item.content[1], Variable)
    assert item.content[1].name == "x"


def test_parse_empty_document():
    """Test parsing empty document."""
    doc = PGMLParser.parse_text("")

    assert isinstance(doc, Document)
    assert len(doc.blocks) == 0


def test_parse_only_whitespace():
    """Test parsing document with only whitespace."""
    doc = PGMLParser.parse_text("\n\n\n\n")

    assert isinstance(doc, Document)
    # Only blank lines - should not create blocks
    assert len(doc.blocks) == 0


def test_parse_answer_blank_widths():
    """Test parsing answer blanks with different widths."""
    pgml = "Short [___] medium [_____] long [__________]"

    doc = PGMLParser.parse_text(pgml)

    para = doc.blocks[0]
    blanks = [n for n in para.content if isinstance(n, AnswerBlank)]
    assert len(blanks) == 3
    assert blanks[0].width == 3
    assert blanks[1].width == 5
    assert blanks[2].width == 10
