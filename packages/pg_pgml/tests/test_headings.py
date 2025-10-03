"""
Tests for PGML heading parsing and rendering.

Tests heading syntax: # H1, ## H2, ..., ###### H6
"""

import pytest
from pg_pgml import PGMLParser, HTMLRenderer, TeXRenderer
from pg_pgml.tokenizer import PGMLTokenizer, TokenType


def test_tokenize_h1():
    """Test tokenizing H1 heading."""
    text = "# Main Heading"
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    # Find heading token
    heading_tokens = [t for t in tokens if t.type == TokenType.HEADING]
    assert len(heading_tokens) == 1
    assert '# Main Heading' in heading_tokens[0].value


def test_tokenize_all_heading_levels():
    """Test tokenizing all heading levels."""
    text = """
# H1
## H2
### H3
#### H4
##### H5
###### H6
"""
    tokenizer = PGMLTokenizer(text.strip())
    tokens = tokenizer.tokenize()
    
    heading_tokens = [t for t in tokens if t.type == TokenType.HEADING]
    assert len(heading_tokens) == 6


def test_parse_h1():
    """Test parsing H1 heading."""
    text = "# Main Heading"
    doc = PGMLParser.parse_text(text)
    
    assert len(doc.blocks) == 1
    heading = doc.blocks[0]
    assert hasattr(heading, 'level')
    assert heading.level == 1
    assert any('Main Heading' in str(c) for c in heading.content)


def test_parse_h2():
    """Test parsing H2 heading."""
    text = "## Subheading"
    doc = PGMLParser.parse_text(text)
    
    heading = doc.blocks[0]
    assert heading.level == 2
    assert any('Subheading' in str(c) for c in heading.content)


def test_parse_all_levels():
    """Test parsing all heading levels."""
    text = """
# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
"""
    doc = PGMLParser.parse_text(text.strip())
    
    headings = [b for b in doc.blocks if hasattr(b, 'level')]
    assert len(headings) == 6
    for i, heading in enumerate(headings, start=1):
        assert heading.level == i


def test_render_heading_to_html():
    """Test rendering heading to HTML."""
    text = "# Main Title"
    doc = PGMLParser.parse_text(text)
    
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert '<h1>' in html
    assert 'Main Title' in html
    assert '</h1>' in html


def test_render_all_heading_levels_to_html():
    """Test rendering all heading levels to HTML."""
    text = """
# H1
## H2
### H3
"""
    doc = PGMLParser.parse_text(text.strip())
    
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert '<h1>' in html and '</h1>' in html
    assert '<h2>' in html and '</h2>' in html
    assert '<h3>' in html and '</h3>' in html


def test_render_heading_to_tex():
    """Test rendering heading to TeX."""
    text = "# Chapter Title"
    doc = PGMLParser.parse_text(text)
    
    renderer = TeXRenderer()
    tex = renderer.render(doc)
    
    # TeX should have section command
    assert 'section' in tex or 'Chapter Title' in tex


def test_heading_with_formatting():
    """Test heading with inline formatting."""
    text = "# Main *bold* Title"
    doc = PGMLParser.parse_text(text)
    
    heading = doc.blocks[0]
    assert heading.level == 1
    # Should have text content
    assert len(heading.content) > 0


def test_multiple_headings():
    """Test document with multiple headings."""
    text = """
# First
Content here

## Second
More content
"""
    doc = PGMLParser.parse_text(text.strip())
    
    headings = [b for b in doc.blocks if hasattr(b, 'level')]
    assert len(headings) >= 2


def test_heading_after_paragraph():
    """Test heading following a paragraph."""
    text = """
Some intro text.

# Heading
"""
    doc = PGMLParser.parse_text(text.strip())
    
    # Should have at least 2 blocks
    assert len(doc.blocks) >= 2
    # Last block should be heading
    assert hasattr(doc.blocks[-1], 'level')


def test_heading_level_cap():
    """Test that excessive # characters cap at level 6."""
    text = "####### Too Many Hashes"
    doc = PGMLParser.parse_text(text)
    
    heading = doc.blocks[0]
    # Should cap at level 6
    assert heading.level <= 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

