"""
MathObjects.pl - Math Object system.

Top-level barrel module for short imports (1:1 parity with Perl MathObjects.pl).
Re-exports from pg_macros.MathObjects.

Usage:
    import MathObjects
    MathObjects.Context()
    MathObjects.Formula("x^2")

Reference: macros/core/MathObjects.pl
"""

from pg_macros.MathObjects import *

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
]

