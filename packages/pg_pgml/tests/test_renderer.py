"""Tests for PGML renderers."""

import pytest

from pg_pgml.parser import PGMLParser
from pg_pgml.renderer import HTMLRenderer, TeXRenderer


def test_html_render_plain_text():
    """Test HTML rendering of plain text."""
    doc = PGMLParser.parse_text("Hello world")
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert '<div class="pgml-document">' in html
    assert "<p>Hello world</p>" in html


def test_html_render_variable():
    """Test HTML rendering of variable interpolation."""
    doc = PGMLParser.parse_text("Value: [$x]")
    renderer = HTMLRenderer(context={"x": 42})
    html = renderer.render(doc)

    assert "Value: " in html
    assert '<span class="pgml-variable">42</span>' in html


def test_html_render_variable_mathvalue():
    """Test HTML rendering of MathValue variable."""
    from pg_math import Real

    doc = PGMLParser.parse_text("Result: [$answer]")
    renderer = HTMLRenderer(context={"answer": Real(3.14)})
    html = renderer.render(doc)

    assert "Result: " in html
    assert '<span class="pgml-variable">3.14</span>' in html


def test_html_render_answer_blank():
    """Test HTML rendering of answer blank."""
    doc = PGMLParser.parse_text("Answer: [_____]")
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert '<input type="text"' in html
    assert 'name="AnSwEr0001"' in html
    assert 'class="pgml-answer-blank"' in html
    assert 'size="5"' in html


def test_html_render_math_block():
    """Test HTML rendering of display math."""
    doc = PGMLParser.parse_text("[```x^2 + y^2 = r^2```]")
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert '<div class="math-block">\\[x^2 + y^2 = r^2\\]</div>' in html


def test_html_render_math_inline():
    """Test HTML rendering of inline math."""
    doc = PGMLParser.parse_text("The formula [``x^2``] is quadratic")
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert "The formula " in html
    assert '<span class="math-inline">\\(x^2\\)</span>' in html
    assert " is quadratic" in html


def test_html_render_list():
    """Test HTML rendering of unordered list."""
    pgml = """
[* First item
[* Second item
"""

    doc = PGMLParser.parse_text(pgml)
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert "<ul>" in html
    assert "<li>First item</li>" in html
    assert "<li>Second item</li>" in html
    assert "</ul>" in html


def test_html_render_ordered_list():
    """Test HTML rendering of ordered list."""
    pgml = """
[1. First step
[2. Second step
"""

    doc = PGMLParser.parse_text(pgml)
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert "<ol>" in html
    assert "<li>First step</li>" in html
    assert "<li>Second step</li>" in html
    assert "</ol>" in html


def test_html_render_multiple_paragraphs():
    """Test HTML rendering of multiple paragraphs."""
    pgml = """First paragraph.

Second paragraph."""

    doc = PGMLParser.parse_text(pgml)
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert html.count("<p>") == 2
    assert "<p>First paragraph.</p>" in html
    assert "<p>Second paragraph.</p>" in html


def test_html_escape_special_chars():
    """Test HTML escaping of special characters."""
    doc = PGMLParser.parse_text("Test: <script>alert('xss')</script>")
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_html_answer_counter():
    """Test HTML answer blank counter increments."""
    doc = PGMLParser.parse_text("First: [___] Second: [_____]")
    renderer = HTMLRenderer()
    html = renderer.render(doc)

    assert 'name="AnSwEr0001"' in html
    assert 'name="AnSwEr0002"' in html


def test_tex_render_plain_text():
    """Test TeX rendering of plain text."""
    doc = PGMLParser.parse_text("Hello world")
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "Hello world" in tex


def test_tex_render_variable():
    """Test TeX rendering of variable interpolation."""
    doc = PGMLParser.parse_text("Value: [$x]")
    renderer = TeXRenderer(context={"x": 42})
    tex = renderer.render(doc)

    assert "Value: 42" in tex


def test_tex_render_variable_mathvalue():
    """Test TeX rendering of MathValue variable."""
    from pg_math import Real

    doc = PGMLParser.parse_text("Result: [$answer]")
    renderer = TeXRenderer(context={"answer": Real(3.14)})
    tex = renderer.render(doc)

    assert "Result: 3.14" in tex


def test_tex_render_answer_blank():
    """Test TeX rendering of answer blank."""
    doc = PGMLParser.parse_text("Answer: [_____]")
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "Answer: \\underline{\\hspace{" in tex
    assert "em}}" in tex


def test_tex_render_math_block():
    """Test TeX rendering of display math."""
    doc = PGMLParser.parse_text("[```x^2 + y^2 = r^2```]")
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "\\[\nx^2 + y^2 = r^2\n\\]" in tex


def test_tex_render_math_inline():
    """Test TeX rendering of inline math."""
    doc = PGMLParser.parse_text("The formula [``x^2``] is quadratic")
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "The formula $x^2$ is quadratic" in tex


def test_tex_render_list():
    """Test TeX rendering of unordered list."""
    pgml = """
[* First item
[* Second item
"""

    doc = PGMLParser.parse_text(pgml)
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "\\begin{itemize}" in tex
    assert "\\item First item" in tex
    assert "\\item Second item" in tex
    assert "\\end{itemize}" in tex


def test_tex_render_ordered_list():
    """Test TeX rendering of ordered list."""
    pgml = """
[1. First step
[2. Second step
"""

    doc = PGMLParser.parse_text(pgml)
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "\\begin{enumerate}" in tex
    assert "\\item First step" in tex
    assert "\\item Second step" in tex
    assert "\\end{enumerate}" in tex


def test_tex_escape_special_chars():
    """Test TeX escaping of special characters."""
    doc = PGMLParser.parse_text("Test: $100 & 50% #1 _underscore")
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "\\$100" in tex
    assert "\\&" in tex
    assert "\\%" in tex
    assert "\\#1" in tex
    assert "\\_underscore" in tex


def test_tex_render_multiple_paragraphs():
    """Test TeX rendering of multiple paragraphs."""
    pgml = """First paragraph.

Second paragraph."""

    doc = PGMLParser.parse_text(pgml)
    renderer = TeXRenderer()
    tex = renderer.render(doc)

    assert "First paragraph." in tex
    assert "Second paragraph." in tex
    # Paragraphs separated by blank line in TeX
    assert "\n\n" in tex


def test_complex_document_html():
    """Test HTML rendering of complex document."""
    pgml = """
Solve for [$x]:

[```x^2 + 2x + 1 = 0```]

Answer: [_____]

[* Use the quadratic formula
[* Simplify
"""

    from pg_math import Real

    doc = PGMLParser.parse_text(pgml)
    renderer = HTMLRenderer(context={"x": Real(1)})
    html = renderer.render(doc)

    # Check all major elements present
    assert '<div class="pgml-document">' in html
    assert '<span class="pgml-variable">1</span>' in html
    assert '<div class="math-block">\\[x^2 + 2x + 1 = 0\\]</div>' in html
    assert '<input type="text"' in html
    assert "<ul>" in html
    assert "<li>Use the quadratic formula</li>" in html


def test_complex_document_tex():
    """Test TeX rendering of complex document."""
    pgml = """
Solve for [$x]:

[```x^2 + 2x + 1 = 0```]

Answer: [_____]

[* Use the quadratic formula
[* Simplify
"""

    from pg_math import Real

    doc = PGMLParser.parse_text(pgml)
    renderer = TeXRenderer(context={"x": Real(1)})
    tex = renderer.render(doc)

    # Check all major elements present
    assert "Solve for 1:" in tex
    assert "\\[\nx^2 + 2x + 1 = 0\n\\]" in tex
    assert "\\underline{\\hspace{" in tex
    assert "\\begin{itemize}" in tex
    assert "\\item Use the quadratic formula" in tex
