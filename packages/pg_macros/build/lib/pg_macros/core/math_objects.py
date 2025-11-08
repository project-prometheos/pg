"""
MathObjects.pl - Load MathObjects system

Reference: macros/core/MathObjects.pl (89 lines)
"""

# Import MathObjects from pg_math
try:
    from pg_math import (
        Real, Complex, Infinity,
        Point, Vector, Matrix,
        List, String,
        Interval, Set, Union,
        Formula
    )
except ImportError:
    # Fallback if pg_math not available
    Real = None
    Complex = None
    Formula = None


def Compute(expr: str, **options):
    """
    Compute a mathematical expression.
    
    Reference: MathObjects.pl::Compute
    """
    if Formula is not None:
        return Formula(expr, **options)
    # Fallback to eval
    try:
        return eval(expr)
    except:
        return expr
