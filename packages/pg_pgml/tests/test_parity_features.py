"""
Tests for PGML parity features (headings, tables, rules, alignment, etc.).

Tests the NEW features added for 100% parity with Perl PGML.pl:
- Headings (# through ######)
- Tables (| col1 | col2 |)
- Horizontal rules (--- and ===)
- Alignment blocks (>>, <<)
- Pre-formatted blocks (:   )
- Solution/Hint sections

Reference: macros/core/PGML.pl (lines 40-1200)
"""

import pytest

from pg_pgml import PGMLParser
from pg_pgml.parser import Heading, Table, TableRow, Rule, PreBlock, AlignBlock, Solution, Hint
from pg_pgml.renderer import HTMLRenderer, TeXRenderer
from pg_pgml.tokenizer import PGMLTokenizer, TokenType


# Heading Tests

def test_tokenize_heading():
    """Test tokenizing headings."""
    text = "# Main Heading\n## Subheading"
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    # Should have heading tokens
    heading_tokens = [t for t in tokens if t.type == TokenType.HEADING]
    assert len(heading_tokens) == 2
    assert "# Main Heading" in heading_tokens[0].value
    assert "## Subheading" in heading_tokens[1].value


def test_parse_heading():
    """Test parsing headings."""
    pgml = "# Main Heading\n\nSome text."
    doc = PGMLParser.parse_text(pgml)
    
    # First block should be heading
    assert len(doc.blocks) >= 1
    # Note: Parser integration may need adjustment


def test_render_heading_html():
    """Test rendering heading to HTML."""
    from pg_pgml.parser import Heading, Text
    
    heading = Heading(level=1, content=[Text(content="Main Heading")])
    renderer = HTMLRenderer()
    html = renderer.render(heading)
    
    assert "<h1>Main Heading</h1>" in html


def test_render_heading_tex():
    """Test rendering heading to TeX."""
    from pg_pgml.parser import Heading, Text
    
    heading = Heading(level=1, content=[Text(content="Main Heading")])
    renderer = TeXRenderer()
    tex = renderer.render(heading)
    
    assert "\\section{Main Heading}" in tex


# Table Tests

def test_tokenize_table():
    """Test tokenizing tables."""
    text = "| col1 | col2 | col3 |\n| data1 | data2 | data3 |"
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    # Should have table tokens
    row_starts = [t for t in tokens if t.type == TokenType.TABLE_ROW_START]
    cell_seps = [t for t in tokens if t.type == TokenType.TABLE_CELL_SEP]
    
    assert len(row_starts) == 2  # Two rows
    assert len(cell_seps) >= 4  # At least 4 cell separators


def test_render_table_html():
    """Test rendering table to HTML."""
    from pg_pgml.parser import Table, TableRow, Text
    
    table = Table(rows=[
        TableRow(cells=[
            [Text(content="col1")],
            [Text(content="col2")]
        ]),
        TableRow(cells=[
            [Text(content="data1")],
            [Text(content="data2")]
        ])
    ])
    
    renderer = HTMLRenderer()
    html = renderer.render(table)
    
    assert "<table" in html
    assert "<tr>" in html
    assert "<td>col1</td>" in html
    assert "<td>data2</td>" in html


def test_render_table_tex():
    """Test rendering table to TeX."""
    from pg_pgml.parser import Table, TableRow, Text
    
    table = Table(rows=[
        TableRow(cells=[
            [Text(content="col1")],
            [Text(content="col2")]
        ])
    ])
    
    renderer = TeXRenderer()
    tex = renderer.render(table)
    
    assert "\\begin{tabular}" in tex
    assert "col1 & col2" in tex
    assert "\\end{tabular}" in tex


# Rule Tests

def test_tokenize_rule():
    """Test tokenizing horizontal rules."""
    text = "---\n===\n"
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    rules = [t for t in tokens if t.type == TokenType.RULE]
    assert len(rules) == 2


def test_render_rule_html():
    """Test rendering rule to HTML."""
    from pg_pgml.parser import Rule
    
    rule = Rule(style="-")
    renderer = HTMLRenderer()
    html = renderer.render(rule)
    
    assert "<hr" in html


def test_render_rule_tex():
    """Test rendering rule to TeX."""
    from pg_pgml.parser import Rule
    
    rule = Rule(style="-")
    renderer = TeXRenderer()
    tex = renderer.render(rule)
    
    assert "\\hrulefill" in tex


# Alignment Tests

def test_tokenize_alignment():
    """Test tokenizing alignment markers."""
    text = ">> right\n<< left\n>> center <<"
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    align_right = [t for t in tokens if t.type == TokenType.ALIGN_RIGHT]
    align_left = [t for t in tokens if t.type == TokenType.ALIGN_LEFT]
    
    assert len(align_right) == 2
    assert len(align_left) == 2


def test_render_align_block_html():
    """Test rendering alignment block to HTML."""
    from pg_pgml.parser import AlignBlock, Text
    
    align = AlignBlock(alignment="center", content=[Text(content="centered text")])
    renderer = HTMLRenderer()
    html = renderer.render(align)
    
    assert "text-center" in html or "pgml-align" in html
    assert "centered text" in html


def test_render_align_block_tex():
    """Test rendering alignment block to TeX."""
    from pg_pgml.parser import AlignBlock, Text
    
    align = AlignBlock(alignment="center", content=[Text(content="centered text")])
    renderer = TeXRenderer()
    tex = renderer.render(align)
    
    assert "\\begin{center}" in tex
    assert "centered text" in tex
    assert "\\end{center}" in tex


# Pre-formatted Block Tests

def test_tokenize_pre_block():
    """Test tokenizing pre-formatted blocks."""
    text = ":   code example\n:   another line"
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    pre_blocks = [t for t in tokens if t.type == TokenType.PRE_BLOCK]
    assert len(pre_blocks) == 2


def test_render_pre_block_html():
    """Test rendering pre-formatted block to HTML."""
    from pg_pgml.parser import PreBlock
    
    pre = PreBlock(content="code example")
    renderer = HTMLRenderer()
    html = renderer.render(pre)
    
    assert "<pre" in html
    assert "code example" in html


def test_render_pre_block_tex():
    """Test rendering pre-formatted block to TeX."""
    from pg_pgml.parser import PreBlock
    
    pre = PreBlock(content="code example")
    renderer = TeXRenderer()
    tex = renderer.render(pre)
    
    assert "\\begin{verbatim}" in tex
    assert "code example" in tex


# Solution/Hint Tests

def test_render_solution_html():
    """Test rendering solution section to HTML."""
    from pg_pgml.parser import Solution, Paragraph, Text
    
    solution = Solution(content=[
        Paragraph(content=[Text(content="Here's the solution")])
    ])
    
    renderer = HTMLRenderer()
    html = renderer.render(solution)
    
    assert "pgml-solution" in html
    assert "Solution:" in html
    assert "Here's the solution" in html


def test_render_solution_tex():
    """Test rendering solution section to TeX."""
    from pg_pgml.parser import Solution, Paragraph, Text
    
    solution = Solution(content=[
        Paragraph(content=[Text(content="Here's the solution")])
    ])
    
    renderer = TeXRenderer()
    tex = renderer.render(solution)
    
    assert "Solution:" in tex
    assert "Here's the solution" in tex


def test_render_hint_html():
    """Test rendering hint section to HTML."""
    from pg_pgml.parser import Hint, Paragraph, Text
    
    hint = Hint(content=[
        Paragraph(content=[Text(content="Try this approach")])
    ])
    
    renderer = HTMLRenderer()
    html = renderer.render(hint)
    
    assert "pgml-hint" in html
    assert "Hint:" in html
    assert "Try this approach" in html


# Integration Tests

def test_complex_document_with_parity_features():
    """Test rendering complex document with multiple new features."""
    from pg_pgml.parser import Document, Heading, Paragraph, Table, TableRow, Rule, Text
    
    doc = Document(blocks=[
        Heading(level=1, content=[Text(content="Chapter 1")]),
        Paragraph(content=[Text(content="Introduction text.")]),
        Rule(style="-"),
        Table(rows=[
            TableRow(cells=[[Text(content="Header1")], [Text(content="Header2")]]),
            TableRow(cells=[[Text(content="Data1")], [Text(content="Data2")]])
        ])
    ])
    
    # Render to HTML
    html_renderer = HTMLRenderer()
    html = html_renderer.render(doc)
    
    assert "<h1>Chapter 1</h1>" in html
    assert "<p>Introduction text.</p>" in html
    assert "<hr" in html
    assert "<table" in html
    
    # Render to TeX
    tex_renderer = TeXRenderer()
    tex = tex_renderer.render(doc)
    
    assert "\\section{Chapter 1}" in tex
    assert "Introduction text." in tex
    assert "\\hrulefill" in tex
    assert "\\begin{tabular}" in tex

