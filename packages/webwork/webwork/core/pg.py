"""
pg.py - Core PG (Program Generation Language) functionality.

Wraps the PG.py barrel export for the webwork namespace.
Provides DOCUMENT(), TEXT(), ANS(), and core PG functions.

Reference: macros/core/PG.pl
"""

import sys
from pathlib import Path

# Add packages directory to path so we can import top-level barrel modules
_packages_dir = Path(__file__).parent.parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))

from PG import *  # noqa: F401, F403

__all__ = [
    # Environment
    "PGEnvironment",
    "get_environment",
    "set_environment",
    # Document lifecycle
    "DOCUMENT",
    "ENDDOCUMENT",
    "_PG_init",
    # Text output
    "TEXT",
    "BEGIN_TEXT",
    "END_TEXT",
    "HEADER_TEXT",
    "POST_HEADER_TEXT",
    "STOP_RENDERING",
    # Answers
    "ANS",
    "NAMED_ANS",
    "LABELED_ANS",
    "RECORD_ANS_NAME",
    "RECORD_IMPLICIT_ANS_NAME",
    "NEW_ANS_NAME",
    "ANS_NUM_TO_NAME",
    "RECORD_FORM_LABEL",
    "RECORD_EXTRA_ANSWERS",
    "ans_rule_count",
    # Solutions and hints
    "SOLUTION",
    "HINT",
    "COMMENT",
    # Utilities
    "loadMacros",
    "install_problem_grader",
    "not_null",
    "DEBUG_MESSAGE",
    "WARN_MESSAGE",
]
