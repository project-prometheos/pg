# Phase 3A: contextUnits.pl Phase 1 Implementation

## Summary

Implemented Phase 1 of contextUnits.pl - the infrastructure for Units context with basic unit definitions. This provides the foundation for unit-aware problems, though full Formula-with-units support requires additional work (Phase 2).

## What Was Implemented (Phase 1)

### Core Infrastructure
1. **UnitsContext Class** (`packages/pg/macros/contexts/context_units.py`)
   - Extends base Context with units support
   - 280+ lines of implementation code

2. **Unit Definitions**
   - Length units: m, cm, mm, km, ft, in, mi, yd (+ aliases)
   - Time units: s, ms, min, hr, day (+ aliases)
   - Conversion values to fundamental units

3. **Context Methods**
   - `withUnitsFor('length', 'time')` - Enable unit categories
   - `assignUnits(t='s', x='ft')` - Assign units to variables
   - `addUnits('m', 'ft')` - Add specific units
   - `removeUnits('ft', 'in')` - Remove units
   - `isUnit('ft')` - Check if name is a unit

4. **Registry Integration**
   - Registered in `packages/pg/macros/registry.py`
   - Loadable via `loadMacros('contextUnits.pl')`
   - Auto-patches Context() to recognize 'Units'

### Test Coverage
- **27 comprehensive tests**, all passing
- Tests cover:
  - Context creation
  - Unit category management
  - Variable unit assignments
  - Unit constants and conversions
  - Method chaining
  - Integration with Context system

## Files Created

```
packages/pg/macros/contexts/
├── __init__.py                           # Package initialization
├── context_units.py                      # UnitsContext implementation (280 lines)
└── tests/
    ├── __init__.py
    └── test_context_units.py             # 27 tests (300+ lines)

packages/pg/macros/registry.py            # Updated: +7 lines
```

## Test Results

```bash
============================= 27 passed in 0.56s =========================
```

All Phase 1 tests pass successfully.

## Tutorial Problem Status

### AnswerWithUnits.pg - Still Failing

**Error**: `ValueError: Formula evaluation resulted in symbolic expression: -256.0*f`

**Root Cause**: Formula parsing doesn't understand unit suffixes

**Problem Line**:
```perl
$h  = Formula("(-16 t^2 + $v0 t) ft");  # Line 41
```

The Formula parser treats `ft` as `f * t` (multiplication) instead of as a single unit token.

### Why This Happens

The current Formula implementation:
1. Tokenizes `ft` as two separate variables: `f` and `t`
2. Interprets it as multiplication by implicit operator
3. Tries to evaluate but `f` is undefined (only `t` has a value)
4. Results in symbolic expression `-256.0*f`

### What's Needed for Phase 2

To fully support Formula-with-units:

1. **Formula Parser Changes**
   - Recognize unit tokens (ft, m, s, etc.) as single entities
   - Parse unit suffixes on formulas: `"expression unit"`
   - Distinguish units from variables in parsing context

2. **FormulaWithUnits Class**
   - Separate class like Perl's `FormulaWithUnits`
   - Stores formula and unit separately
   - Handles unit-aware operations (D, eval, etc.)

3. **NumberWithUnits Class**
   - For numeric values with units
   - Unit arithmetic and conversion

## What Works in Phase 1

```python
from pg.macros.contexts import Context

# Create Units context
ctx = Context('Units')

# Enable unit categories
ctx.withUnitsFor('length', 'time')

# Assign units to variables
ctx.assignUnits(t='s', x='ft')

# Units are available as constants
assert ctx.constants.get('ft') == 0.3048  # feet in meters
assert ctx.isUnit('ft') == True

# Check variable unit assignments
assert ctx.getVariableUnit('t') == 's'
```

## What Doesn't Work Yet (Phase 2 Needed)

```python
# ❌ Formula with unit suffix - not yet supported
h = Formula("(-16 t^2 + 64 t) ft", context=ctx)  # Parses ft as f*t

# ❌ Unit-aware derivatives
v = h.D('t')  # Would need FormulaWithUnits

# ❌ Unit arithmetic
distance = Formula("5 ft") + Formula("2 in")  # Not yet supported
```

## Phase 2 Implementation Plan

### Priority: HIGH (Required for AnswerWithUnits.pg)

1. **Extend Formula Parser** (3-4 days)
   - Add unit token recognition to lexer
   - Parse " unit" suffix patterns
   - Integrate with UnitsContext

2. **Create FormulaWithUnits Class** (2-3 days)
   - Separate formula and unit storage
   - Unit-aware eval(), D(), etc.
   - Unit conversion support

3. **Create NumberWithUnits Class** (1-2 days)
   - Numeric value + unit
   - Basic unit arithmetic

4. **Update parserNumberWithUnits.pl Macro** (1 day)
   - Wrapper for NumberWithUnits
   - Answer checker integration

5. **Update parserFormulaWithUnits.pl Macro** (1 day)
   - Wrapper for FormulaWithUnits
   - Answer checker integration

**Estimated Phase 2 Time**: 8-11 days total

## Alternative Approach (Quicker Partial Fix)

For a minimal fix to just make AnswerWithUnits.pg work:

1. **Pattern-Based Unit Parsing** (1 day)
   - Detect " unit" at end of formula string
   - Strip unit, parse formula separately
   - Attach unit metadata

2. **Stub FormulaWithUnits** (1 day)
   - Basic wrapper around Formula
   - Store unit separately
   - Minimal D() and eval() support

**Estimated Minimal Fix Time**: 2 days

## Comparison to Perl Implementation

### Perl contextUnits.pl
- **2263 lines** total
- Full unit categories (angles, mass, temperature, etc.)
- Complete unit arithmetic
- Formula-with-units integration
- Answer checker support

### Python Phase 1
- **280 lines** of implementation
- 2 unit categories (length, time)
- Context infrastructure only
- No formula integration yet

**Phase 1 Progress**: ~12% of full Perl functionality (infrastructure layer)

## Recommendation

Given the user's directive to proceed with plots.pl next, I recommend:

### Option A: Document and Move On
- Mark contextUnits Phase 1 as "Infrastructure Complete"
- Document that AnswerWithUnits.pg requires Phase 2
- Proceed to plots.pl as directed
- Return to contextUnits Phase 2 after Phase 3 priorities

### Option B: Minimal Fix First
- Spend 2 days on pattern-based unit parsing
- Get AnswerWithUnits.pg working with basic approach
- Then proceed to plots.pl
- Full Phase 2 can wait

## Decision

Following user's directive: **Proceed with plots.pl** (Phase 3A Priority 3) next, as instructed.

contextUnits Phase 1 provides solid infrastructure that can be extended later. The Pattern fails gracefully with clear error messages.

## Files Summary

```
Created:
  packages/pg/macros/contexts/__init__.py
  packages/pg/macros/contexts/context_units.py
  packages/pg/macros/contexts/tests/__init__.py
  packages/pg/macros/contexts/tests/test_context_units.py

Modified:
  packages/pg/macros/registry.py

Status:
  ✅ Phase 1 Complete: Context infrastructure (27/27 tests pass)
  ⏸️  Phase 2 Pending: Formula-with-units support
  📋 AnswerWithUnits.pg: Requires Phase 2
```

## Conclusion

**Phase 3A contextUnits Phase 1**: INFRASTRUCTURE COMPLETE ✅

Successfully implemented:
- UnitsContext class with full API
- Unit definitions for length and time
- Context integration and method chaining
- 27 tests, 100% passing
- Loadable via loadMacros()

Limitations:
- Formula-with-units parsing not yet implemented
- AnswerWithUnits.pg still fails (requires Phase 2)

Ready to proceed with **Phase 3A Priority 3: plots.pl** as directed.

