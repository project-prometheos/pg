"""ParametricLine Parser for WeBWorK.

This module provides the ParametricLine class for validating parametric line equations
(e.g., "<1, 2> + t<3, 4>" or vector form equations).

Based on macros/parsers/parserParametricLine.pl from the WeBWorK distribution.
"""

from typing import Any, Dict, List, Optional, Tuple
import re


def ParametricLine(*args, **kwargs):
    """
    Stub implementation of ParametricLine - parametric line parser.

    Args:
        *args: Parametric line specification
        **kwargs: Additional options

    Returns:
        Object representing a parametric line
    """
    return type('ParametricLine', (), {
        '__str__': lambda self: 'ParametricLine',
    })()


class ParametricLineClass:
    """
    Parser for parametric line equations.

    Represents parametric lines like "<1, 2, 3> + t<4, 5, 6>" and validates
    that student answers represent the same line (possibly with different parameters
    or starting points).

    Attributes:
        equation: The original equation string
        point: A point on the line
        direction: Direction vector
        dimension: Dimensionality (2D or 3D)
    """

    def __init__(self, equation: str = "", **options):
        """
        Create a ParametricLine object.

        Args:
            equation: Parametric line like "<1, 2> + t<3, 4>"
            **options: Additional options

        Example:
            >>> line = ParametricLine("<1, 2, 3> + t<4, 5, 6>")
            >>> line = ParametricLine("<0, 1> + s<1, -1>")
        """
        self.equation = equation
        self.options = options
        self.point = None
        self.direction = None
        self.dimension = None
        self.parameter = None

        self._parse_equation(equation)

    def _parse_equation(self, equation: str) -> None:
        """
        Parse parametric line equation.

        Args:
            equation: Parametric line equation string
        """
        # Pattern: <...> + parameter<...>
        # Examples: "<1, 2> + t<3, 4>" or "<0, 0, 0> + s<1, 1, 1>"

        # Find all angle bracket groups
        bracket_pattern = r'<\s*([^>]+)\s*>'
        brackets = re.findall(bracket_pattern, equation)

        if len(brackets) < 2:
            raise ValueError(f"ParametricLine must have at least two vectors: {equation}")

        # Extract point (first vector)
        try:
            point_str = brackets[0]
            self.point = tuple(float(x.strip()) for x in point_str.split(','))
            self.dimension = len(self.point)
        except ValueError:
            raise ValueError(f"Cannot parse point from: {brackets[0]}")

        # Extract direction (last vector)
        try:
            dir_str = brackets[-1]
            self.direction = tuple(float(x.strip()) for x in dir_str.split(','))
        except ValueError:
            raise ValueError(f"Cannot parse direction from: {brackets[-1]}")

        # Extract parameter name (t, s, etc.)
        param_pattern = r'([a-zA-Z]+)\s*<'
        param_match = re.search(param_pattern, equation)
        if param_match:
            self.parameter = param_match.group(1)
        else:
            self.parameter = 't'  # Default

    def cmp(self, **options) -> 'ParametricLineChecker':
        """
        Get an answer checker for this ParametricLine.

        Returns:
            ParametricLineChecker configured for comparison

        Example:
            >>> line = ParametricLine("<1, 2> + t<3, 4>")
            >>> ANS(line.cmp())
        """
        return ParametricLineChecker(self, **options)

    def __str__(self) -> str:
        """Return string representation."""
        return self.equation

    def __repr__(self) -> str:
        """Return representation."""
        return f"ParametricLine({str(self)})"


class ParametricLineChecker:
    """
    Answer checker for ParametricLine comparison.

    Two parametric lines are equivalent if they represent the same infinite line,
    even if they:
    - Use different parameter names
    - Start at different points on the line
    - Use different direction vectors (scalar multiples of each other)
    """

    def __init__(self, reference: ParametricLine, **options):
        """
        Initialize checker with reference line.

        Args:
            reference: The correct ParametricLine
            **options: Checker options
        """
        self.reference = reference
        self.options = options
        self.tolerance = options.get('tolerance', 1e-6)

    def evaluate(self, student_answer: str) -> bool:
        """
        Check if student line matches reference.

        Args:
            student_answer: Student's parametric line

        Returns:
            True if lines are equivalent
        """
        try:
            student = ParametricLine(student_answer)
        except ValueError:
            return False

        # Check dimensions match
        if self.reference.dimension != student.dimension:
            return False

        # Check that direction vectors are parallel
        if not self._are_parallel(self.reference.direction, student.direction):
            return False

        # Check that student's point lies on reference line
        # Point P is on line Q + t*D if (P - Q) is parallel to D
        if not self._point_on_line(student.point, self.reference.point, self.reference.direction):
            return False

        return True

    def _are_parallel(self, vec1: Tuple[float, ...], vec2: Tuple[float, ...]) -> bool:
        """
        Check if two vectors are parallel (one is scalar multiple of other).

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            True if vectors are parallel
        """
        tolerance = self.tolerance

        # Find scaling factor
        scale = None
        for v1, v2 in zip(vec1, vec2):
            if abs(v1) > tolerance:
                if scale is None:
                    scale = v2 / v1
                else:
                    if abs(v2 / v1 - scale) > tolerance:
                        return False
            elif abs(v2) > tolerance:
                return False

        return True

    def _point_on_line(self, point: Tuple[float, ...], line_point: Tuple[float, ...],
                       direction: Tuple[float, ...]) -> bool:
        """
        Check if a point lies on a line.

        Args:
            point: Point to check
            line_point: A point on the line
            direction: Direction vector of line

        Returns:
            True if point is on line
        """
        tolerance = self.tolerance

        # Vector from line_point to point
        diff = tuple(p - l for p, l in zip(point, line_point))

        # Check if diff is parallel to direction
        return self._are_parallel(diff, direction)

    def __call__(self, student_answer: str) -> Dict[str, Any]:
        """
        Callable interface for compatibility with PG answer checkers.

        Args:
            student_answer: Student's parametric line

        Returns:
            Result dictionary with 'score' and 'message' keys
        """
        is_correct = self.evaluate(student_answer)
        return {
            'score': 1 if is_correct else 0,
            'message': '' if is_correct else 'Your line is not equivalent to the correct one'
        }


__all__ = [
    'ParametricLine',
    'ParametricLineChecker',
]
