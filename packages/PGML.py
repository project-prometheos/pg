"""
PGML.pl - PG Markup Language.

Top-level barrel module for short imports (1:1 parity with Perl PGML.pl).
Re-exports from pg_macros.PGML.

Usage:
    import PGML
    PGML.PGML("Problem text in PGML format")

Reference: macros/core/PGML.pl
"""

from pg_macros.PGML import *

__all__ = ["PGML"]

