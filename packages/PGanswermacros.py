"""
PGanswermacros.pl - Answer evaluation macros.

Top-level barrel module for short imports (1:1 parity with Perl PGanswermacros.pl).
Re-exports from pg_macros.PGanswermacros.

Usage:
    import PGanswermacros
    PGanswermacros.num_cmp(42)
    PGanswermacros.fun_cmp("x^2")

Reference: macros/core/PGanswermacros.pl
"""

from pg_macros.PGanswermacros import *

__all__ = [
    "num_cmp",
    "std_num_cmp",
    "fun_cmp",
    "str_cmp",
    "std_str_cmp",
    "interval_cmp",
    "vector_cmp",
    "matrix_cmp",
]

