"""
pg_macros - Macro system for WeBWorK PG

Provides macro loading and registration system similar to Perl's loadMacros().
"""

from .pg_macros.registry import MacroRegistry, load_macros

__all__ = ["MacroRegistry", "load_macros"]

