"""
MathObjects.pl - Math Object system.

DEPRECATED: Use 'from webwork import *' instead.

This module is maintained for backwards compatibility only.
It re-exports from pg_macros.MathObjects.

Legacy usage:
    import MathObjects
    MathObjects.Context()
    MathObjects.Formula("x^2")

Recommended usage:
    from webwork import *
    Context()
    Formula("x^2")

Reference: macros/core/MathObjects.pl
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "Importing from 'MathObjects' is deprecated. Use 'from webwork import *' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from pg_macros.MathObjects import *  # noqa: F401, F403

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

