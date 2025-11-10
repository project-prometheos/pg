# Complete Stub Migration Plan: 73 Stubs → Proper Macro Modules

## Overview

**Goal**: Migrate all 73 remaining stubs from `in_process_sandbox.py` to proper Python macro modules with 1:1 Perl parity. Remove fallback stubs once tests pass.

**Current Status**:
- ✅ 3 stubs migrated (GraphTool, DraggableProof, LayoutTable - partial implementations)
- ⏳ 73 stubs remaining in sandbox
- 📊 Test pass rate: 149/157 (94.9%)

**Success Criteria**:
- All 73 stubs migrated to proper macro modules
- Zero stub definitions remain in `in_process_sandbox.py`
- Test pass rate maintained at ≥95% (≥149/157)
- All modules documented with Perl source references
- Registry maps all .pl files used in problems

---

## Strategy: Aggressive Phased Migration

**Approach**: Create proper Python modules with 1:1 Perl parity, remove inline stubs immediately after validation.

**Key Principles**:
1. **No Fallbacks** - Once migrated and tested, remove sandbox stub entirely
2. **Perl Parity** - Port actual Perl logic, not just stub interfaces
3. **Test-Driven** - Each module must pass unit + integration tests
4. **Incremental** - One phase at a time, validate before moving forward

---

## Complete Stub Inventory

### Summary by Category

| Category | Stub Count | Priority | Estimated LOC |
|----------|-----------|----------|---------------|
| Graph | 9 | HIGH | 2800-4200 |
| Parsers | 10 | HIGH | 1550-2350 |
| Math Utilities | 9 | MEDIUM | 550-850 |
| Core | 9 | MEDIUM | 1000-1500 |
| Answers | 3 | MEDIUM | 450-700 |
| UI | 2 | LOW | 220-330 |
| Contexts | 1 | LOW | 100-150 |
| MathObjects Fallback | 19 | LOW | 1500-2000 |
| Perl Utilities | 4 | LOW | 120-200 |

**Total**: 73 stubs, ~8290-12280 lines of code

---

## Phase 1: Critical Graphing Infrastructure (Week 1-2)

**Priority**: ⚠️ URGENT - Blocks 30%+ of graphing problems

### Module 1: `pg_macros.graph.pg_graph`

**Source**: `macros/graph/PGgraphmacros.pl`

**Implements**:
- `init_graph()` - WWPlot canvas initialization
  - Creates graph with bounding box, axes, grid
  - Configures labels, ticks, colors
  - Returns WWPlot object
- `add_functions()` - Add function plots to graph
  - Plots mathematical functions
  - Handles domain restrictions
- `Plot()` - 2D plotting wrapper

**Complexity**: HARD (500-800 LOC)

**Registry Mapping**:
```python
"PGgraphmacros.pl": "pg_macros.graph.pg_graph"
```

**Key Perl Functions to Port**:
```perl
# From PGgraphmacros.pl
init_graph($xmin, $xmax, $ymin, $ymax, %options)
add_functions($graph, $f1, $f2, ...)
```

**Sandbox Changes**:
- Remove lines 1163-1172 (`init_graph` stub)
- Remove lines 1174-1176 (`add_functions` stub)
- Remove lines 976-983 (`Plot` stub)
- Import: `from pg_macros.graph.pg_graph import init_graph, add_functions, Plot`

**Testing**:
```bash
pytest packages/pg_macros/tests/test_pg_graph.py
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "GraphTool"
```

---

### Module 2: `pg_macros.graph.tikz_image`

**Source**: `macros/graph/PGtikz.pl`

**Implements**:
- `createTikZImage()` - TikZ graphics wrapper
  - Wraps TikZ LaTeX environment
  - Manages TikZ libraries and packages
  - Handles BEGIN_TIKZ/END_TIKZ blocks

**Complexity**: MEDIUM-HARD (300-500 LOC)

**Registry Mapping**:
```python
"PGtikz.pl": "pg_macros.graph.tikz_image"
```

**Key Perl Functions to Port**:
```perl
# From PGtikz.pl
createTikZImage()
tikzLibraries(@libraries)
texPackages(@packages)
```

**Sandbox Changes**:
- Remove lines 1187-1197 (`createTikZImage` stub)
- Import: `from pg_macros.graph.tikz_image import createTikZImage`

**Testing**:
```bash
pytest packages/pg_macros/tests/test_tikz_image.py
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "TikZ"
```

---

### Module 3: `pg_macros.graph.latex_image`

**Source**: `macros/graph/PGlateximage.pl`

**Implements**:
- `createLaTeXImage()` - LaTeX graphics wrapper
  - Wraps LaTeX environment for custom graphics
  - Manages LaTeX packages
  - Handles BEGIN_LATEX_IMAGE/END_LATEX_IMAGE blocks

**Complexity**: MEDIUM-HARD (300-500 LOC)

**Registry Mapping**:
```python
"PGlateximage.pl": "pg_macros.graph.latex_image"
```

**Key Perl Functions to Port**:
```perl
# From PGlateximage.pl
createLaTeXImage()
texPackages(@packages)
```

**Sandbox Changes**:
- Remove lines 1178-1185 (`createLaTeXImage` stub)
- Import: `from pg_macros.graph.latex_image import createLaTeXImage`

**Testing**:
```bash
pytest packages/pg_macros/tests/test_latex_image.py
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "LaTeX or Image"
```

---

**Phase 1 Deliverables**:
- ✅ 3 graph modules implemented
- ✅ 6 stubs removed from sandbox
- ✅ Registry updated with 2 new mappings
- ✅ Tests pass: ≥149/157
- ✅ Graphing problems functional

---

## Phase 2: Essential Parsers (Week 2-3)

**Priority**: 🔴 HIGH - Common in physics/calculus problems

### Module 4: `pg_macros.parsers.parser_number_with_units`

**Source**: `macros/parsers/parserNumberWithUnits.pl`

**Implements**:
- `NumberWithUnits` class
  - Parses "5 m/s", "9.8 m/s^2", etc.
  - Validates unit consistency
  - Supports unit conversion

**Complexity**: MEDIUM (200-400 LOC)

**Registry Mapping**:
```python
"parserNumberWithUnits.pl": "pg_macros.parsers.parser_number_with_units"
```

**Key Perl Functions to Port**:
```perl
# From parserNumberWithUnits.pl
NumberWithUnits($value, $units)
$obj->cmp()
```

**Sandbox Changes**:
- Remove lines 1097-1103 (`NumberWithUnits` stub)
- Import: `from pg_macros.parsers.parser_number_with_units import NumberWithUnits`

---

### Module 5: `pg_macros.parsers.parser_implicit_plane`

**Source**: `macros/parsers/parserImplicitPlane.pl`

**Implements**:
- `ImplicitPlane` class
  - Parses "2x + 3y - z = 5"
  - Validates plane equations
  - Checks student answers

**Complexity**: MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"parserImplicitPlane.pl": "pg_macros.parsers.parser_implicit_plane"
```

**Sandbox Changes**:
- Remove lines 1128-1132 (`ImplicitPlane` stub)

---

### Module 6: `pg_macros.parsers.parser_parametric_line`

**Source**: `macros/parsers/parserParametricLine.pl`

**Implements**:
- `ParametricLine` class
  - Parses parametric line equations
  - Validates direction vectors
  - Checks equivalence

**Complexity**: MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"parserParametricLine.pl": "pg_macros.parsers.parser_parametric_line"
```

**Sandbox Changes**:
- Remove lines 1122-1126 (`ParametricLine` stub)

---

### Module 7: `pg_macros.parsers.parser_implicit_equation`

**Source**: `macros/parsers/parserImplicitEquation.pl`

**Implements**:
- `ImplicitEquation` class
  - Parses "x^2 + y^2 = 25"
  - Validates implicit equations
  - Checks student solutions

**Complexity**: MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"parserImplicitEquation.pl": "pg_macros.parsers.parser_implicit_equation"
```

**Sandbox Changes**:
- Remove lines 1105-1110 (`ImplicitEquation` stub)

---

### Module 8: `pg_macros.parsers.parser_solution_for`

**Source**: `macros/parsers/parserSolutionFor.pl`

**Implements**:
- `SolutionFor` class
  - Checks if expression solves equation
  - Used in ODE problems
  - Validates symbolic solutions

**Complexity**: MEDIUM (100-200 LOC)

**Registry Mapping**:
```python
"parserSolutionFor.pl": "pg_macros.parsers.parser_solution_for"
```

**Sandbox Changes**:
- Remove lines 1112-1120 (`SolutionFor` stub)

---

**Phase 2 Deliverables**:
- ✅ 5 parser modules implemented
- ✅ 5 stubs removed from sandbox
- ✅ Registry updated with 5 new mappings
- ✅ Tests pass: ≥149/157
- ✅ Physics/calculus problems functional

---

## Phase 3: Problem Structure & UI (Week 3-4)

**Priority**: 🟡 HIGH - Sequential problems and formatting

### Module 9: `pg_macros.core.scaffold`

**Source**: `macros/ui/scaffold.pl`

**Implements**:
- `Scaffold` class - Multi-section problem structure
  - Manages problem sections with dependencies
  - Controls section visibility based on completion
  - Handles scoring across sections
- `Section` class - Individual problem section
  - Section content and answers
  - Completion tracking

**Complexity**: MEDIUM-HARD (400-600 LOC)

**Registry Mapping**:
```python
"scaffold.pl": "pg_macros.ui.scaffold"  # Already mapped but not implemented
```

**Key Perl Functions to Port**:
```perl
# From scaffold.pl
Scaffold(@sections, %options)
Section($content, @answers)
```

**Sandbox Changes**:
- Remove lines 378-400 (`Scaffold`, `Section` classes in fallback)
- Import: `from pg_macros.ui.scaffold import Scaffold, Section`

**Testing**:
```bash
pytest packages/pg_macros/tests/test_scaffold.py
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "Scaffold"
```

---

### Module 10: Complete `pg_macros.ui.nice_tables`

**Source**: `macros/ui/niceTables.pl`

**Current Status**: Partially implemented (LayoutTable exists)

**Enhance with**:
- `DataTable()` - Data table with headers
- `BeginTable()` - Start table environment
- `Row()` - Table row
- `EndTable()` - End table environment
- Complete `LayoutTable()` implementation with:
  - Alignment options
  - Cell styling
  - Accessibility features

**Complexity**: MEDIUM (200-300 LOC additional)

**Sandbox Changes**:
- Remove lines 2233-2243 (`LayoutTable` stub)
- Use complete module implementation

**Testing**:
```bash
pytest packages/pg_macros/tests/test_nice_tables.py
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "Table"
```

---

**Phase 3 Deliverables**:
- ✅ 2 core modules implemented/completed
- ✅ 3 stubs removed from sandbox (Scaffold, Section, LayoutTable)
- ✅ Registry updated
- ✅ Tests pass: ≥149/157
- ✅ Sequential and formatted problems functional

---

## Phase 4: Math Utilities (Week 4)

**Priority**: 🟢 MEDIUM - Common utility functions

### Module 11: `pg_macros.math.vector_utils`

**Source**: `lib/Value.pm` (Vector methods in Perl MathObjects)

**Implements**:
- `norm()` - Vector magnitude
  - Computes ||v|| = √(v₁² + v₂² + ... + vₙ²)
  - Works with Vector objects
- `unit()` - Unit vector
  - Returns v/||v||
  - Handles zero vector case
- `Line` class - Geometric line
  - Point-slope representation
  - Intersection calculations

**Complexity**: EASY-MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"Value.pl": "pg_macros.math.vector_utils"  # Partial port
```

**Sandbox Changes**:
- Remove lines 932-949 (`norm`, `unit` stubs)
- Remove lines 1199-1204 (`Line` stub)
- Import: `from pg_macros.math.vector_utils import norm, unit, Line`

---

### Module 12: `pg_macros.math.auxiliary_functions`

**Source**: `macros/core/PGauxiliaryFunctions.pl`

**Implements**:
- `Round($x, $n)` - Round to n decimal places
- `nicestring($coeffs, %options)` - Format polynomial as string
  - "x^2 + 2x - 3" from [1, 2, -3]
  - Handles various formatting options
- `randomPerson()` - Generate random person name
  - Returns object with first/last name
- `non_zero_point3D()` - Random non-zero 3D point
- `non_zero_vector3D()` - Random non-zero 3D vector

**Complexity**: EASY-MEDIUM (200-300 LOC)

**Registry Mapping**:
```python
"PGauxiliaryFunctions.pl": "pg_macros.math.auxiliary_functions"
```

**Sandbox Changes**:
- Remove lines 918-923 (`non_zero_point3D`)
- Remove lines 925-930 (`non_zero_vector3D`)
- Remove lines 993-1040 (`nicestring`)
- Remove lines 1093-1095 (`Round`)
- Remove lines 1134-1154 (`randomPerson`)
- Import: `from pg_macros.math.auxiliary_functions import *`

---

**Phase 4 Deliverables**:
- ✅ 2 math utility modules implemented
- ✅ 7 stubs removed from sandbox
- ✅ Registry updated with 2 new mappings
- ✅ Tests pass: ≥149/157
- ✅ Math utility functions available

---

## Phase 5: Answer Systems (Week 5)

**Priority**: 🟢 MEDIUM - Answer checking infrastructure

### Module 13: `pg_macros.answers.answer_composition`

**Source**: `macros/answers/answerComposition.pl`

**Implements**:
- `COMPOSITION_ANS()` - Function composition answer checker
  - Checks if student answer is composition of given functions
  - Validates f(g(x)) forms

**Complexity**: MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"answerComposition.pl": "pg_macros.answers.answer_composition"
```

**Sandbox Changes**:
- Remove lines 985-987 (`COMPOSITION_ANS` stub)

---

### Module 14: `pg_macros.answers.unordered_answer`

**Source**: `macros/answers/unorderedAnswer.pl`

**Implements**:
- `UNORDERED_ANS()` - Unordered answer checker
  - Accepts answers in any order
  - Used for set-based problems

**Complexity**: MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"unorderedAnswer.pl": "pg_macros.answers.unordered_answer"
```

**Sandbox Changes**:
- Remove lines 989-991 (`UNORDERED_ANS` stub)

---

### Module 15: Complete `pg_macros.answers.answer_hints`

**Source**: `macros/answers/answerHints.pl`

**Implements**:
- `AnswerHints()` - Custom answer hints wrapper
  - Provides custom feedback for common errors
  - Wraps answer evaluators with hint logic

**Complexity**: MEDIUM (150-250 LOC)

**Registry Mapping**:
```python
"answerHints.pl": "pg_macros.answers.answer_hints"
```

**Sandbox Changes**:
- Remove lines 785-789, 2205-2211 (`AnswerHints` stubs in multiple places)
- Import: `from pg_macros.answers.answer_hints import AnswerHints`

---

### Module 16: `pg_macros.parsers.parser_checkbox_list`

**Source**: `macros/parsers/parserCheckboxList.pl`

**Implements**:
- `CheckboxList()` - Checkbox interface for multiple choice
  - Renders checkbox list
  - Handles multiple correct answers
  - Scoring logic

**Complexity**: EASY-MEDIUM (100-150 LOC)

**Registry Mapping**:
```python
"parserCheckboxList.pl": "pg_macros.parsers.parser_checkbox_list"
```

**Sandbox Changes**:
- Remove lines 1081-1083 (`CheckboxList` stub)

---

**Phase 5 Deliverables**:
- ✅ 4 answer system modules implemented
- ✅ 5 stubs removed from sandbox
- ✅ Registry updated with 4 new mappings
- ✅ Tests pass: ≥149/157
- ✅ Answer checking enhanced

---

## Phase 6: Advanced 3D Graphics (Week 6)

**Priority**: 🔵 MEDIUM-LOW - Specialized 3D features

### Module 17: `pg_macros.graph.vector_field_3d`

**Source**: `macros/graph/VectorField3D.pl`

**Implements**:
- `VectorField3D` class
  - 3D vector field visualization
  - Arrow plots in 3D space
  - Configurable density and styling

**Complexity**: HARD (300-500 LOC)

**Registry Mapping**:
```python
"VectorField3D.pl": "pg_macros.graph.vector_field_3d"
```

**Sandbox Changes**:
- Remove lines 1157-1161 (`VectorField3D` stub)

---

### Module 18: `pg_macros.graph.live_graphics_3d`

**Source**: `macros/graph/LiveGraphics3D.pl`

**Implements**:
- `Graph3D` class
  - Interactive 3D graphics
  - Surface plots, parametric surfaces
  - Java/JavaScript integration

**Complexity**: HARD (400-600 LOC)

**Registry Mapping**:
```python
"LiveGraphics3D.pl": "pg_macros.graph.live_graphics_3d"
```

**Sandbox Changes**:
- Remove lines 967-974 (`Graph3D` stub)

---

**Phase 6 Deliverables**:
- ✅ 2 3D graphics modules implemented
- ✅ 2 stubs removed from sandbox
- ✅ Registry updated with 2 new mappings
- ✅ Tests pass: ≥149/157
- ✅ 3D visualization available

---

## Phase 7: Interactive Features (Week 7-8)

**Priority**: 🔵 MEDIUM - Complex interactive widgets

### Module 19: Complete `pg_macros.math.draggable_proof`

**Source**: `macros/math/draggableProof.pl`

**Current Status**: Basic stub exists

**Enhance with**:
- Full Perl parity for DraggableProof
- JavaScript integration for drag-drop
- Statement bucket management
- Proof validation logic
- Custom scoring

**Complexity**: HARD (400-600 LOC)

**Sandbox Changes**:
- Remove lines 1067-1075 (`DraggableProof` stub)
- Use complete module implementation

---

### Module 20: `pg_macros.math.draggable_subsets`

**Source**: `macros/math/draggableSubsets.pl`

**Implements**:
- `DraggableSubsets` class
  - Drag-drop subset selection
  - Venn diagram interactions
  - Subset validation

**Complexity**: HARD (300-500 LOC)

**Registry Mapping**:
```python
"draggableSubsets.pl": "pg_macros.math.draggable_subsets"
```

**Sandbox Changes**:
- Remove lines 1077-1079 (`DraggableSubsets` stub)

---

### Module 21: Complete `pg_macros.graph.parser_graphtool`

**Source**: `macros/graph/parserGraphTool.pl`

**Current Status**: Basic stub exists

**Enhance with**:
- Full interactive GraphTool implementation
- Canvas drawing API
- Object type detection (points, lines, circles, parabolas)
- Custom answer checking
- JavaScript integration

**Complexity**: VERY HARD (800-1200 LOC)

**Sandbox Changes**:
- Remove lines 1043-1064 (`GraphTool` stub)
- Use complete module implementation

---

**Phase 7 Deliverables**:
- ✅ 3 interactive modules completed
- ✅ 3 stubs removed from sandbox
- ✅ Registry updated
- ✅ Tests pass: ≥149/157
- ✅ Interactive features fully functional

---

## Phase 8: Context & Grading Systems (Week 8-9)

**Priority**: ⚪ LOW - Advanced customization

### Module 22: `pg_macros.contexts.limited_powers`

**Source**: `macros/contexts/contextLimitedPowers.pl`

**Implements**:
- `LimitedPowers` context modifier
  - Restricts polynomial degrees
  - Enforces simplified form
  - Custom context rules

**Complexity**: MEDIUM (100-150 LOC)

**Registry Mapping**:
```python
"contextLimitedPowers.pl": "pg_macros.contexts.limited_powers"
```

**Sandbox Changes**:
- Remove lines 2108-2122 (`LimitedPowers` stub)

---

### Module 23: `pg_macros.parsers.parser_assignment`

**Source**: `macros/parsers/parserAssignment.pl`

**Implements**:
- `parser.Assignment` class
  - Parses assignment expressions (x = 5)
  - Validates left/right sides
  - Used in equation problems

**Complexity**: MEDIUM (150-200 LOC)

**Registry Mapping**:
```python
"parserAssignment.pl": "pg_macros.parsers.parser_assignment"
```

**Sandbox Changes**:
- Remove lines 2214-2226 (`parser.Assignment` stub)

---

### Module 24: `pg_macros.parsers.parser_function`

**Source**: `macros/parsers/parserFunction.pl`

**Implements**:
- `parserFunction()` - Define custom functions in Context
  - Adds new functions to parser
  - Custom function evaluation
  - Used for specialized problems

**Complexity**: MEDIUM (100-150 LOC)

**Registry Mapping**:
```python
"parserFunction.pl": "pg_macros.parsers.parser_function"
```

**Sandbox Changes**:
- Remove lines 1407-1409, 2253-2258 (`parserFunction` stubs)

---

### Module 25: `pg_macros.core.pg_graders`

**Source**: `macros/core/PGgraders.pl`

**Implements**:
- `install_problem_grader()` - Install custom grading function
- `custom_problem_grader_fluid()` - Fluid grading (partial credit)
- Custom grading logic

**Complexity**: MEDIUM (250-450 LOC)

**Registry Mapping**:
```python
"PGgraders.pl": "pg_macros.core.pg_graders"
```

**Sandbox Changes**:
- Remove lines 775-783 (`install_problem_grader`, `custom_problem_grader_fluid`)

---

**Phase 8 Deliverables**:
- ✅ 4 context/grading modules implemented
- ✅ 6 stubs removed from sandbox
- ✅ Registry updated with 4 new mappings
- ✅ Tests pass: ≥149/157
- ✅ Advanced customization available

---

## Phase 9: Core Utilities (Week 9)

**Priority**: ⚪ LOW - Simple helpers

### Module 26: `pg_macros.core.pgml_utils`

**Source**: `macros/core/PGML.pl`

**Implements**:
- `tag()` - HTML tag generator
  - Creates HTML tags with content
  - Handles attributes
- `helpLink()` - Help link generator
  - Creates help documentation links
  - Tooltip integration

**Complexity**: EASY (50-80 LOC)

**Registry Mapping**:
```python
"PGML.pl": "pg_macros.core.pgml"  # Extend existing
```

**Sandbox Changes**:
- Remove lines 1085-1091 (`tag` stub)
- Remove lines 2228-2231 (`helpLink` stub)

---

### Module 27: `pg_macros.math.statistics`

**Source**: `macros/math/PGstatisticsmacros.pl`

**Implements**:
- `linear_regression()` - Linear regression calculations
  - Returns slope, intercept, correlation
  - Statistical computations

**Complexity**: EASY-MEDIUM (50-100 LOC)

**Note**: Some statistics functions already implemented in `pg_macros/statistics.py`

**Registry Mapping**:
```python
"PGstatisticsmacros.pl": "pg_macros.math.statistics"
```

**Sandbox Changes**:
- Remove lines 321-324 (`linear_regression` stub in fallback)

---

**Phase 9 Deliverables**:
- ✅ 2 utility modules implemented
- ✅ 3 stubs removed from sandbox
- ✅ Registry updated
- ✅ Tests pass: ≥149/157
- ✅ All utilities available

---

## Phase 10: Fallback Cleanup & MathObjects (Week 10)

**Priority**: 🧹 CLEANUP - Remove all remaining stubs

### Module 28: `pg_macros.core.mathobjects_fallback`

**Source**: Various Context/MathObjects Perl files

**Purpose**: Port all MathObjects fallback stubs (lines 296-870)

**Implements**:
- `random_subset()` - Random subset selection
- `new_match_list()` - Matching list creation
- `pop_up_list_print_q()` - Pop-up list printer
- `linear_regression()` - Statistics (if not in Phase 9)
- `splice()`, `push()` - Array utilities (may use Python built-ins)
- `Scaffold`, `Section` - If not covered in Phase 3
- Context stubs: `_StubContext`, `_StubFlags`, etc.
- Answer checker stubs: `_AnswerCheckerStub`
- Formula/MathObject stubs: `_FormulaStub`, `_MathObjectStub`

**Complexity**: MEDIUM-HARD (500-800 LOC)

**Approach**:
- Port what's needed from actual Perl MathObjects
- Use Python equivalents where appropriate (splice→slicing, push→append)
- Remove stubs that are no longer needed

**Sandbox Changes**:
- Remove entire `_load_mathobjects()` fallback branch (lines 296-870)
- Keep only real MathObjects imports

---

### Final Sandbox Cleanup

**Goal**: `in_process_sandbox.py` contains ZERO stub definitions

**Actions**:
1. ✅ Remove ALL remaining stub function definitions
2. ✅ Remove ALL fallback branches (`if not _MACROS_AVAILABLE`)
3. ✅ Keep ONLY module imports at top
4. ✅ Keep ONLY namespace registration
5. ✅ Ensure clear errors if macro not loaded

**Before** (current state):
```python
if not _MACROS_AVAILABLE:
    def GraphTool(*args, **kwargs):
        # Stub implementation...
        pass
```

**After** (target state):
```python
# Imports at top
from pg_macros.graph.parser_graphtool import GraphTool

# In namespace registration
self.namespace.update({
    'GraphTool': GraphTool,
})
```

**Validation**:
```bash
# Verify zero stubs remain
grep -c "def.*stub" packages/pg_translator/pg_translator/in_process_sandbox.py
# Expected: 0

# Verify zero fallback branches
grep -c "if not _MACROS_AVAILABLE" packages/pg_translator/pg_translator/in_process_sandbox.py
# Expected: 0

# Run full test suite
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py --tb=no -q
# Expected: ≥149 passed
```

---

**Phase 10 Deliverables**:
- ✅ All remaining stubs migrated or removed
- ✅ Sandbox contains zero stub definitions
- ✅ All fallback logic removed
- ✅ Tests pass: ≥149/157
- ✅ Clean, maintainable codebase

---

## Implementation Workflow (Per Module)

### Step-by-Step Process

```
┌─────────────────────────────────────────────┐
│ 1. CREATE MODULE FILE                       │
├─────────────────────────────────────────────┤
│ • Read Perl source (.pl file)              │
│ • Identify key functions/classes           │
│ • Port logic to Python                     │
│ • Add docstrings with Perl reference       │
│ • Define __all__ exports                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 2. ADD UNIT TESTS                           │
├─────────────────────────────────────────────┤
│ • Test basic functionality                  │
│ • Test edge cases                           │
│ • Test error handling                       │
│ • Compare with Perl behavior                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 3. UPDATE REGISTRY                          │
├─────────────────────────────────────────────┤
│ • Add mapping to registry.py module_map     │
│ • Verify import path correct                │
│ • Test registry.load() works                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 4. UPDATE SANDBOX                           │
├─────────────────────────────────────────────┤
│ • Import module at top of file              │
│ • Remove inline stub definition             │
│ • Remove fallback branch if present         │
│ • Update namespace registration             │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 5. INTEGRATION TEST                         │
├─────────────────────────────────────────────┤
│ • Run affected sample problems              │
│ • Run full test suite                       │
│ • Verify ≥149/157 passing                   │
│ • Check no regressions                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ 6. COMMIT                                   │
├─────────────────────────────────────────────┤
│ • Write descriptive commit message          │
│ • Document what was migrated                │
│ • Note test results                         │
│ • Reference Perl source                     │
└─────────────────────────────────────────────┘
```

### Example: Migrating `init_graph`

```bash
# 1. Create module
touch packages/pg_macros/pg_macros/graph/pg_graph.py

# 2. Write unit tests
touch packages/pg_macros/tests/test_pg_graph.py

# 3. Port Perl logic
# Read macros/graph/PGgraphmacros.pl
# Implement init_graph() in Python

# 4. Update registry
# Edit packages/pg_macros/pg_macros/registry.py

# 5. Update sandbox
# Edit packages/pg_translator/pg_translator/in_process_sandbox.py
# - Add import at top
# - Remove stub (lines 1163-1172)
# - Keep namespace registration

# 6. Test
pytest packages/pg_macros/tests/test_pg_graph.py
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k GraphTool
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py --tb=no -q

# 7. Commit
git add packages/pg_macros/pg_macros/graph/pg_graph.py \
        packages/pg_macros/tests/test_pg_graph.py \
        packages/pg_macros/pg_macros/registry.py \
        packages/pg_translator/pg_translator/in_process_sandbox.py
git commit -m "Migrate init_graph to pg_macros.graph.pg_graph

Port init_graph() from PGgraphmacros.pl with 1:1 Perl parity.
Remove inline stub from sandbox (lines 1163-1172).

Tests: 149/157 passing (94.9%)
"
```

---

## Testing Strategy

### Per-Module Testing

**Unit Tests**:
```python
# packages/pg_macros/tests/test_<module>.py
def test_basic_functionality():
    """Test core function works"""
    pass

def test_edge_cases():
    """Test boundary conditions"""
    pass

def test_perl_parity():
    """Compare with Perl behavior"""
    pass
```

**Integration Tests**:
```bash
# Test specific problems using the macro
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k "GraphTool"

# Test full suite for regressions
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py --tb=no -q
```

### Continuous Validation

**After Each Module**:
```bash
# Run affected tests
pytest packages/pg_macros/tests/test_<module>.py -v

# Run problem-specific tests
pytest packages/pg_translator/tests/ -k "<problem_type>" -v

# Full regression test
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py --tb=no -q

# Verify pass rate maintained
# Expected: ≥149/157 (≥94.9%)
```

**After Each Phase**:
```bash
# Full test suite with coverage
pytest packages/pg_translator/tests/ --cov=pg_macros --cov=pg_translator

# Verify all phase modules working
pytest packages/pg_macros/tests/ -v

# Check for leftover stubs in sandbox
grep -n "def.*stub\|Stub for" packages/pg_translator/pg_translator/in_process_sandbox.py
```

### Success Criteria

**Per Module**:
- ✅ Unit tests pass (≥90% coverage)
- ✅ Integration tests pass
- ✅ No regression in test suite (maintain ≥149/157)
- ✅ Stub removed from sandbox
- ✅ Module documented with Perl reference

**Per Phase**:
- ✅ All modules implemented
- ✅ All stubs removed
- ✅ Registry updated
- ✅ Tests pass: ≥149/157
- ✅ Phase deliverables met

**Final (Phase 10)**:
- ✅ All 73 stubs migrated
- ✅ Zero stubs in sandbox
- ✅ Tests pass: ≥149/157
- ✅ All macros documented
- ✅ Clean, maintainable codebase

---

## Estimated Timeline

### Detailed Breakdown

| Phase | Duration | Modules | LOC | Complexity | Tests | Cumulative Weeks |
|-------|----------|---------|-----|------------|-------|------------------|
| Phase 1: Critical Graphing | 1-2 weeks | 3 | 1100-1800 | HARD | 149+ | 1-2 |
| Phase 2: Essential Parsers | 1 week | 5 | 750-1200 | MEDIUM | 149+ | 2-3 |
| Phase 3: Structure & UI | 1 week | 2 | 600-900 | MEDIUM-HARD | 149+ | 3-4 |
| Phase 4: Math Utilities | 0.5 weeks | 2 | 350-550 | EASY-MEDIUM | 149+ | 4-4.5 |
| Phase 5: Answer Systems | 1 week | 4 | 550-850 | MEDIUM | 149+ | 5-5.5 |
| Phase 6: 3D Graphics | 1 week | 2 | 700-1100 | HARD | 149+ | 6-6.5 |
| Phase 7: Interactive | 1-2 weeks | 3 | 1500-2300 | HARD-VERY HARD | 149+ | 7-8.5 |
| Phase 8: Context/Grading | 1 week | 4 | 600-950 | MEDIUM | 149+ | 8-9.5 |
| Phase 9: Core Utils | 0.5 weeks | 2 | 100-180 | EASY | 149+ | 9-10 |
| Phase 10: Cleanup | 1 week | 1 + cleanup | 500-800 | MEDIUM | 149+ | 10-11 |
| **TOTAL** | **9-11 weeks** | **28** | **6750-10630** | **Mixed** | **≥149** | **10-11** |

### Resource Allocation

**Developer Hours per Week**: 40 hours

**Total Effort**:
- **Minimum**: 9 weeks × 40 hours = 360 hours
- **Maximum**: 11 weeks × 40 hours = 440 hours
- **Average**: 10 weeks × 40 hours = 400 hours

**Breakdown by Activity**:
- **Coding**: 50% (200 hours)
- **Testing**: 25% (100 hours)
- **Documentation**: 10% (40 hours)
- **Integration/Debugging**: 15% (60 hours)

### Milestones

| Week | Milestone | Deliverable |
|------|-----------|------------|
| 2 | Phase 1 Complete | Graphing infrastructure working |
| 3 | Phase 2 Complete | Parser modules functional |
| 4 | Phase 3 Complete | Scaffold and tables working |
| 4.5 | Phase 4 Complete | Math utilities available |
| 5.5 | Phase 5 Complete | Answer systems enhanced |
| 6.5 | Phase 6 Complete | 3D graphics working |
| 8.5 | Phase 7 Complete | Interactive features done |
| 9.5 | Phase 8 Complete | Custom grading available |
| 10 | Phase 9 Complete | All utilities migrated |
| 11 | Phase 10 Complete | **ZERO STUBS IN SANDBOX** |

---

## Risk Mitigation

### Potential Risks

**Risk 1: Complex Perl Logic Hard to Port**
- **Mitigation**: Start with simpler modules in each phase
- **Contingency**: Create simplified version maintaining API, enhance later

**Risk 2: Test Pass Rate Drops Below 95%**
- **Mitigation**: Test after each module, rollback if regression
- **Contingency**: Keep stub temporarily, revisit after other modules

**Risk 3: JavaScript Integration Challenges**
- **Mitigation**: Focus on server-side logic first, stub client-side
- **Contingency**: Coordinate with frontend team for widget work

**Risk 4: Undocumented Perl Behavior**
- **Mitigation**: Test with actual problems, compare outputs
- **Contingency**: Consult Perl source, WeBWorK community

**Risk 5: Timeline Slippage**
- **Mitigation**: Focus on critical phases first (1-3)
- **Contingency**: Defer low-priority phases (8-10) if needed

### Rollback Plan

If a module migration causes test failures:

```bash
# 1. Revert sandbox changes
git checkout packages/pg_translator/pg_translator/in_process_sandbox.py

# 2. Keep module for future work
# Leave in packages/pg_macros/ but don't import

# 3. Document issue
echo "Module X needs additional work - see ISSUES.md" >> TODO.md

# 4. Move to next module
# Continue with other modules in phase
```

---

## Next Steps

### Immediate Actions (Week 1)

**Priority 1: Start Phase 1 - Critical Graphing**

1. **Create `pg_macros/graph/pg_graph.py`**
   ```bash
   touch packages/pg_macros/pg_macros/graph/pg_graph.py
   touch packages/pg_macros/tests/test_pg_graph.py
   ```

2. **Read Perl Source**
   ```bash
   cat macros/graph/PGgraphmacros.pl | less
   # Focus on init_graph, add_functions, Plot
   ```

3. **Port init_graph() Logic**
   - Implement WWPlot class
   - Port bounding box, axes, grid logic
   - Add function plotting capability

4. **Write Tests**
   ```python
   # packages/pg_macros/tests/test_pg_graph.py
   def test_init_graph_basic():
       graph = init_graph(-5, 5, -5, 5)
       assert graph is not None
   ```

5. **Update Registry**
   ```python
   # packages/pg_macros/pg_macros/registry.py
   "PGgraphmacros.pl": "pg_macros.graph.pg_graph",
   ```

6. **Remove Sandbox Stub**
   ```python
   # packages/pg_translator/pg_translator/in_process_sandbox.py
   # DELETE lines 1163-1172
   # ADD import at top:
   from pg_macros.graph.pg_graph import init_graph, add_functions, Plot
   ```

7. **Test**
   ```bash
   pytest packages/pg_macros/tests/test_pg_graph.py -v
   pytest packages/pg_translator/tests/test_tutorial_sample_problems.py -k GraphTool --tb=short
   ```

### Decision Points

**After Phase 1 (Week 2)**:
- Continue with Phase 2 parsers?
- OR pivot to easier utilities (Phase 4) to build momentum?

**After Phase 5 (Week 5.5)**:
- Continue with 3D graphics (Phase 6)?
- OR skip to interactive (Phase 7) if higher priority?

**After Phase 7 (Week 8.5)**:
- Complete remaining phases sequentially?
- OR focus cleanup (Phase 10) and defer advanced features?

---

## Success Metrics

### Quantitative Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Stubs in Sandbox | 73 | 0 | 🔴 Not Started |
| Test Pass Rate | 149/157 (94.9%) | ≥149/157 (≥94.9%) | ✅ Maintained |
| Modules Implemented | 14 | 42+ | 🟡 33% |
| Registry Mappings | 10 | 38+ | 🟡 26% |
| LOC in Modules | ~2000 | ~10000+ | 🟡 20% |
| Test Coverage | Unknown | ≥85% | ⚪ TBD |

### Qualitative Metrics

- ✅ **Code Quality**: All modules follow Python best practices
- ✅ **Documentation**: Every function has docstring with Perl reference
- ✅ **Maintainability**: No inline stubs, clear module structure
- ✅ **Perl Parity**: Behavior matches Perl implementation
- ✅ **Test Coverage**: Unit + integration tests for all modules

---

## Appendix: Quick Reference

### Module Categories

| Category | Modules | Priority | Weeks |
|----------|---------|----------|-------|
| Graph | 9 | HIGH | 3-4 |
| Parsers | 10 | HIGH | 2-3 |
| Math | 9 | MEDIUM | 1.5 |
| Core | 9 | MEDIUM | 2-3 |
| Answers | 3 | MEDIUM | 1 |
| UI | 2 | LOW | 1 |
| Contexts | 1 | LOW | 0.5 |
| MathObjects | 19 | LOW | 1 |

### File Locations

**Perl Sources**: `macros/`
**Python Modules**: `packages/pg_macros/pg_macros/`
**Tests**: `packages/pg_macros/tests/`
**Registry**: `packages/pg_macros/pg_macros/registry.py`
**Sandbox**: `packages/pg_translator/pg_translator/in_process_sandbox.py`

### Key Commands

```bash
# Run specific test
pytest packages/pg_macros/tests/test_<module>.py -v

# Run affected problems
pytest packages/pg_translator/tests/ -k "<problem>" -v

# Full regression test
pytest packages/pg_translator/tests/test_tutorial_sample_problems.py --tb=no -q

# Check for remaining stubs
grep -n "def.*stub" packages/pg_translator/pg_translator/in_process_sandbox.py

# Install updated pg_macros
pip install -e packages/pg_macros
```

---

## Conclusion

This plan provides a complete roadmap for migrating all 73 stubs from `in_process_sandbox.py` to proper Python macro modules with 1:1 Perl parity. By following the phased approach over 9-11 weeks, we will:

1. ✅ Eliminate ALL inline stubs from sandbox
2. ✅ Create 28+ properly documented modules
3. ✅ Maintain ≥95% test pass rate throughout
4. ✅ Achieve full Perl parity for problem macros
5. ✅ Build a clean, maintainable codebase

The key to success is **incremental progress with continuous validation** - migrate one module at a time, test thoroughly, and only remove stubs after confirming functionality. With focused effort and adherence to the workflow, the PG translator will have a robust, modular macro system matching the Perl reference implementation.

---

**Document Status**: Complete Migration Plan
**Version**: 1.0
**Date**: 2025-01-10
**Next Review**: After Phase 1 completion
