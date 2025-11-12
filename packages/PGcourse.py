"""
PGcourse.pl - Course-specific configuration.

DEPRECATED: Use 'from webwork import *' instead.

This module is maintained for backwards compatibility only.
PGcourse.pl is typically empty/minimal in Perl - just loads core macros.

Legacy usage:
    import PGcourse

Recommended usage:
    from webwork import *

Reference: macros/PGcourse.pl
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "Importing from 'PGcourse' is deprecated. Use 'from webwork import *' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# PGcourse.pl is typically empty, just provides loadMacros
from pg_macros.core.pg_core import loadMacros  # noqa: F401

__all__ = ["loadMacros"]

