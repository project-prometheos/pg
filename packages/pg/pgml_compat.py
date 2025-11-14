"""
PGML.pl - PGML markup language support.

Top-level barrel module for short imports (1:1 parity with Perl PGML.pl).
Re-exports from pg.macros.core.pgml.

Usage:
    from pg.pgml_compat import PGML, BEGIN_PGML, END_PGML

Reference: macros/core/PGML.pl
"""

from pg.macros.core.pgml import PGML, BEGIN_PGML, END_PGML

__all__ = [
    "PGML",
    "BEGIN_PGML",
    "END_PGML",
]
