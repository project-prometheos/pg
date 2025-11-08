# pg_macros

Python ports of WeBWorK PG macro library.

Provides compatibility layer for legacy .pg problems while maintaining modern Python architecture.

## Macro Categories

### Core (pg_macros)
- **pg_standard** (PGstandard.pl): DOCUMENT/ENDDOCUMENT, TEXT, ANS, and PG basic macros.
- **math_objects** (MathObjects.pl): Compute/Formula adapters and context helpers.
- **pgml** (PGML.pl): PGML rendering, TeX/HTML sanitization.
- **pg_graph** (PGgraphmacros.pl): Deterministic graph builders.

### Answers
- **pg_answermacros** (PGanswermacros.pl): Numeric, formula, string evaluators.
- **parser_multi_answer** (parserMultiAnswer.pl): MultiAnswer grouping.
- **answer_format_help** (AnswerFormatHelp.pl): Inline help snippets.

### UI & Choice
- **pg_choice** (PGchoicemacros.pl): Multiple choice, Match, Select utilities.
- **parser_popup** (parserPopUp.pl): Popup and dropdown inputs.

### Contexts
- **context_fraction** (contextFraction.pl): Fraction context variants and helpers.
- Runtime helpers live under pg_macros.runtime.* (context stack, MathObject adapters, RNG, rendering, graph layer).

## Usage

Load macros and inject exports:

    from pg_macros import load_macros
    exports = load_macros("PGstandard.pl", "MathObjects.pl", "PGML.pl")
    TEXT = exports["TEXT"]
    TEXT("Problem statement")

## Architecture

Uses a registry pattern for dynamic macro loading:
1. Macros register themselves on import
2. load_macros() resolves requested files
3. Python implementations mirror Perl API

## Porting Guide

See PORTING.md for detailed instructions on porting Perl macros to Python.
