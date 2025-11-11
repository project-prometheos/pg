"""
PGcourse.pl - Course-specific configuration.

Top-level barrel module for short imports (1:1 parity with Perl PGcourse.pl).
PGcourse.pl is typically empty/minimal in Perl - just loads core macros.

Usage:
    import PGcourse

Reference: macros/PGcourse.pl
"""

# PGcourse.pl is typically empty, just provides loadMacros
from pg_macros.core.pg_core import loadMacros

__all__ = ["loadMacros"]

