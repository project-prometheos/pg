"""
parserRadioButtons.pl - Radio button interface.

Top-level barrel module for short imports (1:1 parity with Perl parserRadioButtons.pl).
Re-exports from pg_macros.parsers.parserRadioButtons.

Usage:
    import parserRadioButtons
    parserRadioButtons.RadioButtons(["A", "B", "C"], 0)

Reference: macros/parsers/parserRadioButtons.pl
"""

from pg_macros.parsers.parserRadioButtons import *

__all__ = ["RadioButtons"]

