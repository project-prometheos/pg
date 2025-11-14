"""
MathObjects.pl - MathObjects for problem authoring.

Top-level barrel module for short imports (1:1 parity with Perl MathObjects.pl).
Re-exports from pg.macros.MathObjects which provides complete MathObjects from pg.math.

Usage:
    from pg.mathobjects import Context, Formula, Real, Compute
    Context("Numeric")
    f = Formula("x^2")

Note: This is a barrel module that provides a clean top-level import API.
It aggregates multiple submodules from pg.macros for user convenience.

Reference: macros/core/MathObjects.pl
"""

from pg.macros.MathObjects import (
    Context,
    Formula,
    Real,
    Complex,
    Compute,
    Vector,
    Point,
    Interval,
    Set,
    String,
    List,
    Matrix,
    Fraction,
)

# Also export Infinity and Union from pg.math
from pg.math import Infinity, Union

__all__ = [
    "Context",
    "Formula",
    "Real",
    "Complex",
    "Compute",
    "Vector",
    "Point",
    "Interval",
    "Set",
    "String",
    "List",
    "Matrix",
    "Fraction",
    "Union",
    "Infinity",
]
