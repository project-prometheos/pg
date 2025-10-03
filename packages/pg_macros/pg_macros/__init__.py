"""
pg_macros - Python ports of WeBWorK PG macro library

Provides compatibility layer for legacy .pg problems.

Reference: macros/ directory in legacy Perl codebase
"""

from .registry import MacroRegistry, loadMacros, register_macro_file

__all__ = [
    "MacroRegistry",
    "loadMacros",
    "register_macro_file",
]
