"""PGML macro exports."""

from __future__ import annotations

from typing import Any, Dict

from .core import pgml as _impl
from .runtime.render import render_pgml as _render_pgml, RenderResult


PGML = _impl.PGML
BEGIN_PGML = _impl.BEGIN_PGML
END_PGML = _impl.END_PGML
render_pgml = _render_pgml

__exports__: Dict[str, Any] = {
    'PGML': PGML,
    'BEGIN_PGML': BEGIN_PGML,
    'END_PGML': END_PGML,
    'render_pgml': render_pgml,
    'RenderResult': RenderResult,
}

__all__ = list(__exports__.keys())
