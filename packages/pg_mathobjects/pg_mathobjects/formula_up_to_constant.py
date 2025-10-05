"""FormulaUpToConstant - Formulas unique up to an arbitrary constant.

This module implements formulas that represent antiderivatives, where
the answer is only unique up to an arbitrary constant (e.g., "+ C").

Students must include a constant in their answer, but can use any
single-letter constant they want.

Example:
    >>> from pg_mathobjects import FormulaUpToConstant
    >>> f = FormulaUpToConstant("x^2/2 + C")
    >>> # Student can answer with any constant
    >>> checker = f.cmp()
    >>> result = checker.check("x^2/2 + K")  # Acceptable
    >>> result = checker.check("x^2/2 + 5")  # Acceptable
    >>> result = checker.check("x^2/2")      # Not acceptable - missing constant
"""

from __future__ import annotations

import re
from typing import Any

import sympy as sp

from .context import Context
from .formula import Formula
from .real import Real


class FormulaUpToConstant(Formula):
    """A formula that is only unique up to an arbitrary constant.

    This is used for antiderivatives where the student must include
    a "+ C" (or any other single-letter constant) in their answer.

    Attributes:
        constant (str | None): The name of the arbitrary constant (e.g., "C", "K")
        _adapt_formula (Formula | None): Formula with adaptive parameters for comparison
    """

    def __init__(
        self,
        expr: str | sp.Expr | Formula,
        context: Context | None = None,
    ):
        """Initialize a FormulaUpToConstant.

        Args:
            expr: Mathematical expression (string, sympy, or Formula)
            context: Context to use (creates private copy)

        Notes:
            - If no constant is found in the expression, "+ C" is added automatically
            - The constant must be a single letter (except 'e', 'i', or 'pi')
            - Creates a private context copy to avoid affecting the rest of the problem
        """
        # Create private context copy
        if context is None:
            from . import get_current_context
            context = get_current_context()

        private_context = context.copy()

        # Store a set of arbitrary constants for this formula
        self._arbitrary_constants = set()

        # Convert to Formula first if needed
        if isinstance(expr, FormulaUpToConstant):
            # Copy from existing FormulaUpToConstant
            super().__init__(expr._tree, private_context)
            self.constant = expr.constant
            self._adapt_formula = expr._adapt_formula
            self._private_context = private_context
            self._arbitrary_constants = expr._arbitrary_constants.copy()
            return
        elif isinstance(expr, Formula):
            # Convert from Formula
            super().__init__(expr._tree, private_context)
        else:
            # Parse new expression
            super().__init__(expr, private_context)

        # Store private context after super().__init__
        self._private_context = private_context

        # Find the arbitrary constant in the expression
        self.constant = self._find_constant()

        # If no constant found, add C automatically
        if self.constant is None:
            # Add C to context if not already there
            if self._private_context.variables.get('C') is None:
                self._private_context.variables.add('C')

            # Create new formula with + C
            c_sym = sp.Symbol('C')
            new_expr = self._tree + c_sym
            # Update the tree directly
            self._tree = new_expr
            self.constant = 'C'
            self._arbitrary_constants.add('C')

        # Verify the formula is linear in the constant
        self._verify_linearity()

        # Create adapted formula for comparison (with parameters)
        self._adapt_formula = None  # Created on demand in compare

    def _find_constant(self) -> str | None:
        """Find the arbitrary constant in the expression.

        Returns:
            Name of the constant variable, or None if not found

        Notes:
            A constant is a single-letter variable that:
            - Is not 'e', 'i', or a known math constant
            - Is not already a defined variable in the base context
        """
        # Get all free symbols from the expression
        symbols = self._tree.free_symbols

        # Reserved names that can't be constants
        reserved = {'e', 'i', 'pi', 'E', 'I'}

        # Get base context variables (before we added anything)
        # Note: This is tricky - we need the ORIGINAL context, not our private one
        # For now, check if it's a single letter and not in reserved set

        potential_constants = []
        for sym in symbols:
            name = str(sym)
            if len(name) == 1 and name not in reserved:
                # Check if it's in our arbitrary constants set or not defined yet
                if name in self._arbitrary_constants:
                    potential_constants.append(name)
                elif self._private_context.variables.get(name) is None:
                    # Not defined yet - could be a constant
                    potential_constants.append(name)

        if len(potential_constants) > 1:
            raise ValueError(
                f"Formula has multiple potential arbitrary constants: "
                f"{', '.join(potential_constants)}. Use only one constant."
            )

        if len(potential_constants) == 1:
            # Mark it as arbitrary constant
            const_name = potential_constants[0]
            if self._private_context.variables.get(const_name) is None:
                self._private_context.variables.add(const_name)
            self._arbitrary_constants.add(const_name)
            return const_name

        return None

    def _verify_linearity(self) -> None:
        """Verify that the formula is linear in the arbitrary constant.

        Raises:
            ValueError: If the formula is not linear in the constant
        """
        if self.constant is None:
            return

        # Differentiate with respect to the constant using sympy directly
        # (Don't use D() which calls remove_constant first)
        const_sym = sp.Symbol(self.constant)
        derivative_expr = sp.diff(self._tree, const_sym)

        # Check if derivative has any free symbols
        # For linearity, the derivative with respect to C should be constant (no variables)
        if len(derivative_expr.free_symbols) > 0:
            raise ValueError(
                f"Formula is not linear in the arbitrary constant '{self.constant}'. "
                f"The derivative with respect to {self.constant} must be constant, "
                f"but got: {derivative_expr}"
            )

    def compare(
        self,
        other: Any,
        tolerance: float | None = None,
    ) -> tuple[bool, str | None]:
        """Compare this formula with another, accounting for arbitrary constants.

        Args:
            other: The value to compare with
            tolerance: Comparison tolerance (uses context default if None)

        Returns:
            Tuple of (equal, error_message)
            - equal: True if equivalent up to constant
            - error_message: Helpful message if not equal, None if equal

        Notes:
            Two FormulaUpToConstant objects are equal if they differ only
            by a constant term. The comparison:
            1. Checks if other has a constant
            2. Substitutes constants to match
            3. Verifies equivalence using adaptive parameters
        """
        from . import Compute

        # Convert other to a value
        if not isinstance(other, (Formula, FormulaUpToConstant, Real, int, float)):
            try:
                other = Compute(other, self._private_context)
            except Exception:
                return False, "Cannot compare with non-formula value"

        # Check if other is a FormulaUpToConstant or Formula
        if isinstance(other, Real) or isinstance(other, (int, float)):
            return False, "Your answer should include an arbitrary constant (like +C)"

        if isinstance(other, Formula) and not isinstance(other, FormulaUpToConstant):
            return False, "Your answer should include an arbitrary constant (like +C)"

        if not isinstance(other, FormulaUpToConstant):
            return False, "Your answer should include an arbitrary constant (like +C)"

        # Check if other has a constant
        if other.constant is None:
            return False, "Your answer should include an arbitrary constant (like +C)"

        # If constants are different, substitute to match
        other_expr = other._tree
        if other.constant != self.constant:
            # Substitute other's constant with ours
            other_sym = sp.Symbol(other.constant)
            self_sym = sp.Symbol(self.constant)
            other_expr = other_expr.subs(other_sym, self_sym)

        # Now compare: self.expr and other_expr should differ by at most a constant
        # This means: self.expr - other_expr should be a constant
        diff = sp.simplify(self._tree - other_expr)

        # Check if diff is constant (no free symbols except the arbitrary constant)
        diff_symbols = diff.free_symbols
        const_sym = sp.Symbol(self.constant)

        # Remove the arbitrary constant from free symbols
        diff_symbols_without_const = diff_symbols - {const_sym}

        if len(diff_symbols_without_const) > 0:
            return False, "Your answer is not equivalent to the correct answer"

        # Check that the coefficient of the constant is non-zero
        # (i.e., the student included the constant term)
        const_coeff = diff.coeff(const_sym)

        if tolerance is None:
            tolerance = getattr(self._private_context, 'tolerance', 0.001)

        if const_coeff is not None and abs(float(const_coeff)) > tolerance:
            return True, None  # Different constants - that's okay

        # If coefficient is zero or very small, formulas are identical
        # (meaning student's formula differs from ours by only a numeric constant)
        # That's acceptable
        return True, None

    def cmp(self, **options):
        """Create an answer checker for this FormulaUpToConstant.

        Args:
            **options: Options for the answer checker
                showHints (bool): Show helpful hints to students (default: True)
                showLinearityHints (bool): Show linearity hints (default: True)

        Returns:
            Callable that checks student answers
        """
        show_hints = options.get('showHints', True)
        show_linearity_hints = options.get('showLinearityHints', True)

        def checker(student_answer: str) -> dict[str, Any]:
            """Check student answer against this FormulaUpToConstant.

            Args:
                student_answer: Student's answer string

            Returns:
                Dictionary with:
                    - correct: True if answer is correct
                    - message: Feedback message for student
                    - student_value: Parsed student answer
            """
            from . import Compute

            result = {
                'correct': False,
                'message': '',
                'student_value': None,
            }

            try:
                # Parse student answer
                student = Compute(student_answer, self._private_context)
                result['student_value'] = student

                # Try to convert to FormulaUpToConstant if it's a Formula
                if isinstance(student, Formula) and not isinstance(student, FormulaUpToConstant):
                    # Check if it has a potential constant
                    # Get the variables from the correct answer (excluding the constant)
                    correct_vars = set(
                        self._private_context.variables.list()) - {self.constant}

                    # Check student's symbols
                    symbols = student._tree.free_symbols
                    potential_constants = [
                        str(s) for s in symbols
                        if (len(str(s)) == 1 and
                            str(s) not in {'e', 'i', 'E', 'I'} and
                            # Exclude problem variables
                            str(s) not in correct_vars)
                    ]

                    if len(potential_constants) == 0:
                        result['message'] = (
                            "Your answer should include an arbitrary constant (like +C). "
                            "Note: there is always more than one possibility."
                        ) if show_hints else ""
                        return result
                    elif len(potential_constants) == 1:
                        # Convert to FormulaUpToConstant
                        try:
                            student = FormulaUpToConstant(
                                student, self._private_context)
                        except ValueError as e:
                            if show_linearity_hints:
                                result['message'] = str(e)
                            return result

                # Compare
                equal, error_msg = self.compare(student)

                if equal:
                    result['correct'] = True
                    result['message'] = ""
                elif show_hints and error_msg:
                    result['message'] = error_msg

            except Exception as e:
                result['message'] = f"Error parsing answer: {str(e)}" if show_hints else ""

            return result

        return checker

    def remove_constant(self) -> Formula:
        """Remove the arbitrary constant and return a regular Formula.

        Returns:
            Formula with the constant set to zero

        Example:
            >>> f = FormulaUpToConstant("x^2/2 + C")
            >>> g = f.remove_constant()  # Returns Formula("x^2/2")
        """
        if self.constant is None:
            return Formula(self.sympy_expr, self._private_context)

        # Substitute constant with 0
        const_sym = sp.Symbol(self.constant)
        expr_without_const = self._tree.subs(const_sym, 0)

        # Simplify and return as Formula
        expr_simplified = sp.simplify(expr_without_const)
        return Formula(expr_simplified, self._private_context)

    def D(self, var: str) -> Formula:
        """Differentiate with respect to a variable.

        Args:
            var: Variable name to differentiate with respect to

        Returns:
            Formula (not FormulaUpToConstant) representing the derivative

        Notes:
            Returns a regular Formula because derivatives don't need the constant
        """
        return self.remove_constant().D(var)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"FormulaUpToConstant('{self}', constant='{self.constant}')"
