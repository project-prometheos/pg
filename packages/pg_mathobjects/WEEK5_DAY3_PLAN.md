# Week 5 Day 3: PolynomialFactors Context - Implementation Plan

**Goal**: Implement context that allows only factored polynomials
**Estimated Time**: 3-4 hours
**Date**: October 5, 2025

## Overview

The PolynomialFactors context extends LimitedPolynomial to ensure polynomials are entered in factored form, like `(x-1)(x+2)` or `4(2x+1)(x+3)`, rather than expanded form.

## Key Requirements

### 1. Factored Form Structure

**Accept**:
- Simple factors: `(x-1)(x+2)`
- Constant multiples: `4(2x+1)(x+3)`
- Powers of factors: `(x-1)^2`
- Negation: `-(x-1)(x+2)`
- Division by constants: `(x-1)(x+2)/3`

**Reject**:
- Expanded form: `x^2 + x - 2` (must factor)
- Addition/subtraction at top level: `(x-1) + (x+2)`
- Functions: `sin(x)`, `ln(x)`, etc. (inherited from LimitedPolynomial)

### 2. Context Flags

From Perl implementation:

- **singlePowers**: Only one monomial of each degree in each factor (default: False)
- **singleFactors**: Factors cannot be repeated (default: False)
  - `(x+1)^2*(x+1)` → Error
  - Note: Only catches exact matches, not `(x+1)*(1+x)`
- **strictDivision**: Division only on single factor, not product (default: False)
- **strictPowers**: Powers only on single factor, not product (default: True)

### 3. Modes

- **PolynomialFactors**: Standard mode, allows operations in coefficients
- **PolynomialFactors-Strict**: No operations in coefficients, sets all strict flags

## Implementation Strategy

### Phase 1: Core Structure (1 hour)

1. **Create `polynomial_factors.py`**
   - Inherit validation from LimitedPolynomial
   - Add factored form detection
   - Implement factor tracking

2. **Factor Detection Logic**
   - Identify multiplication at top level
   - Recognize factor boundaries (parentheses)
   - Track factor strings for uniqueness checking

3. **Context Integration**
   - Add `_init_polynomial_factors()` to Context
   - Handle PolynomialFactors and PolynomialFactors-Strict
   - Set appropriate flags

### Phase 2: Validation Rules (1 hour)

1. **Structure Validation**
   - Top level must be multiplication/division/power
   - Each factor must be polynomial
   - No addition/subtraction at top level

2. **Flag Enforcement**
   - singleFactors: Track factor strings, reject duplicates
   - strictDivision: Division only if not multi-factor product
   - strictPowers: Powers only on single factor

3. **Error Messages**
   - "Polynomial must be in factored form"
   - "Each factor can appear only once"
   - "You can only raise a single term or factor to a power"

### Phase 3: Test Suite (1 hour)

**Test Categories** (20+ tests):

1. **Accept Valid Factored** (6 tests)
   - Simple product: `(x-1)(x+2)`
   - Constant multiple: `3(x+1)(x-2)`
   - Powers: `(x-1)^2`
   - Negation: `-(x+1)(x-2)`
   - Division: `(x-1)(x+2)/2`
   - Complex: `4(2x+1)(x+3)^2`

2. **Reject Expanded** (4 tests)
   - Expanded quadratic: `x^2 + x - 2`
   - Simple polynomial: `x^2 + 1`
   - Addition at top: `(x-1) + (x+2)`
   - Single monomial: `x^2` (not factored)

3. **Flag Tests: singleFactors** (3 tests)
   - Reject repeated: `(x+1)^2*(x+1)`
   - Accept powers: `(x+1)^2`
   - Accept different: `(x+1)*(x-1)`

4. **Flag Tests: strictPowers** (2 tests)
   - Reject product power: `(x*(x+1))^2`
   - Accept factor power: `(x+1)^2`

5. **Flag Tests: strictDivision** (2 tests)
   - Standard allows: `(x*(x+1))/3`
   - Strict rejects: `(x*(x+1))/3`

6. **Strict Mode** (3 tests)
   - Reject operations in coefficients
   - Accept simple coefficients
   - All strict flags set

7. **Context Switching** (2 tests)
   - Switch to PolynomialFactors
   - Switch to PolynomialFactors-Strict

### Phase 4: Debugging & Polish (30-60 min)

1. Run tests, fix issues
2. Improve error messages
3. Handle edge cases
4. Verify integration

## Technical Approach

### Sympy-Based Detection

Unlike Perl's operator-level approach, we'll validate the parsed expression:

```python
def is_factored_form(expr, vars):
    """Check if expression is in factored form"""
    # Top level should be Mul, Pow, or Div
    if isinstance(expr, sp.Add):
        return False, "Polynomial must be in factored form (use parentheses)"

    # Extract factors from multiplication
    if isinstance(expr, sp.Mul):
        factors = expr.as_ordered_factors()
        # Each factor should be polynomial
        # Track for uniqueness checking

    # Powers and division OK if operand is polynomial
    return True, None
```

### Factor Tracking

```python
def extract_factors(expr):
    """Get list of factor strings for uniqueness checking"""
    factors = []

    if isinstance(expr, sp.Mul):
        for factor in expr.as_ordered_factors():
            # Skip constants
            if not factor.is_number:
                # Use canonical string form
                factors.append(str(factor))

    return factors
```

### Limitations (Document)

1. **Exact Match Only**: `(x+1)` and `(1+x)` not detected as same factor
2. **Irreducibility**: No check if factors are fully factored (e.g., `(x^2-1)*(x+1)`)
3. **Constant Factoring**: No check if constants factored out (e.g., `3*(x+1)*(3x+3)`)
4. **Sympy Simplification**: May auto-simplify before validation

## Success Criteria

- ✅ 20+ tests passing (100%)
- ✅ Accept factored polynomials
- ✅ Reject expanded polynomials
- ✅ Flags work correctly
- ✅ Strict mode functional
- ✅ Context switching works
- ✅ No regressions in existing tests
- ✅ Integration with Week 5 Days 1-2

## Files to Create/Modify

**Create**:
- `packages/pg_mathobjects/pg_mathobjects/polynomial_factors.py` (~300 lines)
- `packages/pg_mathobjects/tests/test_polynomial_factors.py` (~250 lines)

**Modify**:
- `packages/pg_mathobjects/pg_mathobjects/context.py` (add _init_polynomial_factors)
- `packages/pg_mathobjects/pg_mathobjects/formula.py` (add _validate_factors hook)

## Next Steps After Completion

Week 5 Day 4: Context Flag System (tolerance, limits, etc.)

---

**Ready to implement!** 🚀
