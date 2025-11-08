"""
DifferenceQuotient - Answer checker for difference quotients.

This implements an answer checker for difference quotients as a subclass
of the Formula class. The difference quotient is a special formula with
a special variable for the differential (dx, h, dt, etc.).

The checker validates that the student's result doesn't contain the
differential variable in the denominator (meaning it's fully reduced).

Usage:
    DifferenceQuotient("2*x + h", "h")         # (f(x+h) - f(x))/h for f(x)=x^2
    DifferenceQuotient("2*x + dx")             # Uses 'dx' by default
    DifferenceQuotient("x + 3", "x", 3)        # (f(x) - f(c))/(x-c) at c=3

Reference: macros/parsers/parserDifferenceQuotient.pl
"""

from typing import Any, Optional


class DifferenceQuotient:
    """
    Parser for difference quotient expressions.

    Validates that a difference quotient has been properly simplified
    (no division by the differential variable).
    """

    def __init__(
        self,
        formula: str,
        dx: Optional[str] = None,
        zero_point: float = 0,
        context: Optional[Any] = None
    ):
        """
        Create a DifferenceQuotient object.

        Args:
            formula: The simplified difference quotient formula (e.g., "2*x + h")
            dx: Variable representing the differential (e.g., "h", "dx", "dt")
                If None, uses "d" + last variable name alphabetically
            zero_point: Value to substitute for dx to test for division by zero
                        (default 0). Non-zero for things like (f(x)-f(3))/(x-3)
            context: Context to use (if None, uses current context)

        Examples:
            # Simplify (x+h)^2 - x^2) / h
            DifferenceQuotient("2*x + h", "h")

            # Simplify (t+dt)^3 - t^3) / dt
            DifferenceQuotient("3*t^2 + 3*t*dt + dt^2", "dt")

            # Simplify (x^2 - 9) / (x - 3) at x=3
            DifferenceQuotient("x + 3", "x", 3)
        """
        from pg_math.context import get_current_context
        from pg_mathobjects import Compute

        # Get or use provided context
        self.context = context or get_current_context()

        # Determine differential variable
        if dx is None:
            # Use 'd' + last variable name alphabetically
            var_names = sorted(self.context.variables.list())
            if var_names:
                dx = 'd' + var_names[-1]
            else:
                dx = 'dx'

        self.dx = dx
        self.zero_point = zero_point

        # Create a copy of context with dx variable added
        # Note: In Python we can modify the existing context temporarily
        original_vars = set(self.context.variables.list())
        if dx not in original_vars:
            self.context.variables.add(dx, 'Real')
            self._added_dx = True
        else:
            self._added_dx = False

        # Parse the formula in the modified context
        self.formula = Compute(formula, context=self.context)

    def cmp(self, **options):
        """
        Return answer evaluator with difference quotient checking.

        The evaluator checks that:
        1. Student answer is equivalent to the correct formula
        2. When dx is substituted with zero_point, no division by zero occurs
           (ensuring the quotient is fully simplified)

        Args:
            **options: Options passed to Formula.cmp()

        Returns:
            Answer evaluator
        """
        # Get base formula checker
        base_checker = self.formula.cmp(**options)

        # Create custom checker that adds difference quotient validation
        class DifferenceQuotientChecker:
            def __init__(self, base, dq_obj):
                self.base = base
                self.dq = dq_obj

            def evaluate(self, student_answer: str) -> Any:
                """Evaluate student answer with difference quotient checks."""
                from pg_mathobjects import Compute
                from dataclasses import dataclass

                @dataclass
                class AnswerResult:
                    correct: bool
                    score: float
                    messages: list

                # First check if answer is mathematically correct
                base_result = self.base.evaluate(student_answer)

                # If incorrect or preview mode, return base result
                if not base_result.correct:
                    return base_result

                # Additional check: substitute zero_point for dx
                # If this causes division by zero, answer isn't simplified
                try:
                    student_formula = Compute(student_answer, context=self.dq.context)
                    # Try to evaluate at the zero point
                    test_val = student_formula.eval(**{self.dq.dx: self.dq.zero_point})
                except ZeroDivisionError:
                    return AnswerResult(
                        correct=False,
                        score=0.0,
                        messages=["It looks like you didn't finish simplifying your answer"]
                    )
                except Exception:
                    # Other errors (like undefined) also suggest incomplete simplification
                    return AnswerResult(
                        correct=False,
                        score=0.0,
                        messages=["It looks like you didn't finish simplifying your answer"]
                    )

                # All checks passed
                return base_result

        return DifferenceQuotientChecker(base_checker, self)

    def __str__(self):
        return f"DifferenceQuotient({self.formula}, dx={self.dx})"

    def __repr__(self):
        return f"DifferenceQuotient('{self.formula}', '{self.dx}', {self.zero_point})"
