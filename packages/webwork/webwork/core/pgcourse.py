"""
pgcourse.py - Course-specific configuration.

Wraps the PGcourse.py barrel export for the webwork namespace.
PGcourse.pl is typically minimal in Perl - just provides loadMacros.

Reference: macros/core/PGcourse.pl
"""

import sys
from pathlib import Path

# Add packages directory to path so we can import top-level barrel modules
_packages_dir = Path(__file__).parent.parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))

from PGcourse import *  # noqa: F401, F403

__all__ = ["loadMacros"]
