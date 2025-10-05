"""
PG MathObjects - Python implementation of WeBWorK MathObjects.

This package provides the MathObjects framework for creating, manipulating,
and checking mathematical expressions in PG problems.
"""

from .context import Context, get_current_context
from .value import Value
from .real import Real
from .formula import Formula
from .formula_up_to_constant import FormulaUpToConstant
from .compute import Compute

__all__ = [
    "Context",
    "get_current_context",
    "Value",
    "Real",
    "Formula",
    "FormulaUpToConstant",
    "Compute",
]

__version__ = "0.1.0"
