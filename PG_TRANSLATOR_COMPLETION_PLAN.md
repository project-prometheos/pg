# pg_translator Completion Plan

**Date**: October 5, 2025
**Goal**: Run traditional Perl .pg files with BEGIN_TEXT/END_TEXT syntax
**Estimate**: 6-9 hours
**Status**: IN PROGRESS

---

## Phase 1: Complete Preprocessor (2-3 hours) ✅ STARTING

### Task 1.1: Enhance Perl→Python Syntax Translation (1 hour)
**File**: `packages/pg_translator/pg_translator/preprocessor.py`

**Add**:
- ✅ Array syntax: `@array` → `array`
- ✅ Hash access: `$hash{key}` → `hash['key']`
- ✅ Comments: Already handled
- ✅ Semicolons: Already handled
- ✅ Function calls: `ans_rule(20)` → keep as-is

**Test**: Transform Perl lines to Python

### Task 1.2: Implement loadMacros() Function (1 hour)
**File**: `packages/pg_translator/pg_translator/preprocessor.py`

**Add**:
- Parse `loadMacros("PGstandard.pl", "MathObjects.pl")`
- Generate Python imports based on macro names
- Map .pl files to Python modules

**Mapping**:
```
PG.pl           → from pg_macros.core.pg_core import *
PGstandard.pl   → (included in PG.pl)
PGbasicmacros.pl → from pg_macros.core.pg_basic_macros import *
MathObjects.pl  → from pg_math import Context, Real, Complex, Formula
PGML.pl         → from pg_pgml import PGML
```

### Task 1.3: Test Preprocessor (30 min)
**Create**: `test_preprocessor_complete.py`

**Test Cases**:
- Variable substitution
- loadMacros() conversion
- BEGIN_TEXT with interpolation
- ans_rule() inside TEXT

---

## Phase 2: Integration with pg_macros (2-3 hours)

### Task 2.1: Create loadMacros() Runtime Function (1 hour)
**File**: `packages/pg_translator/pg_translator/runtime.py` (NEW)

**Implement**:
```python
def loadMacros(*macro_files: str) -> None:
    """Runtime loadMacros - no-op since imports handled by preprocessor."""
    pass

def beginproblem() -> str:
    """Start problem - returns empty string."""
    return ""
```

### Task 2.2: Connect Executor to pg_macros (1 hour)
**File**: `packages/pg_translator/pg_translator/executor.py`

**Add**:
- Import pg_macros functions into sandbox globals
- Set up PGEnvironment before execution
- Extract results after execution

### Task 2.3: Test Integration (1 hour)
**Create**: `test_pg_translator_integration.py`

**Test**: Simple .pg file → HTML output

---

## Phase 3: Validation & Testing (2-3 hours)

### Task 3.1: Test with Real .pg Files (1.5 hours)
**Test Files**:
1. Simple arithmetic (test_simple.pg)
2. Multiple answers
3. With hints/solutions
4. Radio buttons
5. Checkboxes

### Task 3.2: Fix Issues (1 hour)
- Debug any preprocessor issues
- Fix executor integration
- Handle edge cases

### Task 3.3: Documentation (30 min)
**Create**: `PG_TRANSLATOR_USAGE.md`

**Document**:
- How to use pg_translator
- Supported .pg features
- Known limitations
- Examples

---

## Success Criteria

✅ **Phase 1 Complete When**:
- Preprocessor converts loadMacros() correctly
- Variable substitution works
- TEXT blocks transform properly

✅ **Phase 2 Complete When**:
- Simple .pg file executes
- HTML output generated
- Answer evaluators registered

✅ **Phase 3 Complete When**:
- 5 test .pg files work
- Documentation complete
- Known issues documented

---

## Timeline

**Hour 1-2**: Phase 1 - Preprocessor enhancements
**Hour 3-4**: Phase 2 - Integration with pg_macros
**Hour 5-6**: Phase 3 - Testing & validation
**Hour 7-9**: Buffer for debugging and documentation

---

## Starting Now: Phase 1, Task 1.1
