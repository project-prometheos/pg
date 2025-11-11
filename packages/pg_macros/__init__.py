"""
pg_macros - Macro system for WeBWorK PG

Provides macro loading and registration system similar to Perl's loadMacros().
"""

from .pg_macros.registry import (
    CORE_MACROS,
    OPTIONAL_MACROS,
    get_macro_info,
    is_core_macro,
    should_lazy_load,
    get_macros_by_category,
    get_all_macro_names,
)

__all__ = [
    "CORE_MACROS",
    "OPTIONAL_MACROS",
    "get_macro_info",
    "is_core_macro",
    "should_lazy_load",
    "get_macros_by_category",
    "get_all_macro_names",
]

