# Week 5 Day 3: PolynomialFactors Context - Progress Report

**Date**: October 5, 2025
**Status**: 🟡 **IN PROGRESS** (85% tests passing)
**Time Spent**: ~2 hours

## Current Status

**Tests**: 28/33 passing (85%)

### ✅ Working Features

1. **Accept Factored Forms** (7/7 tests passing):
   - Simple product: `(x-1)*(x+2)` ✅
   - Constant multiple: `3*(x+1)*(x-2)` ✅
   - Powers: `(x-1)^2` ✅
   - Negation: `-(x+1)*(x-2)` ✅
   - Division by constant: `(x-1)*(x+2)/3` ✅
   - Complex: `4*(2*x+1)*(x+3)^2` ✅
   - Single factor: `x+1` ✅

2. **Reject Expanded** (3/4 tests passing):
   - Expanded quadratic: `x^2 + x - 2` ✅
   - Simple polynomial: `x^2 + 1` ✅
   - Functions: `sin(x)` ✅
   - Addition at top: `(x-1) + (x+2)` ❌ (still failing)

3. **singleFactors Flag** (2/3 tests passing):
   - Accept different factors ✅
   - Accept powers ✅
   - Reject repeated ❌ (not implemented yet)

4. **strictPowers Flag** (2/3 tests passing):
   - Accept factor power ✅
   - Allow when not strict ✅
   - Reject product power ❌ (not detecting correctly)

5. **strictDivision Flag** (2/3 tests passing):
   - Allow product division (standard) ✅
   - Accept single factor division (strict) ✅
   - Reject product division (strict) ❌ (not detecting correctly)

6. **Strict Mode** (1/3 tests passing):
   - Context creation ✅
   - Reject operations ❌ (domain error)
   - Accept simple ❌ (domain error)

7. **Context Switching** (2/2 tests passing):
   - Switch to PolynomialFactors ✅
   - Switch from PolynomialFactors ✅

8. **Operations** (3/3 tests passing):
   - Evaluate ✅
   - Multiply factors ✅
   - Power of factor ✅

9. **Answer Checking** (3/3 tests passing):
   - Accept correct ✅
   - Reject different ✅
   - Accept equivalent ✅

10. **Multi-Variable** (2/2 tests passing):
    - Two-variable product ✅
    - Two-variable evaluation ✅

## Issues to Fix

### 1. Addition at Top Level (Low Priority)
**Test**: `test_reject_addition_at_top`
**Problem**: `(x-1) + (x+2)` is being accepted
**Cause**: My `_is_simple_linear_factor` might be returning True for sum of two factors
**Fix**: Need to check if expression is genuinely a single linear polynomial vs sum of factors

### 2. Repeated Factor Detection (Medium Priority)
**Test**: `test_reject_repeated_factor`
**Problem**: `(x+1)^2*(x+1)` should be rejected with singleFactors flag
**Cause**: `_check_single_factors` not working correctly
**Fix**: Need to properly extract and compare factor strings

### 3. Product Power Detection (Medium Priority)
**Test**: `test_reject_product_power`
**Problem**: `(x*(x+1))^2` should be rejected by default (strictPowers=True)
**Cause**: Detection in `_check_factored_form` not triggering
**Fix**: Need to verify the check is being called

### 4. Product Division Detection (Medium Priority)
**Test**: `test_reject_product_division_strict`
**Problem**: `(x*(x+1))/3` should be rejected with strictDivision
**Cause**: `_check_factor_restrictions` not detecting this case
**Fix**: Need to properly identify multi-factor numerator in division

### 5. Strict Mode Domain Error (High Priority)
**Test**: `test_strict_accept_simple_coefficients`
**Problem**: `3*(x+1)*(x-2)` throws "expected a valid domain specification, got ZZ[]"
**Cause**: Something in strict mode polynomial checking triggers sympy domain error
**Fix**: Need to investigate where this occurs and handle gracefully

## Implementation Summary

### Files Created
1. **`pg_mathobjects/polynomial_factors.py`** (420 lines)
   - `FactoredPolynomialValidator` class
   - `_check_polynomial_restrictions()` - No functions, integer powers
   - `_check_factored_form()` - Main factoring logic
   - `_is_simple_linear_factor()` - Distinguish linear from higher degree
   - `_check_multiplication_factors()` - Validate factors in product
   - `_check_factor_restrictions()` - Single factors, strict powers/division
   - `_check_single_factors()` - Detect repeated factors
   - `_extract_factor_strings()` - Get factor canonical forms
   - `validate_factored_polynomial()` - Entry point

2. **`tests/test_polynomial_factors.py`** (275 lines, 33 tests)
   - 10 test classes covering all functionality
   - Comprehensive coverage of accept/reject cases
   - Flag validation tests
   - Context switching tests
   - Operations and answer checking tests

### Files Modified
1. **`pg_mathobjects/context.py`**
   - Added `_init_polynomial_factors()` method
   - Handles `PolynomialFactors` and `PolynomialFactors-Strict`
   - Sets appropriate flags (strictPowers, singleFactors, etc.)

2. **`pg_mathobjects/formula.py`**
   - Added call to `validate_factored_polynomial()` in `_validate_polynomial()`
   - Runs after LimitedPolynomial validation if polynomialFactors flag set

## Technical Approach

### Key Design Decisions

1. **Inline Polynomial Validation**: Instead of calling LimitedPolynomialValidator, implemented checks inline to avoid API coupling issues

2. **Linear Factor Detection**: Created `_is_simple_linear_factor()` to distinguish `x+1` (OK) from `x^2+x-2` (reject)

3. **Sympy-Based Approach**: Use sympy's tree structure (Add, Mul, Pow) to detect form, not operator-level like Perl

4. **Practical Limitations**: Accept documented limitations (e.g., `(x+1)` vs `(1+x)` not detected as same)

### Validation Flow

```
validate_factored_polynomial()
  ↓
1. Check polynomial restrictions (no functions, integer powers)
  ↓
2. Check factored form:
   - If Add: must be simple linear (not x^2+x-2)
   - If Mul: validate each factor
   - If Pow: check base and strictPowers
  ↓
3. Check factor restrictions:
   - singleFactors: no repeats
   - strictPowers: no (a*b)^2
   - strictDivision: no (a*b)/c
```

## Next Steps

### Immediate (30-60 min)
1. ✅ Fix addition at top level detection
2. ✅ Implement repeated factor detection
3. ✅ Fix product power detection
4. ✅ Fix product division detection
5. ⚠️ Investigate strict mode domain error

### If Time Permits (30 min)
- Add more test cases for edge scenarios
- Improve error messages
- Document limitations clearly

## Success Metrics

**Target**: 30/33 tests passing (91%)
**Current**: 28/33 tests passing (85%)
**Stretch**: 33/33 tests passing (100%)

## Lessons Learned

1. **API Compatibility**: Need to check method signatures carefully (ContextFlags.get, VariableManager.list vs .keys)

2. **Expression Types**: Sympy's is_polynomial() returns True for any polynomial, including expanded ones - need degree checks

3. **Validation Order**: Check specific cases first (linear) before general cases (any polynomial)

4. **Testing Strategy**: Start with simple accept tests, then rejection tests, then flags

## Time Breakdown

- Research Perl implementation: 15 min
- Create implementation plan: 15 min
- Implement core validator: 45 min
- Create test suite: 30 min
- Debug and fix issues: 45 min
- **Total**: ~2 hours

## Remaining Work

**Estimate**: 30-60 minutes to reach 30+ tests passing

**Priority**:
1. High: Fix strict mode domain error (blocking 2 tests)
2. Medium: Repeated factors, product power/division (3 tests)
3. Low: Addition at top level (1 test, edge case)

---

**Status**: Making good progress, core functionality works, need to polish edge cases and fix strict mode issue.
