"""
PG.py - Core PG module (Python version of PG.pl).

This module is loaded with unrestricted permissions by the translator.
It exports all core PG functions to the problem namespace.

Reference: macros/PG.pl
"""

# Import all core functions from pg_core
from pg_macros.core.pg_core import *


def _PG_init():
    """
    Initialize PG environment when module is loaded.
    
    This is called automatically by MacroLoader.unrestricted_load()
    
    Reference: PG.pl::_PG_init (line 73)
    """
    # Set version
    import sys
    frame = sys._getframe(1)
    frame.f_globals["VERSION"] = "PG-2.20-Python"
    
    # Export all core functions to problem namespace
    for name in __all__:
        if name != "_PG_init":
            frame.f_globals[name] = globals()[name]
