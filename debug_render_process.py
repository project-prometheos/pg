#!/usr/bin/env python
"""
Debug the render process step by step.
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_renderer'))

def debug_render_process():
    """Debug the render process step by step."""
    
    # Load the problem
    with open('tutorial/sample-problems/Algebra/FractionAnswer.pg', 'r') as f:
        pg_source = f.read()
    
    # Parse the problem
    from pg_renderer.parser import PGParser
    parser = PGParser()
    problem = parser.parse(pg_source)
    
    # Execute setup code
    from pg_renderer.evaluator import PGEvaluator
    evaluator = PGEvaluator(seed=123)
    variables = evaluator.evaluate(problem.setup)
    
    # Create PGML renderer
    from pg_renderer.pgml import PGMLRenderer
    pgml_renderer = PGMLRenderer(variables)
    
    print("Before render:")
    print(f"  answer_blanks: {pgml_renderer.answer_blanks}")
    print()
    
    # Render step by step
    html = problem.pgml
    
    # Test the answer blank regex
    import re
    pattern = r'\[_+\]\{([^}]+)\}(?:\{[0-9]+\})?'
    
    def debug_create_answer_blank(match):
        print(f"_create_answer_blank called with: {match}")
        answer_expr = match.group(1)
        print(f"  answer_expr: {repr(answer_expr)}")
        
        # Call the actual method
        result = pgml_renderer._create_answer_blank(match)
        print(f"  result: {result}")
        print(f"  answer_blanks after: {pgml_renderer.answer_blanks}")
        return result
    
    # Apply the regex
    html = re.sub(pattern, debug_create_answer_blank, html)
    
    print(f"Final HTML: {html}")
    print(f"Final answer_blanks: {pgml_renderer.answer_blanks}")

if __name__ == "__main__":
    debug_render_process()
