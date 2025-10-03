"""
pg_math - MathObjects system for WeBWorK PG

Intelligent mathematical value types with:
- Type promotion
- Operator overloading
- Fuzzy comparison
- Multiple output formats

Reference: lib/Value.pm and lib/Value/*.pm in legacy Perl codebase
"""

from .collections import List, String
from .formula import Formula
from .geometric import Matrix, Point, Vector
from .numeric import Complex, Infinity, Real
from .sets import Interval, Set, Union
from .value import MathValue, ToleranceMode, TypePrecedence

__all__ = [
    "MathValue",
    "TypePrecedence",
    "ToleranceMode",
    "Real",
    "Complex",
    "Infinity",
    "Point",
    "Vector",
    "Matrix",
    "List",
    "String",
    "Interval",
    "Set",
    "Union",
    "Formula",
]
