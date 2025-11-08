"""
Answer checkers for MathObjects.

Provides answer checking functionality for Formula objects in pg_math.
Ported from pg_mathobjects for Perl parity migration.
"""

from typing import Any, Dict
import random
import sympy as sp


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

        # Parse student answer to Formula
        try:
            # Use the correct formula's context to ensure same flags/variables
            student_formula = Formula(
                student_answer, self.correct_value.variables, self.correct_value.context)
        except Exception as e:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Error parsing answer: {e}'
            }

        # Get variables from correct answer
        correct_vars = sorted(
            [str(s) for s in self.correct_value._sympy_expr.free_symbols])
        student_vars = sorted(
            [str(s) for s in student_formula._sympy_expr.free_symbols])

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

                # Compare values - convert to float
                correct_float = float(correct_value)
                student_float = float(student_value)

                diff = abs(correct_float - student_float)
                if diff > self.tolerance:
                    return {
                        'score': 0.0,
                        'correct': False,
                        'message': f'Formulas differ at {test_point}'
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


class RealAnswerChecker(AnswerChecker):
    """
    Answer checker for Real numbers.

    Compares real numbers with tolerance.
    """

    def __init__(self, correct_value, **options):
        """
        Create a RealAnswerChecker.

        Args:
            correct_value: The correct Real number
            **options: Checker options (tolerance, tolType)
        """
        super().__init__(correct_value, **options)
        # Get tolerance from options or context
        tolerance_from_context = correct_value.context.flags.get('tolerance')
        self.tolerance = options.get(
            'tolerance', tolerance_from_context if tolerance_from_context is not None else 0.001)

        tol_type_from_context = correct_value.context.flags.get('tolType')
        self.tol_type = options.get(
            'tolType', tol_type_from_context if tol_type_from_context is not None else 'relative')

    def __call__(self, student_answer: str) -> Dict[str, Any]:
        """Allow checker to be called as a function."""
        return self.check(student_answer)

    def check(self, student_answer: str) -> Dict[str, Any]:
        """
        Check if student answer matches correct answer.

        Args:
            student_answer: Student's answer (string)

        Returns:
            dict with 'score', 'correct' keys, and optional 'message'
        """
        from .numeric import Real

        # Try to parse student answer as number
        try:
            if isinstance(student_answer, (int, float)):
                student_value = float(student_answer)
            else:
                student_answer = str(student_answer).strip()
                student_value = float(student_answer)
        except (ValueError, TypeError) as e:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Invalid number format: {student_answer}'
            }

        # Create a Real from student answer with same context
        student_real = Real(student_value, self.correct_value.context)

        # Compare using Real's equality with tolerance
        if self.correct_value == student_real:
            return {
                'score': 1.0,
                'correct': True
            }
        else:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Expected {self.correct_value.value}, got {student_value}'
            }
