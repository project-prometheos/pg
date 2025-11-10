"""ImplicitPlane Parser for WeBWorK.

This module provides the ImplicitPlane class for validating plane equations
in 3D space (e.g., "2x + 3y - z = 5").

Based on macros/parsers/parserImplicitPlane.pl from the WeBWorK distribution.
"""

from typing import Any, Dict, Optional, Tuple
import re


def ImplicitPlane(*args, **kwargs):
    """
    Stub implementation of ImplicitPlane - implicit plane parser.

    Args:
        *args: Plane equation specification
        **kwargs: Additional options

    Returns:
        Object representing an implicit plane
    """
    return type('ImplicitPlane', (), {
        '__str__': lambda self: 'ImplicitPlane',
    })()


class ImplicitPlaneClass:
    """
    Parser for implicit plane equations in 3D.

    Represents equations like "2x + 3y - z = 5" and validates student answers
    by comparing the planes they define (up to scalar multiples).

    Attributes:
        equation: The original equation string
        left_side: Left side of equation
        right_side: Right side of equation
    """

    def __init__(self, equation: str = "", **options):
        """
        Create an ImplicitPlane object.

        Args:
            equation: Plane equation like "2x + 3y - z = 5"
            **options: Additional options

        Example:
            >>> plane = ImplicitPlane("2x + 3y - z = 5")
            >>> plane = ImplicitPlane("x + y + z = 1")
        """
        self.equation = equation
        self.options = options
        self.left_side = None
        self.right_side = None
        self.normal_vector = None
        self.constant = None

        self._parse_equation(equation)

    def _parse_equation(self, equation: str) -> None:
        """
        Parse plane equation into components.

        Args:
            equation: Equation string with '=' sign
        """
        if '=' not in equation:
            raise ValueError(f"ImplicitPlane must contain '=': {equation}")

        parts = equation.split('=')
        if len(parts) != 2:
            raise ValueError(f"ImplicitPlane must have exactly one '=': {equation}")

        self.left_side = parts[0].strip()
        self.right_side = parts[1].strip()

        # Try to extract normal vector and constant
        # Pattern: ax + by + cz = d
        self._extract_coefficients()

    def _extract_coefficients(self) -> None:
        """
        Extract coefficients for x, y, z from the equation.

        Attempts to parse equations like "2x + 3y - z = 5"
        into normal vector (2, 3, -1) and constant 5.
        """
        # Simple pattern matching for common cases
        # This is a simplified version; full parser would be more robust
        coeff_pattern = r'([+-]?\s*\d*)\s*([xyz])'

        left_coeffs = {'x': 0, 'y': 0, 'z': 0}

        # Parse left side
        for match in re.finditer(coeff_pattern, self.left_side):
            coeff_str = match.group(1).replace(' ', '')
            var = match.group(2)

            if coeff_str == '' or coeff_str == '+':
                coeff = 1.0
            elif coeff_str == '-':
                coeff = -1.0
            else:
                try:
                    coeff = float(coeff_str)
                except ValueError:
                    coeff = 1.0

            left_coeffs[var] = coeff

        # Try to parse right side as constant
        try:
            self.constant = float(self.right_side)
        except ValueError:
            self.constant = None

        if left_coeffs.get('x') or left_coeffs.get('y') or left_coeffs.get('z'):
            self.normal_vector = (
                left_coeffs.get('x', 0),
                left_coeffs.get('y', 0),
                left_coeffs.get('z', 0)
            )

    def cmp(self, **options) -> 'ImplicitPlaneChecker':
        """
        Get an answer checker for this ImplicitPlane.

        Returns:
            ImplicitPlaneChecker configured for comparison

        Example:
            >>> plane = ImplicitPlane("x + y + z = 1")
            >>> ANS(plane.cmp())
        """
        return ImplicitPlaneChecker(self, **options)

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.left_side} = {self.right_side}"

    def __repr__(self) -> str:
        """Return representation."""
        return f"ImplicitPlane({str(self)})"


class ImplicitPlaneChecker:
    """
    Answer checker for ImplicitPlane comparison.

    Two plane equations are equivalent if they represent the same plane.
    This is true if one equation is a scalar multiple of the other.
    """

    def __init__(self, reference: ImplicitPlane, **options):
        """
        Initialize checker with reference plane.

        Args:
            reference: The correct ImplicitPlane
            **options: Checker options
        """
        self.reference = reference
        self.options = options
        self.tolerance = options.get('tolerance', 1e-6)

    def evaluate(self, student_answer: str) -> bool:
        """
        Check if student plane matches reference.

        Args:
            student_answer: Student's plane equation

        Returns:
            True if equations represent the same plane
        """
        try:
            student = ImplicitPlane(student_answer)
        except ValueError:
            return False

        # Check if normal vectors are parallel (scalar multiples)
        if not self.reference.normal_vector or not student.normal_vector:
            return str(student) == str(self.reference)

        ref_normal = self.reference.normal_vector
        student_normal = student.normal_vector

        # Find scaling factor (if any)
        scale = None
        tolerance = self.tolerance

        for ref_comp, student_comp in zip(ref_normal, student_normal):
            if abs(ref_comp) > tolerance:
                if scale is None:
                    if abs(student_comp) > tolerance:
                        scale = student_comp / ref_comp
                    else:
                        return False
                else:
                    if abs(student_comp) > tolerance:
                        if abs(student_comp / ref_comp - scale) > tolerance:
                            return False
                    elif abs(student_comp) > tolerance:
                        return False
            elif abs(student_comp) > tolerance:
                return False

        # Check that constants scale the same way
        if scale and self.reference.constant is not None:
            expected_const = self.reference.constant * scale
            if student.constant is not None:
                if abs(student.constant - expected_const) > tolerance:
                    return False

        return True

    def __call__(self, student_answer: str) -> Dict[str, Any]:
        """
        Callable interface for compatibility with PG answer checkers.

        Args:
            student_answer: Student's plane equation

        Returns:
            Result dictionary with 'score' and 'message' keys
        """
        is_correct = self.evaluate(student_answer)
        return {
            'score': 1 if is_correct else 0,
            'message': '' if is_correct else 'Your plane equation is not equivalent to the correct one'
        }


__all__ = [
    'ImplicitPlane',
    'ImplicitPlaneChecker',
]
