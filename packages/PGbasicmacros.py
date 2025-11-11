"""
PGbasicmacros.pl - Basic functions and constants for PG problems.

Top-level barrel module for short imports (1:1 parity with Perl PGbasicmacros.pl).
Re-exports from pg_macros.PGbasicmacros.

Usage:
    import PGbasicmacros
    PGbasicmacros.ans_rule(20)
    PGbasicmacros.PAR

Reference: macros/core/PGbasicmacros.pl
"""

from pg_macros.PGbasicmacros import *

__all__ = [
    # Initialization
    "_PGbasicmacros_init",
    # Display constants
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
    # Answer blanks
    "ans_rule",
    "NAMED_ANS_RULE",
    "ans_box",
    "NAMED_ANS_BOX",
    "ans_radio_buttons",
    "NAMED_ANS_RADIO_BUTTONS",
    "pop_up_list",
    "NAMED_POP_UP_LIST",
    # Utilities
    "MODES",
    "image",
]

