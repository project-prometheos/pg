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
            
            # Step 5: Format answers (propagate metadata if available)
            answers = {}
            for answer_id, spec in answer_blanks.items():
                if isinstance(spec, dict):
                    # Expect keys: correct_value, type, checker?, variables?
                    cv = spec.get('correct_value', '')
                    raw_type = spec.get('type') if 'type' in spec else None
                    raw_options = spec.get('options')
                    # If this answer belongs to a MultiAnswer group, mark as 'multi'
                    if 'group' in spec:
                        atype = 'multi'
                    else:
                        # Avoid evaluating type detection if 'type' already present
                        atype = raw_type if raw_type is not None else self._detect_answer_type(str(cv))
                    entry = {
                        'correct_value': cv,
                        'type': atype,
                    }
                    if 'checker' in spec:
                        entry['checker'] = spec['checker']
                    if 'variables' in spec:
                        entry['variables'] = spec['variables']
                    if raw_options is not None:
                        entry['options'] = dict(raw_options) if isinstance(raw_options, dict) else raw_options
                    if 'group' in spec:
                        entry['group'] = spec['group']
                        entry['part_type'] = raw_type if raw_type is not None else self._detect_answer_type(str(cv))
                    if 'group_index' in spec:
                        entry['group_index'] = spec['group_index']
                    answers[answer_id] = entry
                else:
                    answers[answer_id] = {
                        'correct_value': spec,
                        'type': self._detect_answer_type(str(spec))
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
    
    def _detect_answer_type(self, answer: str) -> str:
        """
        Detect the type of answer based on its content.
        
        Returns:
            'number', 'formula', 'interval', 'point', 'vector', or 'string'
        """
        answer_str = str(answer).strip()
        
        # Check for intervals: [a, b], (a, b), [a, b), (-inf, 5]
        if (answer_str.startswith('[') or answer_str.startswith('(')) and \
           (answer_str.endswith(']') or answer_str.endswith(')')):
            return 'interval'
        
        # Check for points/vectors: (x, y, z) or <x, y, z>
        if answer_str.startswith('(') and answer_str.endswith(')') and ',' in answer_str:
            return 'point'
        if answer_str.startswith('<') and answer_str.endswith('>'):
            return 'vector'
        
        # Check for inequalities: treat as formulas for parity; checker routes appropriately
        if any(op in answer_str for op in ['>=', '<=', '>', '<']) and \
           any(var in answer_str for var in ['x', 'y', 'z', 't', 'r', 'theta']):
            return 'formula'
        
        # Check if it's a simple number
        try:
            float(answer_str)
            return 'number'
        except (ValueError, TypeError):
            pass
        
        # Check if it contains mathematical operators or variables (formula)
        if any(char in answer_str for char in ['+', '-', '*', '/', '^', '(', ')']) or \
           any(var in answer_str.lower() for var in ['x', 'y', 'z', 't', 'sin', 'cos', 'sqrt']):
            return 'formula'
        
        # Default to string
        return 'string'


# Public API
__all__ = ['PGRenderer', 'PGProblem']

