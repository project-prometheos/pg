"""
PGML.pl - PG Markup Language.

DEPRECATED: Use 'from webwork import *' instead.

This module is maintained for backwards compatibility only.
It re-exports from pg_macros.PGML.

Legacy usage:
    import PGML
    PGML.PGML("Problem text in PGML format")

Recommended usage:
    from webwork import *
    BEGIN_PGML
    Problem text in PGML format
    END_PGML

Reference: macros/core/PGML.pl
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "Importing from 'PGML' is deprecated. Use 'from webwork import *' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from pg_macros.PGML import *  # noqa: F401, F403

__all__ = ["PGML"]

