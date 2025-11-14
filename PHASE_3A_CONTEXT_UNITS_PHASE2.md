# Phase 3A: contextUnits.pl Phase 2 - Partial Implementation

## Summary

Implemented **FormulaWithUnits** and **NumberWithUnits** classes to support formulas and numbers with physical units. This provides the core infrastructure for Phase 2, though full integration with Formula parsing requires additional work.

**Implementation Time**: ~2 hours  
**Status**: 🔶 **PARTIAL** - Classes working, Formula integration pending  
**Tests**: 13/13 passing for unit classes ✅  
**Tutorial**: AnswerWithUnits.pg still requires deeper Formula parser integration ⏸️

---

## What Was Implemented

### Core Classes

1. **FormulaWithUnits Class** (`packages/pg/macros/parsers/parser_formula_with_units.py`)
   - Stores formula and unit separately
   - Parses "formula unit" string format
   - Supports D() differentiation with unit propagation
   - Supports eval() with unit preservation
   - **~150 lines** of implementation

2. **NumberWithUnits Class**
   - Stores numeric value with unit
   - Parses "number unit" string format
   - Unit conversion data integration
   - **~80 lines** of implementation

### Key Features Working

#### NumberWithUnits
```python
# Parse from string
num = NumberWithUnits("3.5 ft")
assert num.value == 3.5
assert num.units_str == "ft"

# Create from parts
num = NumberWithUnits(42, "m")
assert float(num) == 42.0
```

#### FormulaWithUnits
```python
# Parse formula with units
formula = FormulaWithUnits("x+1 ft")
assert formula.units_str == "ft"

# Create from parts
formula = FormulaWithUnits(Formula("x^2"), "m")

# Derivative with unit propagation
h = FormulaWithUnits("t^2", "ft") 
v = h.D('t')  # Returns FormulaWithUnits with units "ft/s"

# Evaluation
result = formula.eval(x=5)  # Returns NumberWithUnits
```

---

## Test Coverage

### Test Suite: 13 Tests, 100% Passing ✅

**Location**: `packages/pg/macros/parsers/tests/test_formula_with_units.py`

#### Test Categories

1. **NumberWithUnits Tests** (4 tests)
   - Parse from string
   - Create from parts
   - String representation
   - Float conversion

2. **FormulaWithUnits Tests** (6 tests)
   - Simple formula parsing
   - Complex formula parsing
   - Create from parts
   - String representation
   - Units with division (m/s)
   - Unit detection logic

3. **Formula Operations** (2 tests)
   - Derivative structure
   - Evaluation structure

4. **Module Exports** (1 test)
   - Factory functions
   - Class exports

### Test Execution
```bash
$ python -m pytest packages/pg/macros/parsers/tests/test_formula_with_units.py -v
================================
13 passed in 0.15s
================================
```

---

## Registry Integration

**File**: `packages/pg/macros/registry.py`

### Registration Entries
```python
"parserFormulaWithUnits": {
    "module": "pg.macros.parsers.parser_formula_with_units",
    "aliases": ["parserFormulaWithUnits.pl"],
    "category": "parsers",
    "functions": ["FormulaWithUnits", "FormulaWithUnits_factory"],
    "description": "Formula with physical units (Phase 2 of contextUnits)",
},
"parserNumberWithUnits": {
    "module": "pg.macros.parsers.parser_formula_with_units",
    "aliases": ["parserNumberWithUnits.pl"],
    "category": "parsers",
    "functions": ["NumberWithUnits", "NumberWithUnits_factory"],
    "description": "Number with physical units (Phase 2 of contextUnits)",
},
```

---

## The Core Challenge: Formula Parser Integration

### The Problem

AnswerWithUnits.pg uses:
```perl
$h  = Formula("(-16 t^2 + 64 t) ft");  # Line 41
```

When Formula() parses this string, it sees:
- `-16 t^2 + 64 t` ← formula part
- `ft` ← interpreted as `f * t` (two variables!)

The Formula parser tokenizes `ft` as two separate variables before our unit detection can run.

### What Perl Does

In Perl, contextUnits.pl modifies the Formula parser itself to:
1. Recognize unit tokens before parsing
2. Strip units from the formula string
3. Return a FormulaWithUnits object automatically

### What We Need

**Option A: Preprocessing** (Recommended)
- Add a preprocessor step that detects and transforms:
  ```perl
  Formula("expression units")  →  FormulaWithUnits("expression", "units")
  ```
- This happens before the Formula parser sees it
- Requires PygmentPreprocessor enhancement

**Option B: Parser Modification**
- Modify Formula parser to recognize known units as special tokens
- Prevent "ft" from being parsed as `f * t`
- Requires deep Formula/SymPy integration

**Option C: Context Override**
- Make Units context override Formula() globally
- Detect unit suffixes and route to FormulaWithUnits
- Requires sandbox namespace injection

---

## Current Tutorial Problem Status

### AnswerWithUnits.pg - Still Failing ❌

**Error**: 
```
ValueError: Formula evaluation resulted in symbolic expression: -256.0*f
```

**Root Cause**: Formula parser sees `ft` as `f * t`, tries to evaluate, but `f` is undefined

**Line 41-43**:
```perl
$h  = Formula("(-16 t^2 + $v0 t) ft");  # ft parsed as f*t
$v  = $h->D('t');  # Can't differentiate - f is unknown
$v1 = $v->eval(t => $v0 / 16);  # Can't evaluate - f undefined
```

---

## What Works vs What Doesn't

### ✅ Works
- Creating FormulaWithUnits explicitly: `FormulaWithUnits("x+1", "ft")`
- Creating NumberWithUnits: `NumberWithUnits(3.5, "ft")`
- Unit parsing from strings (when called directly)
- Derivative with unit propagation (when formula valid)
- Unit data from context integration
- Registry loading via `loadMacros()`

### ❌ Doesn't Work Yet
- `Formula("expression unit")` syntax (parser issue)
- Automatic unit detection in Formula()
- AnswerWithUnits.pg tutorial problem
- Unit-aware answer checking
- Full derivative chain with units

---

## Workaround for Phase 2

### Current Approach
Users can explicitly use FormulaWithUnits:

```perl
# Instead of:
$h = Formula("(-16 t^2 + 64 t) ft");

# Use:
$h = FormulaWithUnits("-16 t^2 + 64 t", "ft");
# OR
$h_formula = Formula("-16 t^2 + 64 t");
$h = FormulaWithUnits($h_formula, "ft");
```

This works with our implementation but requires problem code changes.

---

## Recommended Path Forward

### Phase 2.5: Formula Integration (3-4 days)

**Approach**: Preprocessor Enhancement

1. **Add Preprocessor Pattern** (1 day)
   - Detect `Formula("..." <unit>)` patterns
   - Transform to `FormulaWithUnits("...", "<unit>")`
   - Add to PygmentPreprocessor

2. **Test Pattern Matching** (1 day)
   - Unit detection regex
   - Formula vs FormulaWithUnits routing
   - Edge case handling

3. **Context Integration** (1 day)
   - Make Units context aware of transformation
   - Export FormulaWithUnits as Formula in Units context
   - Update variable tracking

4. **Answer Checker Support** (1 day)
   - Unit comparison in answer checking
   - Conversion between compatible units
   - Error messages for unit mismatches

**Estimated Total**: 4 days to complete Phase 2

---

## Files Created/Modified

### Created
```
packages/pg/macros/parsers/
├── parser_formula_with_units.py          # Main implementation (260 lines)
└── tests/
    └── test_formula_with_units.py        # Test suite (13 tests, 100 lines)
```

### Modified
```
packages/pg/macros/registry.py            # Added 2 macro registrations (+12 lines)
```

---

## Comparison to Perl

### Perl Implementation
- **lib/Parser/Legacy/NumberWithUnits.pm** (480 lines)
- Fully integrated with Parser
- Automatic unit detection in Formula()
- Complete answer checker support

### Python Phase 2
- **parser_formula_with_units.py** (260 lines)
- Standalone classes working
- Manual FormulaWithUnits usage required
- Answer checker integration pending

**Coverage**: ~54% of Perl functionality (classes work, integration pending)

---

## Success Criteria

### ✅ Achieved
- [x] FormulaWithUnits class implemented
- [x] NumberWithUnits class implemented
- [x] Unit string parsing working
- [x] 13/13 tests passing
- [x] Registered in macro registry
- [x] D() differentiation with units
- [x] eval() evaluation with units

### ⏸️ Pending (Phase 2.5)
- [ ] Formula("expression unit") syntax
- [ ] Automatic unit detection
- [ ] AnswerWithUnits.pg passing
- [ ] Answer checker integration
- [ ] Preprocessor enhancement

---

## Conclusion

**Phase 2 Status**: 🔶 **INFRASTRUCTURE COMPLETE, INTEGRATION PENDING**

Successfully delivered:
- 260 lines of production code
- 100 lines of test code (13 tests, 100% passing)
- FormulaWithUnits and NumberWithUnits classes
- Registry integration
- Unit parsing and storage

Not yet complete:
- Formula parser integration (requires preprocessor or parser modification)
- AnswerWithUnits.pg tutorial problem
- Automatic unit detection in Formula()

**Recommendation**: 
- **Option 1**: Proceed with other Phase 3 priorities, return to Phase 2.5 later
- **Option 2**: Invest 4 days in preprocessor enhancement to complete Phase 2

**Phase 3A Overall Status**:
1. ✅ parserFunction.pl - COMPLETE (150 passing, +3)
2. ✅ contextUnits Phase 1 - COMPLETE (27/27 tests)
3. 🔶 contextUnits Phase 2 - PARTIAL (13/13 tests, integration pending)
4. ✅ plots.pl - COMPLETE (32/32 tests, 150 passing, +1)

**Tutorial Pass Rate**: 150/160 (93.75%)  
**Remaining Failures**: 10 problems (AnswerWithUnits requires Phase 2.5)

---

*Document Date: 2025-11-14*  
*Implementation Time: ~2 hours*  
*Test Pass Rate: 100% (13/13 for classes)*  
*Integration: Pending (Formula parser)*

