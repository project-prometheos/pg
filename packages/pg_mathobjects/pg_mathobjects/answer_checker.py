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


class ListAnswerChecker(AnswerChecker):
    """
    Answer checker for List objects.
    
    Checks if student's list matches the correct list.
    Supports ordered and unordered matching.
    """

    def __init__(self, correct_value, **options):
        """
        Create a ListAnswerChecker.

        Args:
            correct_value: The correct List
            **options: Checker options (ordered, partialCredit)
        """
        super().__init__(correct_value, **options)
        self.ordered = options.get('ordered', True)
        self.partial_credit = options.get('partialCredit', False)

    def check(self, student_answer: str) -> Dict[str, Any]:
        """
        Check if student answer matches correct list.

        Args:
            student_answer: Student's answer (comma-separated string)

        Returns:
            dict with 'score' and 'correct' keys
        """
        from .list import List
        from .formula import Formula
        from .real import Real

        try:
            # Handle special case: NONE
            if student_answer.strip().upper() == "NONE":
                student_list = List("NONE", context=self.correct_value.context)
            else:
                # Parse comma-separated values
                parts = [p.strip() for p in student_answer.split(',')]
                
                # Try to parse each part as appropriate MathObject
                items = []
                for part in parts:
                    # Try as number first
                    try:
                        items.append(float(part))
                    except ValueError:
                        # Try as Formula
                        try:
                            items.append(Formula(part, self.correct_value.context))
                        except:
                            # Keep as string
                            items.append(part)
                
                student_list = List(*items, context=self.correct_value.context)

        except Exception as e:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Error parsing answer: {e}'
            }

        # Compare lists
        if self.correct_value == student_list:
            return {'score': 1.0, 'correct': True}
        
        # Check for partial credit if enabled
        if self.partial_credit:
            # Count how many items match
            correct_count = 0
            total = len(self.correct_value.items)
            
            if self.ordered:
                # Count matching items in correct positions
                for i in range(min(len(self.correct_value.items), len(student_list.items))):
                    if self._items_equal(self.correct_value.items[i], student_list.items[i]):
                        correct_count += 1
            else:
                # Count matching items in any position
                student_items = list(student_list.items)
                for correct_item in self.correct_value.items:
                    for i, student_item in enumerate(student_items):
                        if self._items_equal(correct_item, student_item):
                            student_items.pop(i)
                            correct_count += 1
                            break
            
            if total > 0:
                score = correct_count / total
                if score > 0:
                    return {
                        'score': score,
                        'correct': score == 1.0,
                        'message': f'{correct_count} out of {total} correct'
                    }
        
        return {'score': 0.0, 'correct': False}

    def _items_equal(self, item1: Any, item2: Any) -> bool:
        """Check if two items are equal."""
        # Handle MathObjects with equality
        if hasattr(item1, '__eq__'):
            try:
                return item1 == item2
            except:
                pass
        return item1 == item2


class IntervalAnswerChecker(AnswerChecker):
    """
    Answer checker for Interval objects.
    
    Checks if student's interval matches the correct interval.
    """

    def check(self, student_answer: str) -> Dict[str, Any]:
        """
        Check if student answer matches correct interval.

        Args:
            student_answer: Student's answer (interval notation string)

        Returns:
            dict with 'score' and 'correct' keys
        """
        from .interval import Interval

        try:
            # Parse student answer as Interval
            student_interval = Interval(student_answer, self.correct_value.context)

            # Compare intervals
            if self.correct_value == student_interval:
                return {'score': 1.0, 'correct': True}
            else:
                return {'score': 0.0, 'correct': False}

        except Exception as e:
            return {
                'score': 0.0,
                'correct': False,
                'message': f'Error parsing interval: {e}'
            }

