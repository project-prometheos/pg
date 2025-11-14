# Phase 3 Macro Priorities Analysis
## Research Report: Remaining 10 Failing Tutorial Problems

**Date**: 2025-11-14  
**Repository**: d:\pg (WeBWorK PG - Monorepo)  
**Branch**: refactor/webwork-pg  
**Analysis Scope**: 10 failing tutorial problems requiring macro implementations

---

## Executive Summary

Analysis of the 10 remaining failing tutorial problems identifies **3 high-impact macros** that will resolve the most failures with manageable implementation complexity:

1. **contextUnits.pl** - Fixes AnswerWithUnits (enables units in formulas)
2. **parserFunction.pl** - Fixes HeavisideStep (add custom functions to context)
3. **plots.pl** - Fixes ParametricPlotAlt (modern plotting library)

Additionally, 5 supporting macros need implementation to fix the remaining problems:
- **scaffold.pl** - Multi-part problem scaffolding
- **parserPopUp.pl** - Already in registry (needs verification)
- **PGtikz.pl** - TikZ image generation
- **PGchoicemacros.pl** - Choice/shuffle utilities
- **PGgraders.pl** - Custom grading system

---

## Detailed Problem Analysis

### Problem 1: AnswerWithUnits.pg
**Location**: `d:/pg/tutorial/sample-problems/DiffCalc/AnswerWithUnits.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'contextUnits.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `Context('Units')` - Units context selection
- `Context()->withUnitsFor('length', 'time')` - Enable specific unit categories
- `Context()->assignUnits(t => 's')` - Assign units to variables
- `Formula("(-16 t^2 + $v0 t) ft")` - Formula with units
- `$h->D('t')` - Differentiation with unit propagation
- `$v->eval(t => value)` - Evaluation with unit checking

**Implementation Complexity**: **MEDIUM-HIGH** (2262 lines in Perl)
- Complex unit system with ~40+ unit categories
- Requires unit algebra (multiplication, division, conversion)
- Must propagate units through mathematical operations
- Answer checking must validate unit correctness

**Impact**: Fixes 1 problem, blocks basic unit support

---

### Problem 2: HeavisideStep.pg
**Location**: `d:/pg/tutorial/sample-problems/DiffEq/HeavisideStep.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'parserFunction.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `parserFunction('u(t)' => 'step(t)')` - Define custom function
- `Context()->functions->add(...)` - Add function to context
- `Parser::Legacy::Numeric` class usage
- Function evaluation in formulas: `$f->eval(t => value)`
- Custom answer checking with limits/test points

**Implementation Complexity**: **LOW** (~200 lines in Perl)
- Simple wrapper around Context->functions->add()
- Parses function definitions in string form
- Creates Parser::Function objects
- Minimal new functionality - mostly configuration

**Perl Reference Implementation Size**: 125 lines  
**Impact**: Fixes 1 problem, enables custom function definition for all users

---

### Problem 3: MatchingAlt.pg
**Location**: `d:/pg/tutorial/sample-problems/Misc/MatchingAlt.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'parserPopUp.pl', 'PGgraders.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `DropDown(['A', 'B', 'C'], correct_index)` - Dropdown menu creation
- `custom_problem_grader_fluid` - Incremental grading
- `$ENV{grader_numright}` / `$ENV{grader_scores}` - Grading configuration
- `install_problem_grader(~~&custom_problem_grader_fluid)` - Install grader

**Implementation Complexity**: **LOW for DropDown, MEDIUM for grading**
- **parserPopUp.py** already exists (594 lines in Perl, implemented in Python)
- **PGgraders.pl** needs implementation (~400+ lines in Perl)

**Impact**: Fixes 1 problem; parserPopUp is core for multiple problems

---

### Problem 4: ParametricPlotAlt.pg
**Location**: `d:/pg/tutorial/sample-problems/Parametric/ParametricPlotAlt.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'plots.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `Plot(xmin => ..., xmax => ..., ...)` - Create plot object
- `$plot->add_function([x_expr, y_expr], 't', t_min, t_max, ...)` - Add parametric curve
- Supports parametric/multi-dimensional plotting
- Configuration: axes, labels, scaling
- Image rendering to PNG/SVG/JSXGraph

**Implementation Complexity**: **HIGH** (590 lines in Perl)
- Modern plotting library supporting multiple backends (JSXGraph, TikZ, GD)
- Parametric curve support
- Coordinate transformation and scaling
- Dynamic JavaScript generation for web rendering
- Backend abstraction for TikZ/GD compatibility

**Impact**: Fixes 1 problem; enables modern graph generation for many problems

---

### Problem 5: CustomAnswerCheckers.pg
**Location**: `d:/pg/tutorial/sample-problems/ProblemTechniques/CustomAnswerCheckers.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `$ans = Compute('pi/3')->cmp(checker => sub { ... })` - Custom checker function
- `Value->Error("message")` - Error handling in checker
- `$ansHash` parameter access (student/correct answers, preview state)

**Implementation Complexity**: **LOW** (already in core MathObjects)
- Custom checker support is fundamental to answer evaluation
- Likely already working in Python implementation
- Only needs verification of callback mechanism

**Impact**: Core feature - should already work; verify in testing

---

### Problem 6: GraphsInTables.pg
**Location**: `d:/pg/tutorial/sample-problems/ProblemTechniques/GraphsInTables.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'PGtikz.pl', 'parserPopUp.pl', 'PGchoicemacros.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `createTikZImage()` - Create TikZ drawing
- `$graph->tikzLibraries('arrows.meta')` - Add TikZ libraries
- `BEGIN_TIKZ ... END_TIKZ` - Embedded TikZ code
- `shuffle(n)` / `invert(@array)` - Array utility functions
- `DropDown()` - Dropdown menus (from parserPopUp)
- `LayoutTable()` - Nicely formatted layout tables

**Implementation Complexity**: **MEDIUM**
- **PGtikz.pl**: 122 lines (wraps TikZ), already partially implemented (tikz_image.py exists)
- **PGchoicemacros.pl**: 400+ lines (shuffle, invert, other utilities)
- **niceTables.pl**: Automatically loaded by PGML.pl (check PGML implementation)

**Impact**: Fixes 1 problem; enables TikZ-based graph generation

---

### Problem 7: LinearRegression.pg
**Location**: Search didn't find this file - may not exist yet

**Status**: Unknown - file not found in tutorial directory

**Note**: This may be a placeholder name; actual file might be in ProblemTechniques directory with different name

---

### Problem 8: ProvingTrigIdentities.pg
**Location**: `d:/pg/tutorial/sample-problems/Trig/ProvingTrigIdentities.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', 'scaffold.pl', 'PGcourse.pl');
```

**Key Features Used**:
- `Scaffold::Begin(is_open => 'correct_or_first_incorrect')` - Start scaffold
- `Section::Begin('Part N')` / `Section::End()` - Define scaffold sections
- `[_]{ formula }{width}` - Answer blanks within sections
- Custom function definition via Context()->functions->add()

**Implementation Complexity**: **MEDIUM** (767 lines in Perl)
- Complex state management for section visibility/correctness
- Conditional rendering based on answer submission
- JavaScript support for collapse/expand UI
- Integration with answer checker system

**Impact**: Fixes 1 problem; enables multi-part scaffolded problems

---

### Problem 9: VectorOperations.pg
**Location**: `d:/pg/tutorial/sample-problems/VectorCalc/VectorOperations.pg`

**Required Macros**:
```perl
loadMacros('PGstandard.pl', 'PGML.pl', '
