"""
webwork.core - Core PG (Program Generation Language) functionality.

This module provides the fundamental PG macro functions needed for problem authoring:
- DOCUMENT() and ENDDOCUMENT() for document structure
- TEXT(), PGML() for problem statement rendering
- ANS() for answer collection
- Context() for mathematical contexts
- Random utilities for problem variation

For typical problem authoring, import from webwork directly:
    from webwork import *

For explicit imports:
    from webwork.core import *
"""

from .pg import *  # noqa: F401, F403
from .pgml import *  # noqa: F401, F403
from .pgstandard import *  # noqa: F401, F403
from .pgcourse import *  # noqa: F401, F403

__all__ = []  # Everything is re-exported above
