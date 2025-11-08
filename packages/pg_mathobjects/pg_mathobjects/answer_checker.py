"""
Answer checkers for MathObjects.

Provides answer checking functionality for Real numbers and Formulas.
"""

from typing import Any, Dict


class AnswerChecker:
    """Base class for answer checkers."""

    def __init__(self, correct_value, **options):
        """
        Create an answer checker.

        Args:
            correct_value: The correct answer
            **options: Checker options
        """
        self.correct_value = correct_value
        self.options = options

    def check(self, student_answer: str) -> Dict[str, Any]:
        """
        Check a student answer.

        Args:
            student_answer: Student's answer as string

        Returns:
            Dictionary with 'score' (0-1) and optional 'message'
        """
        raise NotImplementedError("Subclass must implement check()")

    def withPostFilter(self, filter_function):
        """
        Add post-processing filter (stub implementation).

        In full implementation, this would apply a filter function after
        answer checking to provide custom hints, modify scores, etc.

        Args:
            filter_function: Filter to apply (e.g., AnswerHints result)

        Returns:
            self (for method chaining)
        """
        # Stub: just store the filter but don't use it
        self.post_filter = filter_function
        return self


class RealAnswerChecker(AnswerChecker):
    """Answer checker for Real numbers."""

    def check(self, student_answer: str) -> Dict[str, Any]:
        """Check if student answer matches correct Real number."""
        from .real import Real
        from .formula import Formula

        try:
            # Normalize common constant representations
            # Replace unicode π with 'pi', uppercase 'Pi' with 'pi'
            normalized = student_answer.replace('π', 'pi').replace('Pi', 'pi')

            # First try to parse as a simple float
            try:
                student_value = float(normalized)
                student_real = Real(student_value, self.correct_value.context)
            except ValueError:
                # If that fails, try parsing as a formula (which handles pi, e, etc.)
                # Then evaluate it to get a numeric value
                formula = Formula(normalized, self.correct_value.context)
                # Evaluate with no variables (constant expression)
                import sympy as sp
                student_value = float(formula._tree.evalf())
                student_real = Real(student_value, self.correct_value.context)

            # Compare with tolerance
            if student_real == self.correct_value:
                return {'score': 1.0, 'correct': True}
            else:
                return {'score': 0.0, 'correct': False}

        except (ValueError, TypeError) as e:
            return {
                'score': 0.0,
                'correct': False,
                'message': 'Invalid number format'
            }


class FormulaAnswerChecker(AnswerChecker):
    """
    Answer checker for Formula objects.

    Compares formulas by testing them at multiple points.
    """

    def __init__(self, correct_value, **options):
        """
        Create a FormulaAnswerChecker.

        Args:
            correct_value: The correct Formula
            **options: Checker options (num_points, tolerance)
        """
        super().__init__(correct_value, **options)
        self.num_points = options.get('num_points', 5)
        self.tolerance = options.get('tolerance', 0.01)

    def check(self, student_answer: str) -> Dict[str, Any]:
        """
        Check if student answer matches correct answer.

        Tests the formulas at multiple random points to see if they
        produce the same values within tolerance.

        Args:
            student_answer: Student's answer (string)

        Returns:
            dict with 'score' and 'correct' keys
        """
        from .formula import Formula
        from .real import Real
        import random

        # Parse student answer to Formula
        try:
            student_formula = Formula(
                student_answer, self.correct_value.context)
        except Exception as e:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Error parsing answer: {e}'
            }

        # Get variables from correct answer
        import sympy as sp
        correct_vars = sorted([str(s)
                              for s in self.correct_value._tree.free_symbols])
        student_vars = sorted([str(s)
                              for s in student_formula._tree.free_symbols])

        # Check that variables match
        if correct_vars != student_vars:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Formula uses different variables. Expected: {correct_vars}, got: {student_vars}'
            }

        # Test at multiple random points
        for _ in range(self.num_points):
            # Generate random test point
            test_point = {}
            for var in correct_vars:
                test_point[var] = random.uniform(-5, 5)

            try:
                # Evaluate both formulas
                correct_value = self.correct_value.eval(**test_point)
                student_value = student_formula.eval(**test_point)

                # Compare values
                if isinstance(correct_value, Real) and isinstance(student_value, Real):
                    diff = abs(correct_value.value - student_value.value)
                    if diff > self.tolerance:
                        return {
                            'score': 0.0,
                            'correct': False,
                            'message': f'Formulas differ at {test_point}'
                        }
                else:
                    # Still symbolic - something is wrong
                    return {
                        'score': 0.0,
                        'correct': False,
                        'message': 'Unable to evaluate formulas numerically'
                    }

            except Exception as e:
                return {
                    'score': 0.0,
                    'correct': False,
                    'message': f'Error evaluating formula: {e}'
                }

        # All test points passed
        return {
            'score': 1.0,
            'correct': True
        }
