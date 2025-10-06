"""
Tests for PGML table parsing and rendering.

Tests pipe-delimited table syntax: | cell1 | cell2 |
"""

import pytest
from pg_pgml import PGMLParser, HTMLRenderer, TeXRenderer
from pg_pgml.tokenizer import PGMLTokenizer, TokenType


def test_tokenize_simple_table():
    """Test tokenizing simple table."""
    text = """
| Header 1 | Header 2 |
| Cell 1 | Cell 2 |
"""
    tokenizer = PGMLTokenizer(text.strip())
    tokens = tokenizer.tokenize()
    
    # Find table tokens
    table_tokens = [t for t in tokens if 'TABLE' in t.type.name]
    assert len(table_tokens) >= 4  # At least 2 rows with start/end markers


def test_parse_simple_table():
    """Test parsing simple 2x2 table."""
    text = """
| Header 1 | Header 2 |
| Cell 1 | Cell 2 |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    # Should have a Table block
    assert len(doc.blocks) == 1
    table = doc.blocks[0]
    assert hasattr(table, 'rows')
    assert len(table.rows) == 2
    
    # First row
    row1 = table.rows[0]
    assert len(row1.cells) == 2
    assert any('Header 1' in str(cell) for cell in row1.cells[0])
    assert any('Header 2' in str(cell) for cell in row1.cells[1])
    
    # Second row
    row2 = table.rows[1]
    assert len(row2.cells) == 2
    assert any('Cell 1' in str(cell) for cell in row2.cells[0])
    assert any('Cell 2' in str(cell) for cell in row2.cells[1])


def test_parse_table_with_math():
    """Test table with math content."""
    text = """
| Formula | Value |
| [``x^2``] | 4 |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    table = doc.blocks[0]
    assert len(table.rows) == 2
    
    # Second row should have math inline in first cell
    row2 = table.rows[1]
    # Check that math content is present
    assert len(row2.cells[0]) > 0


def test_parse_table_with_variables():
    """Test table with variable interpolation."""
    text = """
| Name | Value |
| x | [$x] |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    table = doc.blocks[0]
    row2 = table.rows[1]
    # Should have variable node in second cell
    assert len(row2.cells[1]) > 0


def test_render_table_to_html():
    """Test rendering table to HTML."""
    text = """
| Header 1 | Header 2 |
| Cell 1 | Cell 2 |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert '<table' in html
    assert '<tr>' in html
    assert '<td>' in html
    assert 'Header 1' in html
    assert 'Header 2' in html
    assert 'Cell 1' in html
    assert 'Cell 2' in html


def test_render_table_to_tex():
    """Test rendering table to TeX."""
    text = """
| A | B |
| 1 | 2 |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    renderer = TeXRenderer()
    tex = renderer.render(doc)
    
    assert 'tabular' in tex or 'array' in tex
    assert 'A' in tex
    assert 'B' in tex


def test_table_with_three_columns():
    """Test table with three columns."""
    text = """
| Col 1 | Col 2 | Col 3 |
| A | B | C |
| D | E | F |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    table = doc.blocks[0]
    assert len(table.rows) == 3
    assert len(table.rows[0].cells) == 3
    assert len(table.rows[1].cells) == 3
    assert len(table.rows[2].cells) == 3


def test_table_with_empty_cells():
    """Test table with empty cells."""
    text = """
| A | |
| | B |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    table = doc.blocks[0]
    assert len(table.rows) == 2
    
    # First row: filled, empty
    assert len(table.rows[0].cells) == 2
    
    # Second row: empty, filled
    assert len(table.rows[1].cells) == 2


def test_multiple_tables():
    """Test multiple tables in one document."""
    text = """
| Table 1 A | Table 1 B |

| Table 2 A | Table 2 B |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    # Should have 2 tables
    tables = [b for b in doc.blocks if hasattr(b, 'rows')]
    assert len(tables) == 2


def test_table_with_code_blocks():
    """Test table cells with code execution."""
    class SimpleExecutor:
        def __init__(self, context):
            self.context = context
        def eval(self, code):
            try:
                return eval(code, {"__builtins__": {}}, self.context)
            except SyntaxError:
                exec(code, {"__builtins__": {}}, self.context)
                return None
    
    text = """
| Expression | Result |
| 2 + 3 | [@2 + 3@]* |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    executor = SimpleExecutor({})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    assert '<table' in html
    assert '5' in html  # Result of 2 + 3


def test_table_css_classes():
    """Test that table renders with appropriate CSS classes."""
    text = """
| A | B |
"""
    doc = PGMLParser.parse_text(text.strip())
    
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert 'pgml-table' in html or 'class="' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


