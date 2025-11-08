"""PGstandard macro bundle providing core PG functionality."""

from __future__ import annotations

from types import ModuleType
from typing import Any, Dict

from .core import pg_core as _pg_core
from .core import pg_standard as _std_macros
from .core import pg_basic_macros as _basic_macros
from .answers import pg_answer_macros as _answer_macros


def _collect_exports(module: ModuleType) -> Dict[str, Any]:
    exports: Dict[str, Any] = {}
    explicit = getattr(module, "__exports__", None)
    if explicit:
        for name in explicit:
            exports[name] = getattr(module, name)
        return exports

    for name in dir(module):
        if name.startswith('_'):
            continue
        value = getattr(module, name)
        if callable(value):
            exports[name] = value
    return exports


__exports__: Dict[str, Any] = {}
for _module in (_pg_core, _std_macros, _basic_macros, _answer_macros):
    __exports__.update(_collect_exports(_module))

globals().update(__exports__)

__all__ = sorted(__exports__.keys())
