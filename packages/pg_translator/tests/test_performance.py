"""Performance tests for PG rendering."""

import pytest
import time
from pg_pgml import PGMLParser, HTMLRenderer


def test_simple_problem_performance():
    """Test that simple problems render quickly."""
    pgml = """
# Problem

Calculate [@2 + 3@]*

Answer: [_____]
"""
    
    class SimpleExecutor:
        def eval(self, code):
            return eval(code)
    
    # Warm up
    doc = PGMLParser.parse_text(pgml.strip())
    renderer = HTMLRenderer(code_executor=SimpleExecutor())
    renderer.render(doc)
    
    # Measure
    start = time.time()
    for _ in range(100):
        doc = PGMLParser.parse_text(pgml.strip())
        renderer = HTMLRenderer(code_executor=SimpleExecutor())
        html = renderer.render(doc)
    end = time.time()
    
    avg_time = (end - start) / 100 * 1000  # ms
    
    assert avg_time < 10, f"Average time {avg_time}ms exceeds 10ms target"


def test_complex_problem_performance():
    """Test complex problem with all features."""
    pgml = """
# Main Heading

## Part A

| Col1 | Col2 | Col3 |
| [@1+1@]* | [@2+2@]* | [@3+3@]* |

## Part B

Calculate [@5 * 5@]*

BEGIN_PGML_SOLUTION
The answer is 25.
END_PGML_SOLUTION
"""
    
    class SimpleExecutor:
        def eval(self, code):
            return eval(code)
    
    doc = PGMLParser.parse_text(pgml.strip())
    renderer = HTMLRenderer(code_executor=SimpleExecutor())
    
    start = time.time()
    for _ in range(10):
        html = renderer.render(doc)
    end = time.time()
    
    avg_time = (end - start) / 10 * 1000
    
    # More complex, allow 100ms
    assert avg_time < 100, f"Average time {avg_time}ms exceeds 100ms target"


def test_parser_performance():
    """Test parser performance."""
    pgml = "Simple text " * 100
    
    start = time.time()
    for _ in range(100):
        doc = PGMLParser.parse_text(pgml)
    end = time.time()
    
    avg_time = (end - start) / 100 * 1000
    assert avg_time < 5, f"Parser time {avg_time}ms exceeds 5ms target"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


