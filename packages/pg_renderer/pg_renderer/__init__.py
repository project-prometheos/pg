"""Pure Python PG problem renderer."""

from typing import Dict, Any
from .parser import PGParser, PGProblem
from .evaluator import PGEvaluator
from .pgml import PGMLRenderer


class PGRenderer:
    """Main PG problem renderer."""
    
    def render(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """
        Render a PG problem to HTML with answer evaluators.
        
        Args:
            pg_source: Full PG file content
            seed: Random seed for problem variation
            
        Returns:
            {
                'statement_html': str,
                'inputs': List[str],
                'answers': Dict[str, Dict],
                'solution_html': str,
                'warnings': List[str],
                'errors': List[str]
            }
        """
        try:
            # Step 1: Parse PG file
            parser = PGParser()
            problem = parser.parse(pg_source)
            
            # Step 2: Execute setup code
            evaluator = PGEvaluator(seed=seed)
            variables = evaluator.evaluate(problem.setup)
            
            # Step 3: Render PGML
            pgml_renderer = PGMLRenderer(variables)
            statement_html, answer_blanks = pgml_renderer.render(problem.pgml)
            
            # Step 4: Render solution (if any)
            solution_html = ""
            if problem.solution:
                solution_renderer = PGMLRenderer(variables)
                solution_html, _ = solution_renderer.render(problem.solution)
            
            # Step 5: Format answers
            answers = {}
            for answer_id, correct_value in answer_blanks.items():
                answers[answer_id] = {
                    'correct_value': correct_value,
                    'type': 'number'
                }
            
            return {
                'statement_html': statement_html,
                'inputs': list(answer_blanks.keys()),
                'answers': answers,
                'solution_html': solution_html,
                'warnings': [],
                'errors': []
            }
            
        except Exception as e:
            import traceback
            return {
                'statement_html': f'<p class="error">Error rendering problem: {str(e)}</p>',
                'inputs': [],
                'answers': {},
                'solution_html': '',
                'warnings': [],
                'errors': [str(e), traceback.format_exc()]
            }


# Public API
__all__ = ['PGRenderer', 'PGProblem']

