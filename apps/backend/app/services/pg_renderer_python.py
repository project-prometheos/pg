"""Python PG renderer service for backend."""

from typing import Dict, Any, List, Set

# Import from installed package (editable mode)
# Package is installed with: pip install -e packages/pg_renderer
from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker

# Reload: Added inequality and interval string comparison


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
        rendered = self.renderer.render(pg_source, seed=seed)
        answers_meta = rendered.get('answers', {})

        results: Dict[str, Any] = {}

        # Pre-compute MultiAnswer group metadata so we can evaluate groups once.
        multi_groups: Dict[str, List[Dict[str, Any]]] = {}
        for ans_id, meta in answers_meta.items():
            group = meta.get('group')
            if group:
                multi_groups.setdefault(group, []).append({
                    'answer_id': ans_id,
                    'index': meta.get('group_index', 0),
                    'meta': meta,
                })

        processed_groups: Set[str] = set()

        for answer_id, meta in answers_meta.items():
            student_answer = student_inputs.get(answer_id, '') or ''
            correct_answer = meta.get('correct_value')
            answer_type = meta.get('type')

            if answer_type == 'multi':
                group = meta.get('group')
                if not group or group in processed_groups:
                    continue
                group_items = [
                    {
                        'answer_id': item['answer_id'],
                        'meta': item['meta'],
                        'student_answer': student_inputs.get(item['answer_id'], '') or '',
                    }
                    for item in sorted(multi_groups.get(group, []), key=lambda data: data['index'])
                ]

                group_result = self.checker.check_multi_group(group, group_items)

                print(f"[DEBUG] Checking MultiAnswer group {group}:")
                for item in group_result['items']:
                    idx = item['context'].get('group_index')
                    print(f"  Blank {item['answer_id']} (index {idx}):")
                    print(f"    Student: '{item['student_answer']}'")
                    print(f"    Correct: '{item['correct_answer']}'")
                    print(f"    Raw correct: {item.get('raw_correct')}")
                    print(f"    Final correct: {item['correct']}")
                    print(f"    Message: {item['message']}")

                for item in group_result['items']:
                    results[item['answer_id']] = {
                        'correct': item['correct'],
                        'message': item['message'],
                        'student_answer': item['student_answer'],
                        'correct_answer': item['correct_answer'],
                        'answer_type': 'multi',
                        'context': item['context'],
                    }

                processed_groups.add(group)
                continue

            context = self.checker.build_context(meta)

            print(f"[DEBUG] Checking answer {answer_id}:")
            print(f"  Student: '{student_answer}'")
            print(f"  Correct: '{correct_answer}'")
            print(f"  Type: {answer_type}")
            print(f"  Context: {context}")

            is_correct, message = self.checker.check(
                student_answer,
                correct_answer,
                answer_type,
                context
            )

            print(f"  Result: {is_correct} - {message}")

            results[answer_id] = {
                'correct': is_correct,
                'message': message,
                'student_answer': student_answer,
                'correct_answer': correct_answer,
                'answer_type': answer_type,
                'context': context
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

