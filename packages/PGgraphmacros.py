"""
PGgraphmacros.pl - 2D graphing functions.

Top-level barrel module for short imports (1:1 parity with Perl PGgraphmacros.pl).
Re-exports from pg_macros.graph.PGgraphmacros.

Usage:
    import PGgraphmacros
    PGgraphmacros.init_graph(-10, 10, -10, 10)

Reference: macros/graph/PGgraphmacros.pl
"""

from pg_macros.graph.PGgraphmacros import *

__all__ = ["init_graph", "add_functions", "Plot", "WWPlot", "Label", "Fun"]

