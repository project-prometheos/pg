"""
parserPopUp.pl - Popup menus and dropdowns.

Top-level barrel module for short imports (1:1 parity with Perl parserPopUp.pl).
Re-exports from pg_macros.parsers.parserPopUp.

Usage:
    import parserPopUp
    parserPopUp.PopUp(["choice1", "choice2"], 0)

Reference: macros/parsers/parserPopUp.pl
"""

from pg_macros.parsers.parserPopUp import *

__all__ = ["PopUp", "DropDown", "DropDownTF"]

