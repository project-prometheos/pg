"""
WeBWorK PG - Modern Python reimplementation of WeBWorK's PG system.

WeBWorK is an open-source online homework system for math and sciences courses.
This package provides the Problem Generation (PG) language for authoring math problems.

Quick Start
===========

Import all standard PG functionality:

    from webwork import *

    DOCUMENT()

    # Problem setup
    Context("Numeric")
    $a = random(2, 5)
    $answer = Compute("$a * x + 1")

    # Problem statement (PGML format)
    BEGIN_PGML
    Find the derivative of [``y = [$a]x + 1``]

    [_]{$answer}{20}
    END_PGML

    # Solution
    SOLUTION(PGML('''
    The derivative of a linear function [``y = [$a]x + 1``] is [``[$a]``].
    '''))

    ENDDOCUMENT()

Core Modules
============

- **webwork.core**: Core PG functionality
  - DOCUMENT(), ENDDOCUMENT(): Problem document structure
  - TEXT(), BEGIN_TEXT/END_TEXT: Output text
  - ANS(), NAMED_ANS(): Answer collection
  - PGML(): Markup language for problem authoring
  - loadMacros(): Load additional macro libraries

- **webwork.math**: Mathematical objects and contexts
  - Context(): Configure math domains (Numeric, Complex, Vector, Matrix, etc.)
  - Compute(), Formula(): Parse and evaluate expressions
  - Vector, Matrix, Point, Interval: Math types
  - String, List, Set: Container types

Documentation
==============

Full documentation available at: https://webwork.example.com/docs

Perl PG Reference
==================

This is a modern Python port of WeBWorK's PG system. Perl references are available at:
- Macro reference: https://webwork.maa.org/wiki/PG_Syntax
- Problem authoring: https://webwork.maa.org/wiki/Creating_WeBWorK_problems

Third-Party Usage
==================

To use webwork in your own projects:

1. Install the package:

       pip install webwork-pg

2. Create a .pyg file:

       from webwork import *

       @problem(id="unique.problem.id")
       def my_problem(seed: int = 0) -> None:
           # Your problem here
           pass

3. Run it:

       python my_problem.pyg

Version
=======

__version__ = "0.1.0"

Reference: WeBWorK Legacy PG (Perl) - macros/core/
"""

__version__ = "0.1.0"

# Import everything from core and math submodules
from .core import *  # noqa: F401, F403
from .math import *  # noqa: F401, F403

# Most commonly used items are explicitly listed for IDE autocompletion
__all__ = [
    # Version
    "__version__",

    # Document structure (from core.pg)
    "DOCUMENT",
    "ENDDOCUMENT",
    "PGEnvironment",
    "get_environment",
    "set_environment",

    # Text output
    "TEXT",
    "BEGIN_TEXT",
    "END_TEXT",
    "HEADER_TEXT",
    "POST_HEADER_TEXT",

    # Answer handling
    "ANS",
    "NAMED_ANS",
    "LABELED_ANS",
    "RECORD_ANS_NAME",
    "ans_rule_count",

    # Problem components
    "SOLUTION",
    "HINT",
    "COMMENT",

    # Markup language (from core.pgml)
    "PGML",

    # Utilities
    "loadMacros",
    "install_problem_grader",
    "random",
    "non_zero_random",
    "list_random",
    "DEBUG_MESSAGE",
    "WARN_MESSAGE",

    # HTML formatting
    "PAR",
    "BR",
    "BBOLD",
    "EBOLD",
    "BITALIC",
    "EITALIC",

    # Math Objects (from math.objects)
    "Context",
    "Compute",
    "Formula",
    "Real",
    "Complex",
    "Vector",
    "Point",
    "Matrix",
    "Interval",
    "Set",
    "String",
    "List",
    "Fraction",
]
