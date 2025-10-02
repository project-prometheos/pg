"""Python PG renderer service for backend."""

from typing import Dict, Any

# Import from installed package (editable mode)
# Package is installed with: pip install -e packages/pg_renderer
from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker


class PGRenderService:
    """Service for rendering PG problems using Python renderer."""
    
    def __init__(self):
        self.renderer = PGRenderer()
        self.checker = AnswerChecker(tolerance=0.01)
    
    def render_problem(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """Render a PG problem."""
        return self.renderer.render(pg_source, seed=seed)
    
    def check_answers(self, pg_source: str, seed: int, 
                     student_inputs: Dict[str, str]) -> Dict[str, Any]:
        """Check student answers for a problem."""
        # Render to get correct answers
        rendered = self.renderer.render(pg_source, seed=seed)
        
        results = {}
        for answer_id, student_answer in student_inputs.items():
            if answer_id in rendered['answers']:
                correct_answer = rendered['answers'][answer_id]['correct_value']
                answer_type = rendered['answers'][answer_id]['type']
                
                is_correct, message = self.checker.check(
                    student_answer,
                    correct_answer,
                    answer_type
                )
                
                results[answer_id] = {
                    'correct': is_correct,
                    'message': message,
                    'student_answer': student_answer,
                    'correct_answer': correct_answer
                }
        
        all_correct = all(r['correct'] for r in results.values()) if results else False
        
        return {
            'results': results,
            'all_correct': all_correct,
            'score': sum(1 for r in results.values() if r['correct']) / len(results) if results else 0
        }


# Singleton
_service = None


def get_pg_render_service() -> PGRenderService:
    """Get singleton PG render service instance."""
    global _service
    if _service is None:
        _service = PGRenderService()
    return _service

