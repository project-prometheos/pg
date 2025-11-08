"""Course-specific macro initialization hooks."""

from __future__ import annotations

from typing import Any, Callable, Iterable, List

from .registry import load_macros as _load_macros


_course_hooks: List[Callable[[dict[str, Any]], None]] = []


def _PGcourse_init() -> None:
    """Mirror Perl macro entry point (no-op by default)."""
    return None


def register_course_hook(callback: Callable[[dict[str, Any]], None]) -> None:
    """Register a callback to customize the PG environment."""
    _course_hooks.append(callback)


def run_course_initializers(envir: dict[str, Any]) -> None:
    """Execute registered course initialization hooks."""
    for hook in _course_hooks:
        hook(envir)


def load_course_macros(*macro_names: str) -> dict[str, Any]:
    """Convenience wrapper to load additional course macros."""
    return _load_macros(*macro_names)


__exports__ = {
    '_PGcourse_init': _PGcourse_init,
    'register_course_hook': register_course_hook,
    'run_course_initializers': run_course_initializers,
    'load_course_macros': load_course_macros,
}

__all__ = list(__exports__.keys())
