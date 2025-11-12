"""
objects.py - Math Objects system.

Wraps the MathObjects.py barrel export for the webwork namespace.
Provides intelligent mathematical objects: Context, Formula, Compute, Vector, Matrix, etc.

Reference: macros/core/MathObjects.pl
"""

import sys
from pathlib import Path

# Add packages directory to path so we can import top-level barrel modules
_packages_dir = Path(__file__).parent.parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))

from MathObjects import *  # noqa: F401, F403

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
