# Week 5 Day 2: LimitedPolynomial - Progress Report

**Status**: 🟡 IN PROGRESS (46% complete)  
**Tests**: 12/26 passing

## What's Working ✅

### Tests Passing (12 tests)

**Accept Valid Polynomials** (6/6):
- ✅ Simple polynomial: `x^2 + 2*x + 1`
- ✅ Multiple variables: `x^2 + y^2 + 2*x*y`
- ✅ Constant term: `5`
- ✅ Higher degree: `x^5 - 3*x^4 + ...`
- ✅ Division by constant: `x^2/2 + x/3`
- ✅ Negative coefficients: `-x^2 + 3*x - 5`

**Reject Invalid** (2/9):
- ✅ Negative power: `x^(-1)` 
- ✅ Division by variable: `1/x`

**Context Switching** (2/2):
- ✅ Switch to LimitedPolynomial
- ✅ Switch back to Numeric

**Strict Mode** (2/3):
- ✅ Accept simple coefficient: `5*x + 3`
- ✅ Accept fraction: `x/2 + 1/3`

## Issues to Fix (14 tests failing)

### Issue 1: Error Message Patterns (7 tests)

**Problem**: Validation errors say "not a polynomial" but tests expect specific messages like "function 'sin' not allowed"

**Tests**:
- test_reject_sin, test_reject_cos, test_reject_ln
- test_reject_exp, test_reject_sqrt
- test_reject_fractional_power
- test_reject_absolute_value

**Fix**: Improve validation to check functions BEFORE polynomial check, give specific errors

### Issue 2: Strict Mode Not Working (1 test)

**Problem**: `(2+3)*x` is accepted but should be rejected in strict mode

**Test**: test_strict_reject_addition_in_coefficient

**Fix**: Improve _check_strict_coefficients to detect operations properly

### Issue 3: Answer Checker Not Callable (3 tests)

**Problem**: Tests do `checker('x^2 + 2*x + 1')` but checker is FormulaAnswerChecker object

**Fix**: Either make it callable or use `checker.check()` method

### Issue 4: Float Conversion (3 tests)

**Problem**: `float(result)` fails because result is Real object

**Fix**: Use `result.value` or `float(result.value)`

## Files Created

1. ✅ `pg_mathobjects/limited_polynomial.py` (250 lines)
2. ✅ `tests/test_limited_polynomial.py` (215 lines)
3. ✅ Updated `pg_mathobjects/context.py` (added LimitedPolynomial init)
4. ✅ Updated `pg_mathobjects/formula.py` (added validation hook)

## Next Steps to Complete Day 2

### Step 1: Fix Error Messages (30 min)

Reorder validation checks:
1. Check functions first (give specific error)
2. Check powers (specific error)
3. Then check is_polynomial (general fallback)

### Step 2: Fix Strict Mode (20 min)

Improve coefficient operation detection:
- Parse coefficient subtree
- Check for Add/Mul nodes with multiple args

### Step 3: Fix Test Issues (20 min)

- Update answer checker tests to use correct API
- Fix float() calls to use .value attribute

### Step 4: Run Full Suite (10 min)

Get to 20+ tests passing (77%)

## Time Tracking

- Planning: 30 min ✅
- Core implementation: 90 min ✅
- Testing setup: 30 min ✅
- First test run: 15 min ✅
- **Remaining**: ~1.5 hours to completion

**Total so far**: ~2.5 hours  
**Target**: 3.5-4 hours  
**On track**: ✅

## Architecture Notes

### Validation Flow

```
Formula.__init__
  → _parse_expression()
    → parse with sympy
    → _validate_polynomial()
      → validate_polynomial_formula()
        → PolynomialValidator.validate()
          → _check_functions() [NEW: do this first!]
          → _check_powers()
          → _is_polynomial_tree()
          → _check_strict_coefficients()
```

### Key Insight

Sympy's `is_polynomial()` catches everything (including sin(x)), but gives generic error.
Need to check specific restrictions BEFORE the general polynomial check.

## Ready to Continue

Next action: Fix validation order to give better error messages.
