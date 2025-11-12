"""
pgml.py - PG Markup Language (PGML) support.

Wraps the PGML.py barrel export for the webwork namespace.
Provides PGML() function for markup-based problem authoring.

Reference: macros/core/PGML.pl
"""

import sys
from pathlib import Path

# Add packages directory to path so we can import top-level barrel modules
_packages_dir = Path(__file__).parent.parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))

from PGML import *  # noqa: F401, F403

__all__ = ["PGML"]
