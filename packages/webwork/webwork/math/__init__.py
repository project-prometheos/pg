"""
webwork.math - Mathematical objects and contexts.

This module provides intelligent mathematical objects for problem authoring:
- Context(): Configure mathematical contexts (Numeric, Complex, Vector, Matrix, etc.)
- Compute(): Parse and evaluate mathematical expressions
- Formula(): Create mathematical formulas with automatic differentiation
- Vector, Matrix, Point, Interval: Mathematical types
- String, List, Set: Container types

For typical problem authoring, import from webwork directly:
    from webwork import *

For explicit imports:
    from webwork.math import *
"""

from .objects import *  # noqa: F401, F403

__all__ = []  # Everything is re-exported above
