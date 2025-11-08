"""Popup parser macros."""

from __future__ import annotations

from typing import Any, Dict

from .parsers import parser_popup as _impl


__exports__ = {name: getattr(_impl, name) for name in getattr(_impl, '__exports__', [])}
if not __exports__:
    __exports__ = {
        name: getattr(_impl, name)
        for name in dir(_impl)
        if not name.startswith('_') and callable(getattr(_impl, name))
    }

globals().update(__exports__)

__all__ = list(__exports__.keys())
