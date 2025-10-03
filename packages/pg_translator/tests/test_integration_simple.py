"""Simple integration tests for end-to-end workflow."""

import pytest
from pg_pgml import PGMLParser, HTMLRenderer
from pg_macros import load_macros


def test_pgml_with_code_execution():
    """Test PGML with code execution."""
    pgml_text = """
# Problem 1

Calculate [@2 + 3@]*

Answer: [_____]
"""
    
    class SimpleExecutor:
        def __init__(self):
            self.context = {}
        def eval(self, code):
            try:
                return eval(code, {"__builtins__": {}}, self.context)
            except SyntaxError:
                exec(code, {"__builtins__": {}}, self.context)
                return None
    
    doc = PGMLParser.parse_text(pgml_text)
    executor = SimpleExecutor()
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    assert "5" in html
    assert "h1" in html
    assert "input" in html


def test_pgml_with_table_and_code():
    """Test PGML with table containing code."""
    pgml_text = """
| Expression | Result |
| 2 + 2 | [@2 + 2@]* |
| 3 * 4 | [@3 * 4@]* |
"""
    
    class SimpleExecutor:
        def __init__(self):
            self.context = {}
        def eval(self, code):
            return eval(code, {"__builtins__": {}}, self.context)
    
    doc = PGMLParser.parse_text(pgml_text)
    executor = SimpleExecutor()
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    assert "<table" in html
    assert "4" in html  # 2+2
    assert "12" in html  # 3*4


def test_macro_loading_integration():
    """Test loading and using macros."""
    macros = load_macros("PGstandard.pl")
    
    TEXT = macros["TEXT"]
    random = macros["random"]
    
    # Should work
    text = TEXT("Hello ", "World")
    assert text == "Hello World"
    
    # Random should generate number
    r = random(1, 10)
    assert 1 <= r <= 10


def test_choice_macros_integration():
    """Test choice macros."""
    macros = load_macros("PGchoicemacros.pl")
    
    new_multiple_choice = macros["new_multiple_choice"]
    mc = new_multiple_choice()
    mc.qa("What is 2+2?", "4")
    mc.extra("3", "5")
    
    q = mc.print_q()
    a = mc.print_a()
    
    assert "2+2" in q
    assert "4" in a
    assert "radio" in a


def test_complete_problem_flow():
    """Test complete problem with multiple features."""
    pgml_text = """
# Arithmetic Problem

## Question

Calculate the sum:

| A | B | Sum |
| 5 | 3 | [@5 + 3@]* |

What is [@7 + 2@]*?

Answer: [_____]

BEGIN_PGML_SOLUTION
7 + 2 = 9
END_PGML_SOLUTION

BEGIN_PGML_HINT
Add the numbers together.
END_PGML_HINT
"""
    
    class SimpleExecutor:
        def __init__(self):
            self.context = {}
        def eval(self, code):
            return eval(code, {"__builtins__": {}}, self.context)
    
    doc = PGMLParser.parse_text(pgml_text)
    executor = SimpleExecutor()
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # Should have all elements
    assert "<h1>" in html
    assert "<h2>" in html
    assert "<table" in html
    assert "8" in html  # 5+3
    assert "9" in html  # 7+2
    assert "input" in html
    assert "solution" in html.lower()
    assert "hint" in html.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

