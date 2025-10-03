"""
MathObjects.pl - MathObjects integration

Python port of macros/core/MathObjects.pl
Provides MathObject constructors and utilities.

Reference: MathObjects.pl
"""

from pg_math import Complex, Formula, Interval, Matrix, Point, Real, Vector
from pg_parser import Context

# Export list
__exports__ = [
    "Real",
    "Complex",
    "Formula",
    "Compute",
    "Point",
    "Vector",
    "Matrix",
    "Interval",
    "Context",
]


def Compute(expression: str, **kwargs) -> Formula:
    """
    Compute a mathematical expression (alias for Formula).

    This is the primary way to create formulas in PG problems.

    Args:
        expression: Mathematical expression string
        **kwargs: Additional options

    Returns:
        Formula object

    Example:
        >>> f = Compute("x^2 + 2*x + 1")
        >>> f.eval(x=2)  # Returns 9

    Reference: MathObjects.pl::Compute
    """
    return Formula(expression, **kwargs)
