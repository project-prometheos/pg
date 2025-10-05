"""
Tests for PGML (PG Markup Language) parser and renderer.

Tests Week 3 Day 2 functionality.
"""

import pytest

from pg_translator.pgml_parser import (
    AnswerBlankNode,
    BoldNode,
    HeadingNode,
    ItalicNode,
    LineBreakNode,
    ListNode,
    MathNode,
    ParNode,
    PGMLParser,
    PGMLRenderer,
    RuleNode,
    TextNode,
    VariableNode,
)


class TestPGMLParser:
    """Test PGML parser."""

    def test_parse_plain_text(self):
        """Test parsing plain text."""
        parser = PGMLParser()
        doc = parser.parse("Hello, world!")

        assert len(doc.nodes) == 1
        assert isinstance(doc.nodes[0], TextNode)
        assert doc.nodes[0].text == "Hello, world!"

    def test_parse_variable(self):
        """Test variable interpolation."""
        parser = PGMLParser()
        doc = parser.parse("The answer is [$ans].")

        assert len(doc.nodes) >= 3
        # Find the variable node
        var_nodes = [n for n in doc.nodes if isinstance(n, VariableNode)]
        assert len(var_nodes) == 1
        assert var_nodes[0].var_name == "ans"

    def test_parse_answer_blank_simple(self):
        """Test simple answer blank."""
        parser = PGMLParser()
        doc = parser.parse("[_]{$answer}")

        blank_nodes = [n for n in doc.nodes if isinstance(n, AnswerBlankNode)]
        assert len(blank_nodes) == 1
        assert blank_nodes[0].evaluator_expr == "$answer"
        assert blank_nodes[0].width == 20  # default

    def test_parse_answer_blank_with_width(self):
        """Test answer blank with custom width."""
        parser = PGMLParser()
        doc = parser.parse("[___]{$answer}{30}")

        blank_nodes = [n for n in doc.nodes if isinstance(n, AnswerBlankNode)]
        assert len(blank_nodes) == 1
        assert blank_nodes[0].width == 30

    def test_parse_inline_math(self):
        """Test inline math."""
        parser = PGMLParser()
        doc = parser.parse("Calculate [`x^2 + 1`].")

        math_nodes = [n for n in doc.nodes if isinstance(n, MathNode)]
        assert len(math_nodes) == 1
        assert math_nodes[0].math == "x^2 + 1"
        assert not math_nodes[0].display

    def test_parse_display_math(self):
        """Test display math."""
        parser = PGMLParser()
        doc = parser.parse("[``x^2 + y^2 = z^2``]")

        math_nodes = [n for n in doc.nodes if isinstance(n, MathNode)]
        assert len(math_nodes) == 1
        assert math_nodes[0].math == "x^2 + y^2 = z^2"
        assert math_nodes[0].display

    def test_parse_bold_double_star(self):
        """Test bold with double asterisk."""
        parser = PGMLParser()
        doc = parser.parse("This is **bold** text.")

        bold_nodes = [n for n in doc.nodes if isinstance(n, BoldNode)]
        assert len(bold_nodes) == 1
        assert len(bold_nodes[0].children) == 1
        assert bold_nodes[0].children[0].text == "bold"

    def test_parse_bold_single_star(self):
        """Test bold with single asterisk."""
        parser = PGMLParser()
        doc = parser.parse("This is *bold* text.")

        bold_nodes = [n for n in doc.nodes if isinstance(n, BoldNode)]
        assert len(bold_nodes) == 1

    def test_parse_italic(self):
        """Test italic with underscore."""
        parser = PGMLParser()
        doc = parser.parse("This is _italic_ text.")

        italic_nodes = [n for n in doc.nodes if isinstance(n, ItalicNode)]
        assert len(italic_nodes) == 1

    def test_parse_heading_level1(self):
        """Test level 1 heading."""
        parser = PGMLParser()
        doc = parser.parse("# Main Heading")

        heading_nodes = [n for n in doc.nodes if isinstance(n, HeadingNode)]
        assert len(heading_nodes) == 1
        assert heading_nodes[0].level == 1

    def test_parse_heading_level3(self):
        """Test level 3 heading."""
        parser = PGMLParser()
        doc = parser.parse("### Sub-heading")

        heading_nodes = [n for n in doc.nodes if isinstance(n, HeadingNode)]
        assert len(heading_nodes) == 1
        assert heading_nodes[0].level == 3

    def test_parse_horizontal_rule(self):
        """Test horizontal rule."""
        parser = PGMLParser()
        doc = parser.parse("---")

        rule_nodes = [n for n in doc.nodes if isinstance(n, RuleNode)]
        assert len(rule_nodes) == 1

    def test_parse_paragraph_break(self):
        """Test paragraph breaks."""
        parser = PGMLParser()
        doc = parser.parse("Paragraph 1\n\nParagraph 2")

        par_nodes = [n for n in doc.nodes if isinstance(n, ParNode)]
        assert len(par_nodes) == 1

    def test_parse_list_bullet(self):
        """Test bullet list."""
        parser = PGMLParser()
        doc = parser.parse("+ Item 1\n+ Item 2\n+ Item 3")

        list_nodes = [n for n in doc.nodes if isinstance(n, ListNode)]
        assert len(list_nodes) == 1
        assert len(list_nodes[0].items) == 3


class TestPGMLRenderer:
    """Test PGML renderer."""

    def test_render_plain_text(self):
        """Test rendering plain text."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("Hello, world!")
        html = renderer.render(doc)

        assert "Hello, world!" in html

    def test_render_variable(self):
        """Test variable substitution."""
        context = {"ans": 42}
        renderer = PGMLRenderer(context=context)
        doc = PGMLParser().parse("The answer is [$ans].")
        html = renderer.render(doc)

        assert "42" in html

    def test_render_answer_blank(self):
        """Test answer blank rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("[_]{$answer}")
        html = renderer.render(doc)

        assert '<input type="text"' in html
        assert 'name="AnSwEr0001"' in html
        assert 'size="20"' in html

    def test_render_answer_blank_custom_width(self):
        """Test answer blank with custom width."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("[___]{$answer}{30}")
        html = renderer.render(doc)

        assert 'size="30"' in html

    def test_render_multiple_answer_blanks(self):
        """Test multiple answer blanks get unique IDs."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("[_]{$a} and [_]{$b}")
        html = renderer.render(doc)

        assert "AnSwEr0001" in html
        assert "AnSwEr0002" in html

    def test_render_inline_math(self):
        """Test inline math rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("Calculate [`x^2`].")
        html = renderer.render(doc)

        assert "\\(x^2\\)" in html

    def test_render_display_math(self):
        """Test display math rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("[``x^2 + y^2 = 1``]")
        html = renderer.render(doc)

        assert "\\[x^2 + y^2 = 1\\]" in html

    def test_render_bold(self):
        """Test bold rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("This is **bold** text.")
        html = renderer.render(doc)

        assert "<b>bold</b>" in html

    def test_render_italic(self):
        """Test italic rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("This is _italic_ text.")
        html = renderer.render(doc)

        assert "<i>italic</i>" in html

    def test_render_heading(self):
        """Test heading rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("# Main Heading")
        html = renderer.render(doc)

        assert "<h1>" in html and "</h1>" in html

    def test_render_horizontal_rule(self):
        """Test horizontal rule rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("---")
        html = renderer.render(doc)

        assert "<hr />" in html

    def test_render_list(self):
        """Test list rendering."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("+ Item 1\n+ Item 2")
        html = renderer.render(doc)

        assert "<ul>" in html
        assert "<li>Item 1</li>" in html
        assert "<li>Item 2</li>" in html
        assert "</ul>" in html

    def test_html_escaping(self):
        """Test HTML special characters are escaped."""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse("Use < and > symbols.")
        html = renderer.render(doc)

        assert "&lt;" in html
        assert "&gt;" in html


class TestPGMLIntegration:
    """Integration tests with real PGML examples."""

    def test_simple_problem(self):
        """Test simple problem with answer blank."""
        pgml = """
**Problem 1.** Calculate \\(\\tan\\!\\left(\\frac{23\\pi}{6}\\right)\\).

[_]{$ans}
"""
        context = {"ans": "-sqrt(3)/3"}
        renderer = PGMLRenderer(context=context)
        doc = PGMLParser().parse(pgml)
        html = renderer.render(doc)

        assert "<b>Problem 1.</b>" in html
        assert '<input type="text"' in html

    def test_multiple_answers(self):
        """Test problem with multiple answer blanks."""
        pgml = """
Determine all solutions:

[_]{$A} <= [_]{$B}
"""
        context = {"A": "pi/6", "B": "7pi/6"}
        renderer = PGMLRenderer(context=context)
        doc = PGMLParser().parse(pgml)
        html = renderer.render(doc)

        assert "AnSwEr0001" in html
        assert "AnSwEr0002" in html

    def test_math_and_formatting(self):
        """Test mixed math and formatting."""
        pgml = """
Enter your answers as simplified fractions.

+ [`\\cos(\\pi) =`] [_]{$answer1}{15}

+ [`\\sin(\\pi / 3) =`] [_]{$answer2}{15}
"""
        renderer = PGMLRenderer()
        doc = PGMLParser().parse(pgml)
        html = renderer.render(doc)

        # Check for inline math (using single backslash for LaTeX delimiters)
        assert r"\(" in html and r"\)" in html
        assert "cos" in html
        assert "<ul>" in html
        assert "<li>" in html
        assert 'size="15"' in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
