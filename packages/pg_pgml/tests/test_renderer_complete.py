"""Test that renderers support all new features."""

import pytest
from pg_pgml import PGMLParser, HTMLRenderer, TeXRenderer


def test_html_renderer_all_features():
    """Test HTML renderer with all features."""
    pgml = """
# Main Heading

Some text with [@2+3@]*.

## Subheading

| Col1 | Col2 |
| A | B |

---

BEGIN_PGML_SOLUTION
Solution text
END_PGML_SOLUTION

BEGIN_PGML_HINT
Hint text
END_PGML_HINT
"""
    
    class Executor:
        def eval(self, code):
            return eval(code)
    
    doc = PGMLParser.parse_text(pgml.strip())
    renderer = HTMLRenderer(code_executor=Executor())
    html = renderer.render(doc)
    
    assert "<h1>" in html
    assert "<h2>" in html
    assert "<table" in html
    assert "<hr" in html
    assert "solution" in html.lower()
    assert "hint" in html.lower()
    assert "5" in html  # 2+3


def test_tex_renderer_all_features():
    """Test TeX renderer with all features."""
    pgml = """
# Heading

| A | B |
| 1 | 2 |

---

BEGIN_PGML_SOLUTION
Solution
END_PGML_SOLUTION
"""
    
    doc = PGMLParser.parse_text(pgml.strip())
    renderer = TeXRenderer()
    tex = renderer.render(doc)
    
    assert "section" in tex
    assert "tabular" in tex
    assert "hrulefill" in tex or "rule" in tex.lower()
    assert "solution" in tex.lower()


def test_all_node_types_render_html():
    """Test that all node types can render."""
    from pg_pgml.parser import (
        Document, Paragraph, Text, Variable, AnswerBlank,
        Code, MathInline, MathBlock, Bold, Italic,
        List, ListItem, Table, TableRow, Heading, Rule,
        Solution, Hint, AlignBlock, PreBlock
    )
    
    renderer = HTMLRenderer()
    
    # Test each node type
    assert renderer.visit_text(Text("hello")) == "hello"
    assert renderer.visit_bold(Bold([Text("bold")])) == "<strong>bold</strong>"
    assert renderer.visit_italic(Italic([Text("italic")])) == "<em>italic</em>"
    assert "<h1>" in renderer.visit_heading(Heading(1, [Text("H1")]))
    assert "<hr" in renderer.visit_rule(Rule())
    assert "table" in renderer.visit_table(Table([TableRow([[Text("A")]])]))
    assert "solution" in renderer.visit_solution(Solution([Paragraph([Text("sol")])])).lower()
    assert "hint" in renderer.visit_hint(Hint([Paragraph([Text("hint")])])).lower()


def test_all_node_types_render_tex():
    """Test that all node types can render in TeX."""
    from pg_pgml.parser import (
        Document, Paragraph, Text, Heading, Rule,
        Table, TableRow, Solution, Hint
    )
    
    renderer = TeXRenderer()
    
    assert "section" in renderer.visit_heading(Heading(1, [Text("H1")]))
    assert "hrulefill" in renderer.visit_rule(Rule())
    assert "tabular" in renderer.visit_table(Table([TableRow([[Text("A")]])]))
    assert "Solution" in renderer.visit_solution(Solution([Paragraph([Text("sol")])]))
    assert "Hint" in renderer.visit_hint(Hint([Paragraph([Text("hint")])]))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


