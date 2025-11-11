"""
parserMultiAnswer.pl - Multiple related answers.

Top-level barrel module for short imports (1:1 parity with Perl parserMultiAnswer.pl).
Re-exports from pg_macros.parsers.parserMultiAnswer.

Usage:
    import parserMultiAnswer
    parserMultiAnswer.MultiAnswer(ans1, ans2)

Reference: macros/parsers/parserMultiAnswer.pl
"""

from pg_macros.parsers.parserMultiAnswer import *

__all__ = ["MultiAnswer"]

