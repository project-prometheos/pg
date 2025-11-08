"""PGchoice macro exports aggregating choice-related utilities."""

from __future__ import annotations

from types import ModuleType
from typing import Any, Dict

from .choice import pg_choice_macros as _legacy_choice
from .ui import choice_macros as _ui_choice


def _collect(module: ModuleType) -> Dict[str, Any]:
    exports: Dict[str, Any] = {}
    desired = getattr(module, '__exports__', None)
    if desired:
        for name in desired:
            exports[name] = getattr(module, name)
        return exports
    for name in dir(module):
        if name.startswith('_'):
            continue
        value = getattr(module, name)
        if callable(value):
            exports[name] = value
    return exports


__exports__ = {}
for _module in (_legacy_choice, _ui_choice):
    __exports__.update(_collect(_module))

globals().update(__exports__)

__all__ = sorted(__exports__.keys())
