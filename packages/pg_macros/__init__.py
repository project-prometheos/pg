"""Top-level pg_macros package shim.

Extends the package search path so submodules under pg_macros/pg_macros are
importable both as ``pg_macros.*`` and ``pg_macros.pg_macros.*``.
"""

from __future__ import annotations

from pathlib import Path

# Ensure the nested package directory is on the module search path so imports
# like ``pg_macros.core`` resolve correctly.
_nested = Path(__file__).resolve().parent / "pg_macros"
if _nested.exists():
    __path__.append(str(_nested))  # type: ignore[name-defined]

from .pg_macros.registry import MacroRegistry, load_macros

__all__ = ["MacroRegistry", "load_macros"]
