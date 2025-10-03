"""Tests for PGML solution and hint sections."""

import pytest
from pg_pgml import PGMLParser, HTMLRenderer, TeXRenderer
from pg_pgml.tokenizer import PGMLTokenizer, TokenType


def test_tokenize_solution():
    """Test tokenizing solution section."""
    text = """
BEGIN_PGML_SOLUTION
This is the solution.
END_PGML_SOLUTION
"""
    tokenizer = PGMLTokenizer(text.strip())
    tokens = tokenizer.tokenize()
    
    sol_tokens = [t for t in tokens if 'SOLUTION' in t.type.name]
    assert len(sol_tokens) == 2  # START and END


def test_tokenize_hint():
    """Test tokenizing hint section."""
    text = """
BEGIN_PGML_HINT
This is a hint.
END_PGML_HINT
"""
    tokenizer = PGMLTokenizer(text.strip())
    tokens = tokenizer.tokenize()
    
    hint_tokens = [t for t in tokens if 'HINT' in t.type.name]
    assert len(hint_tokens) == 2


def test_parse_solution():
    """Test parsing solution section."""
    text = """
BEGIN_PGML_SOLUTION
The answer is 42.
END_PGML_SOLUTION
"""
    doc = PGMLParser.parse_text(text.strip())
    
    assert len(doc.blocks) == 1
    solution = doc.blocks[0]
    assert hasattr(solution, 'content')
    assert len(solution.content) > 0


def test_parse_hint():
    """Test parsing hint section."""
    text = """
BEGIN_PGML_HINT
Try factoring first.
END_PGML_HINT
"""
    doc = PGMLParser.parse_text(text.strip())
    
    assert len(doc.blocks) == 1
    hint = doc.blocks[0]
    assert hasattr(hint, 'content')


def test_render_solution_html():
    """Test rendering solution to HTML."""
    text = """
BEGIN_PGML_SOLUTION
The answer is 42.
END_PGML_SOLUTION
"""
    doc = PGMLParser.parse_text(text.strip())
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert 'solution' in html.lower()
    assert '42' in html


def test_render_hint_html():
    """Test rendering hint to HTML."""
    text = """
BEGIN_PGML_HINT
Try factoring.
END_PGML_HINT
"""
    doc = PGMLParser.parse_text(text.strip())
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert 'hint' in html.lower()
    assert 'factoring' in html


def test_solution_with_math():
    """Test solution with math content."""
    text = """
BEGIN_PGML_SOLUTION
The derivative is [``2x``].
END_PGML_SOLUTION
"""
    doc = PGMLParser.parse_text(text.strip())
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert 'solution' in html.lower()
    assert 'derivative' in html


def test_problem_with_solution():
    """Test complete problem with solution."""
    text = """
What is 2 + 2?

Answer: [_____]

BEGIN_PGML_SOLUTION
2 + 2 = 4
END_PGML_SOLUTION
"""
    doc = PGMLParser.parse_text(text.strip())
    assert len(doc.blocks) >= 2  # Problem + solution


def test_problem_with_hint_and_solution():
    """Test problem with both hint and solution."""
    text = """
Solve x^2 = 4

BEGIN_PGML_HINT
Consider both positive and negative roots.
END_PGML_HINT

BEGIN_PGML_SOLUTION
x = ±2
END_PGML_SOLUTION
"""
    doc = PGMLParser.parse_text(text.strip())
    
    # Should have problem, hint, and solution
    blocks = doc.blocks
    assert len(blocks) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

