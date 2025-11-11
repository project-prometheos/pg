"""
parserCheckboxList.pl - Checkbox list interface.

Top-level barrel module for short imports (1:1 parity with Perl parserCheckboxList.pl).
Re-exports from pg_macros.parsers.parserCheckboxList.

Usage:
    import parserCheckboxList
    parserCheckboxList.CheckboxList(["A", "B", "C"], ["A", "C"])

Reference: macros/parsers/parserCheckboxList.pl
"""

from pg_macros.parsers.parserCheckboxList import *

__all__ = ["CheckboxList"]

