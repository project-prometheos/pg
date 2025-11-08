"""Value adapters bridging MathObjects-style APIs."""

from __future__ import annotations

from typing import Any

from pg_math.numeric import Real, Complex, Infinity
from pg_math.geometric import Point, Vector, Matrix
from pg_math.collections import List, String
from pg_math.sets import Interval, Set, Union
from pg_math.formula import Formula
from pg_math.value import MathValue as Value


def to_value(obj: Any) -> Value | Any:
    """Coerce plain Python types into MathObject values when possible."""
    if isinstance(obj, Value):
        return obj
    if isinstance(obj, (int, float)):
        return Real(obj)
    if isinstance(obj, complex):
        return Complex(obj.real, obj.imag)
    if isinstance(obj, str):
        return String(obj)
    if isinstance(obj, (list, tuple)):
        return List([to_value(item) for item in obj])
    return obj


__all__ = [
    'Real',
    'Complex',
    'Infinity',
    'Point',
    'Vector',
    'Matrix',
    'List',
    'String',
    'Interval',
    'Set',
    'Union',
    'Formula',
    'Value',
    'to_value',
]
