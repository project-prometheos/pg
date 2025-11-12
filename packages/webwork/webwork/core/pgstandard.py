"""
pgstandard.py - Standard PG macros.

Wraps the PGstandard.py barrel export for the webwork namespace.
This is the primary entry point for most PG problems.

PGstandard.pl in Perl loads: PG.pl, PGbasicmacros.pl, PGanswermacros.pl, PGauxiliaryFunctions.pl

Reference: macros/core/PGstandard.pl
"""

import sys
from pathlib import Path

# Add packages directory to path so we can import top-level barrel modules
_packages_dir = Path(__file__).parent.parent.parent.parent
if str(_packages_dir) not in sys.path:
    sys.path.insert(0, str(_packages_dir))

from PGstandard import *  # noqa: F401, F403

__all__ = [
    # From PG.pl (pg_core)
    "PGEnvironment",
    "get_environment",
    "set_environment",
    "DOCUMENT",
    "ENDDOCUMENT",
    "_PG_init",
    "TEXT",
    "BEGIN_TEXT",
    "END_TEXT",
    "HEADER_TEXT",
    "POST_HEADER_TEXT",
    "STOP_RENDERING",
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
    "SOLUTION",
    "HINT",
    "COMMENT",
    "loadMacros",
    "install_problem_grader",
    "not_null",
    "DEBUG_MESSAGE",
    "WARN_MESSAGE",
    "random",
    "non_zero_random",
    "list_random",
    "persistent_data",
    # From PGbasicmacros.pl (pg_basic_macros)
    "_PGbasicmacros_init",
    "PAR",
    "BR",
    "BRBR",
    "LQ",
    "RQ",
    "BBOLD",
    "EBOLD",
    "BITALIC",
    "EITALIC",
    "BUL",
    "EUL",
    "BCENTER",
    "ECENTER",
    "HR",
    "NBSP",
    "PI",
    "E",
    # From PGanswermacros.pl (pg_answer_macros)
    "num_cmp",
    "std_num_cmp",
    "fun_cmp",
    "str_cmp",
    "std_str_cmp",
    "interval_cmp",
    "vector_cmp",
    "matrix_cmp",
]
