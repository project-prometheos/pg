"""
parserGraphTool.pl - Interactive graph tool.

Top-level barrel module for short imports (1:1 parity with Perl parserGraphTool.pl).
Re-exports from pg_macros.parsers.parserGraphTool.

Usage:
    import parserGraphTool
    parserGraphTool.GraphTool()

Reference: macros/parsers/parserGraphTool.pl
"""

from pg_macros.parsers.parserGraphTool import *

__all__ = ["GraphTool"]

