"""
PG.pl - Core Program Generation Language functionality.

DEPRECATED: Use 'from webwork import *' instead.

This module is maintained for backwards compatibility only.
It re-exports from pg_macros.PG.

Legacy usage:
    import PG
    PG.DOCUMENT()
    PG.TEXT("Problem text")
    PG.ANS(answer)

Recommended usage:
    from webwork import *
    DOCUMENT()
    TEXT("Problem text")
    ANS(answer)

Reference: macros/PG.pl
"""

import warnings

# Emit deprecation warning
warnings.warn(
    "Importing from 'PG' is deprecated. Use 'from webwork import *' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from pg_macros.PG import *  # noqa: F401, F403

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
    # Solution/Hint
    "SOLUTION",
    "HINT",
    "COMMENT",
    # Macro loading
    "loadMacros",
    # Grading
    "install_problem_grader",
    # Utilities
    "not_null",
    "DEBUG_MESSAGE",
    "WARN_MESSAGE",
    # Random
    "random",
    "non_zero_random",
    "list_random",
    # Persistent data
    "persistent_data",
]
