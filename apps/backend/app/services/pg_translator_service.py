"""PG Translator service for backend - Full PG compatibility with all enhancements."""

from typing import Dict, Any, List
from pathlib import Path
import tempfile

from pg_translator import PGTranslator
from pg_answer import AnswerResult
from pg_parser import Context


class PGTranslatorService:
    """Service for rendering and checking PG problems using pg_translator."""

    def __init__(self):
        self.translator = PGTranslator()

    def render_problem(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """
        Render a PG problem using pg_translator.

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
            # Use translate_source to avoid file I/O
            result = self.translator.translate_source(
                pg_source=pg_source,
                seed=seed,
                inputs=None,  # No answer checking yet
                context=None  # Use default context
            )

            # Extract answer information from answer_blanks
            answers = {}
            for name, blank_info in result.answer_blanks.items():
                # Handle both dict format {"evaluator": ev} and direct evaluator format
                evaluator = None

                if isinstance(blank_info, dict):
                    # New format: {"evaluator": evaluator} OR {"ans_eval": evaluator}
                    evaluator = blank_info.get(
                        "evaluator") or blank_info.get("ans_eval")

                    # Check if evaluator is itself a dict (nested case)
                    if isinstance(evaluator, dict):
                        # Try to extract from nested dict: {'ans_eval': Formula(...)}
                        evaluator = evaluator.get(
                            "ans_eval") or evaluator.get("evaluator")
                else:
                    # Old format: direct evaluator
                    evaluator = blank_info

                if evaluator:
                    # Get correct answer from evaluator
                    # Try multiple attributes in order of preference
                    correct_value = ""

                    # 1. Try TeX() method for best representation
                    if hasattr(evaluator, "TeX"):
                        try:
                            tex_val = evaluator.TeX()
                            if tex_val:
                                correct_value = str(tex_val)
                        except Exception as e:
                            pass

                    # 2. Try string() method
                    if not correct_value and hasattr(evaluator, "string"):
                        try:
                            str_val = evaluator.string()
                            if str_val:
                                correct_value = str(str_val)
                        except Exception as e:
                            pass

                    # 3. Try correct_answer attribute
                    if not correct_value and hasattr(evaluator, "correct_answer"):
                        try:
                            correct_value = str(evaluator.correct_answer)
                        except Exception as e:
                            pass

                    # 4. Try value attribute
                    if not correct_value and hasattr(evaluator, "value"):
                        try:
                            correct_value = str(evaluator.value)
                        except Exception as e:
                            pass

                    # 5. Fallback to str() of evaluator
                    if not correct_value:
                        try:
                            correct_value = str(evaluator)
                        except Exception as e:
                            correct_value = ""

                    # Detect answer type
                    answer_type = self._detect_answer_type(evaluator)

                    answers[name] = {
                        'correct_value': correct_value,
                        'type': answer_type
                    }

            return {
                'statement_html': result.statement_html or "",
                'inputs': list(result.answer_blanks.keys()),
                'answers': answers,
                'solution_html': result.solution_html or "",
                'warnings': result.warnings or [],
                'errors': result.errors or []
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

    def check_answers(self, pg_source: str, seed: int,
                      student_inputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Check student answers for a problem.

        Args:
            pg_source: PG file source code
            seed: Random seed
            student_inputs: Dict mapping answer_id to student's answer string

        Returns:
            {
                'results': Dict[str, Dict],  # Per-answer results
                'all_correct': bool,
                'score': float
            }
        """
        try:
            # Translate with inputs to trigger answer checking
            result = self.translator.translate_source(
                pg_source=pg_source,
                seed=seed,
                inputs=student_inputs,
                context=None
            )

            # Format results
            results = {}
            for name, answer_result in (result.answer_results or {}).items():
                results[name] = {
                    'correct': answer_result.score >= 1.0,
                    'score': answer_result.score,
                    'message': answer_result.answer_message or ("Correct!" if answer_result.score >= 1.0 else "Incorrect"),
                    'student_answer': student_inputs.get(name, ""),
                    'correct_answer': answer_result.correct_answer or "",
                    'answer_type': self._get_answer_type_from_result(answer_result)
                }

            # Calculate overall score
            all_correct = all(r['correct']
                              for r in results.values()) if results else False
            score = result.score if result.score is not None else 0.0

            return {
                'results': results,
                'all_correct': all_correct,
                'score': score
            }

        except Exception as e:
            import traceback
            return {
                'results': {},
                'all_correct': False,
                'score': 0.0,
                'errors': [str(e), traceback.format_exc()]
            }

    def _detect_answer_type(self, evaluator: Any) -> str:
        """
        Detect the type of answer based on evaluator.

        Returns:
            'number', 'formula', 'interval', 'point', 'vector', or 'string'
        """
        # Check evaluator class name
        class_name = evaluator.__class__.__name__.lower()

        if 'real' in class_name or 'numeric' in class_name:
            return 'number'
        elif 'formula' in class_name:
            return 'formula'
        elif 'interval' in class_name:
            return 'interval'
        elif 'point' in class_name:
            return 'point'
        elif 'vector' in class_name:
            return 'vector'
        elif 'string' in class_name:
            return 'string'

        # Fallback: try to get value and infer type
        try:
            correct_value = str(getattr(evaluator, "correct_answer", ""))

            # Check for intervals: [a, b], (a, b), [a, b), (-inf, 5]
            if (correct_value.startswith('[') or correct_value.startswith('(')) and \
               (correct_value.endswith(']') or correct_value.endswith(')')):
                return 'interval'

            # Check for points/vectors: (x, y, z) or <x, y, z>
            if correct_value.startswith('(') and correct_value.endswith(')') and ',' in correct_value:
                return 'point'
            if correct_value.startswith('<') and correct_value.endswith('>'):
                return 'vector'

            # Check if it's a simple number
            try:
                float(correct_value)
                return 'number'
            except (ValueError, TypeError):
                pass

            # Check if it contains mathematical operators (formula)
            if any(char in correct_value for char in ['+', '-', '*', '/', '^', '(', ')']) or \
               any(var in correct_value.lower() for var in ['x', 'y', 'z', 't', 'sin', 'cos', 'sqrt', 'pi']):
                return 'formula'
        except:
            pass

        # Default to string
        return 'string'

    def _get_answer_type_from_result(self, answer_result: AnswerResult) -> str:
        """Get answer type from AnswerResult."""
        # AnswerResult might have type information
        if hasattr(answer_result, 'answer_type'):
            return answer_result.answer_type

        # Try to infer from correct_answer
        correct = str(answer_result.correct_answer or "")

        if (correct.startswith('[') or correct.startswith('(')) and \
           (correct.endswith(']') or correct.endswith(')')):
            return 'interval'

        try:
            float(correct)
            return 'number'
        except:
            pass

        return 'formula'


# Singleton
_service = None


def get_pg_translator_service() -> PGTranslatorService:
    """Get singleton PG translator service instance."""
    global _service
    if _service is None:
        _service = PGTranslatorService()
    return _service
