"""
Tests for PGML code block execution.

Tests [@code@] and [@code@]* syntax with actual code execution.
"""

import pytest
from pg_pgml import PGMLParser, HTMLRenderer
from pg_pgml.tokenizer import PGMLTokenizer, TokenType


class SimpleExecutor:
    """Simple code executor for testing."""
    
    def __init__(self, context: dict):
        self.context = context
    
    def eval(self, code: str):
        """Execute code in context and return result."""
        # Try eval first (for expressions), fall back to exec (for statements)
        try:
            return eval(code, {"__builtins__": {}}, self.context)
        except SyntaxError:
            # If eval fails (e.g., for assignment statements), use exec
            exec(code, {"__builtins__": {}}, self.context)
            return None  # exec doesn't return a value


def test_tokenize_code_block_silent():
    """Test tokenizing [@code@] (silent code block)."""
    text = "The value is [@$a = 5@]."
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    # Find CODE tokens
    code_tokens = [t for t in tokens if t.type in (TokenType.CODE_START, TokenType.CODE_END)]
    assert len(code_tokens) == 2
    assert code_tokens[0].type == TokenType.CODE_START
    assert code_tokens[1].type == TokenType.CODE_END
    assert code_tokens[1].value == "@]"  # No * marker


def test_tokenize_code_block_display():
    """Test tokenizing [@code@]* (display result)."""
    text = "The value is [@2 + 3@]*."
    tokenizer = PGMLTokenizer(text)
    tokens = tokenizer.tokenize()
    
    # Find CODE tokens
    code_tokens = [t for t in tokens if t.type in (TokenType.CODE_START, TokenType.CODE_END)]
    assert len(code_tokens) == 2
    assert code_tokens[0].type == TokenType.CODE_START
    assert code_tokens[1].type == TokenType.CODE_END
    assert code_tokens[1].value == "@]*"  # Has * marker


def test_parse_code_block_silent():
    """Test parsing silent code block."""
    text = "Value: [@x = 10@]"
    doc = PGMLParser.parse_text(text)
    
    # Find Code node
    paragraph = doc.blocks[0]
    code_nodes = [node for node in paragraph.content if hasattr(node, 'code')]
    assert len(code_nodes) == 1
    assert code_nodes[0].code == "x = 10"
    assert code_nodes[0].display_result is False  # No * means don't display


def test_parse_code_block_display():
    """Test parsing display code block."""
    text = "Value: [@x + 5@]*"
    doc = PGMLParser.parse_text(text)
    
    # Find Code node
    paragraph = doc.blocks[0]
    code_nodes = [node for node in paragraph.content if hasattr(node, 'code')]
    assert len(code_nodes) == 1
    assert code_nodes[0].code == "x + 5"
    assert code_nodes[0].display_result is True  # Has * means display


def test_render_code_block_no_executor():
    """Test rendering without executor shows placeholder."""
    text = "Value: [@2 + 3@]*"
    doc = PGMLParser.parse_text(text)
    
    renderer = HTMLRenderer()
    html = renderer.render(doc)
    
    assert "[code result]" in html or "data-code" in html


def test_render_code_block_simple_expression():
    """Test executing and rendering simple expression."""
    text = "The answer is [@2 + 3@]*."
    doc = PGMLParser.parse_text(text)
    
    executor = SimpleExecutor({})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    assert "5" in html
    assert "The answer is" in html


def test_render_code_block_with_variables():
    """Test code execution with variables from context."""
    text = "The sum is [@a + b@]*."
    doc = PGMLParser.parse_text(text)
    
    executor = SimpleExecutor({"a": 10, "b": 20})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    assert "30" in html


def test_render_code_block_silent():
    """Test silent code block doesn't display result."""
    text = "Start [@x = 42@] End"
    doc = PGMLParser.parse_text(text)
    
    executor = SimpleExecutor({})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # Silent code should not show result
    assert "42" not in html or html.count("42") == 0
    assert "Start" in html
    assert "End" in html


def test_render_code_block_with_side_effects():
    """Test code block with side effects."""
    text = "[@x = 5@] The value is [@x * 2@]*."
    doc = PGMLParser.parse_text(text)
    
    context = {}
    executor = SimpleExecutor(context)
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # Second block should see x from first block
    assert "10" in html


def test_render_code_block_none_result():
    """Test code block returning None displays nothing."""
    text = "Value: [@None@]*"
    doc = PGMLParser.parse_text(text)
    
    executor = SimpleExecutor({})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # None should not display anything
    assert "None" not in html


def test_render_code_block_error_handling():
    """Test code block with error shows error message."""
    text = "Value: [@1 / 0@]*"
    doc = PGMLParser.parse_text(text)
    
    executor = SimpleExecutor({})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # Should show error indicator
    assert "error" in html.lower() or "[code" in html


def test_multiple_code_blocks():
    """Test multiple code blocks in same document sharing state."""
    text = """
    Set first: [@a = 10@]
    Set second: [@b = 20@]
    First: [@a@]*
    Second: [@b@]*
    Sum: [@a + b@]*
    """
    doc = PGMLParser.parse_text(text)
    
    context = {}
    executor = SimpleExecutor(context)
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # Silent assignments don't show, but later expressions do
    assert "10" in html
    assert "20" in html
    assert "30" in html


def test_code_block_with_math_result():
    """Test code block returning object with to_tex method."""
    # Mock a MathValue-like object
    class MockMathValue:
        def to_tex(self):
            return "3.14159"
        def __str__(self):
            return "3.14159"
    
    text = "Value: [@result@]*"
    doc = PGMLParser.parse_text(text)
    
    executor = SimpleExecutor({"result": MockMathValue()})
    renderer = HTMLRenderer(code_executor=executor)
    html = renderer.render(doc)
    
    # Should render as math
    assert "math-inline" in html
    assert "3.14" in html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

