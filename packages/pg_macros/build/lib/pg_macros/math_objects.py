"""MathObjects convenience exports mirroring MathObjects.pl."""

from __future__ import annotations

from typing import Any

from .core import math_objects as _impl
from .runtime.context import Context, set_context, get_context
from .runtime.value import (
    Real,
    Complex,
    Infinity,
    Point,
    Vector,
    Matrix,
    List,
    String,
    Interval,
    Set,
    Union,
    Formula,
    Value,
    to_value,
)


Compute = _impl.Compute


def FormulaFactory(expression: str, **options: Any) -> Formula:
    """Create a Formula while respecting active context."""
    return Formula(expression, context=options.get('context', get_context()))


__exports__ = {
    'Compute': Compute,
    'Context': Context,
    'set_context': set_context,
    'Real': Real,
    'Complex': Complex,
    'Infinity': Infinity,
    'Point': Point,
    'Vector': Vector,
    'Matrix': Matrix,
    'List': List,
    'String': String,
    'Interval': Interval,
    'Set': Set,
    'Union': Union,
    'Formula': FormulaFactory,
    'Value': Value,
    'to_value': to_value,
}

__all__ = list(__exports__.keys())
