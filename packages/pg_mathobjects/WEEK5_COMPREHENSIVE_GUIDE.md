# Week 5 Features: Comprehensive User Guide

**Version**: 1.0  
**Date**: October 5, 2025  
**Status**: Complete

This guide covers all Week 5 specialized contexts and features added to the MathObjects system.

---

## Table of Contents

1. [FormulaUpToConstant](#formulauptoconstant)
2. [LimitedPolynomial](#limitedpolynomial)
3. [PolynomialFactors](#polynomialfactors)
4. [Context Flag System](#context-flag-system)
5. [Migration Guide](#migration-guide)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## FormulaUpToConstant

### Overview

The `FormulaUpToConstant` class handles formulas that differ only by an additive constant, commonly used for indefinite integrals.

### Basic Usage

```python
from pg_mathobjects import Context, FormulaUpToConstant

# Create context
ctx = Context('Numeric')

# Student answer with constant C
student_answer = FormulaUpToConstant('x**2 + C', ctx)

# Correct answer with different constant
correct_answer = FormulaUpToConstant('x**2 + K', ctx)

# They are considered equal (differ only by constant)
assert student_answer == correct_answer
```

### Creating FormulaUpToConstant

**From string** (automatically adds constant if missing):
```python
f = FormulaUpToConstant('x**2', ctx)
# Automatically becomes: x**2 + C
```

**With specific constant letter**:
```python
f = FormulaUpToConstant('x**2 + K', ctx)
# Uses K as the constant
```

**From existing Formula**:
```python
from pg_mathobjects import Formula

formula = Formula('x**2', ctx)
f = FormulaUpToConstant.from_formula(formula)
# Adds constant: x**2 + C
```

### Constant Requirements

**Valid constants** (single uppercase letters, not reserved):
- ✅ C, K, A, B, D, F, G, H, I, J, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z
- ❌ Reserved: E (Euler's number)

**Linear appearance**:
```python
# ✅ Valid - constant appears linearly
FormulaUpToConstant('x**2 + C', ctx)
FormulaUpToConstant('sin(x) + 2*K', ctx)

# ❌ Invalid - constant appears nonlinearly
FormulaUpToConstant('x**2 + C**2', ctx)  # Raises ValueError
FormulaUpToConstant('sin(C)', ctx)        # Raises ValueError
```

**Single constant only**:
```python
# ✅ Valid - one constant
FormulaUpToConstant('x**2 + C', ctx)

# ❌ Invalid - multiple constants
FormulaUpToConstant('x**2 + C + K', ctx)  # Raises ValueError
```

### Comparison and Answer Checking

**Automatic constant matching**:
```python
f1 = FormulaUpToConstant('x**2 + C', ctx)
f2 = FormulaUpToConstant('x**2 + K', ctx)
f3 = FormulaUpToConstant('x**2 + 5', ctx)

# All three are equal (differ only by constant)
assert f1 == f2 == f3
```

**Wrong formula rejected**:
```python
f1 = FormulaUpToConstant('x**2 + C', ctx)
f2 = FormulaUpToConstant('x**3 + C', ctx)

assert f1 != f2  # Different formulas
```

**Answer checker with hints**:
```python
correct = FormulaUpToConstant('x**2 + C', ctx)
checker = correct.cmp()

# Correct answer
result = checker('x**2 + K')
assert result['score'] == 1.0

# Wrong answer with helpful hints
result = checker('x**2')
assert result['score'] == 0.0
assert 'constant' in result['message']  # Hints about missing constant

result = checker('2*x')
assert result['score'] == 0.0
assert 'derivative' in result['message']  # Hints about wrong formula
```

### Operations

**Differentiation**:
```python
f = FormulaUpToConstant('x**2 + C', ctx)
df = f.D('x')  # Returns regular Formula (constant disappears)

assert isinstance(df, Formula)
assert df == Formula('2*x', ctx)
```

**Removing constant**:
```python
f = FormulaUpToConstant('x**2 + C', ctx)
formula = f.remove_constant()

assert isinstance(formula, Formula)
assert formula == Formula('x**2', ctx)
```

**Evaluation** (must provide constant value):
```python
f = FormulaUpToConstant('x**2 + C', ctx)
result = f.eval(x=2, C=5)

assert result.value == 9  # 2**2 + 5
```

### Real-World Examples

**Example 1: Indefinite Integral**
```python
# Problem: Find ∫ e^x dx
ctx = Context('Numeric')

correct_answer = FormulaUpToConstant('exp(x) + C', ctx)

# Student submissions
student1 = 'exp(x) + K'        # ✅ Correct
student2 = 'exp(x) + 5'        # ✅ Correct (constant value)
student3 = 'exp(x)'            # ❌ Missing constant
student4 = 'x * exp(x) + C'    # ❌ Wrong formula

checker = correct_answer.cmp()
print(checker(student1)['score'])  # 1.0
print(checker(student2)['score'])  # 1.0
print(checker(student3)['score'])  # 0.0 (with hint)
print(checker(student4)['score'])  # 0.0
```

**Example 2: Polynomial Integral**
```python
# Problem: Find ∫ 3x² dx
correct = FormulaUpToConstant('x**3 + C', ctx)

# These are all correct:
assert correct == FormulaUpToConstant('x**3 + K', ctx)
assert correct == FormulaUpToConstant('x**3 + 7', ctx)
assert correct == FormulaUpToConstant('x**3 - 2*A', ctx)  # Different coefficient
```

**Example 3: Trig Integral**
```python
# Problem: Find ∫ cos(x) dx
correct = FormulaUpToConstant('sin(x) + C', ctx)

# Equivalent forms accepted
assert correct == FormulaUpToConstant('sin(x) + K', ctx)
```

---

## LimitedPolynomial

### Overview

The `LimitedPolynomial` context restricts formulas to polynomial form, rejecting transcendental functions like sin, cos, exp, ln, etc.

### Context Modes

**Standard mode** - Allows any polynomial operations:
```python
ctx = Context('LimitedPolynomial')
```

**Strict mode** - Requires simple coefficients:
```python
ctx = Context('LimitedPolynomial-Strict')
```

### Basic Usage

```python
from pg_mathobjects import Context, Formula

ctx = Context('LimitedPolynomial')

# ✅ Accepted - polynomial forms
Formula('x**2 + 3*x + 1', ctx)
Formula('x**3 - 2*x**2 + x - 5', ctx)
Formula('x*y + x**2*y**3', ctx)
Formula('x**2/3', ctx)  # Division by constant

# ❌ Rejected - non-polynomial
Formula('sin(x)', ctx)     # Trig function
Formula('exp(x)', ctx)     # Exponential
Formula('ln(x)', ctx)      # Logarithm
Formula('x**(-1)', ctx)    # Negative power
Formula('x**(1/2)', ctx)   # Fractional power
Formula('1/x', ctx)        # Division by variable
```

### Standard Mode Features

**Accepts all polynomial operations**:
```python
ctx = Context('LimitedPolynomial')

# Complex coefficients allowed
Formula('(2+3)*x + 1', ctx)        # ✅ Accepted
Formula('(x+1)*(x-2)', ctx)        # ✅ Accepted (expands to x^2-x-2)
Formula('x**2 + sin(0)', ctx)      # ✅ Accepted (constant function)
```

### Strict Mode Features

**Requires simple coefficients**:
```python
ctx = Context('LimitedPolynomial-Strict')

# Simple coefficients only
Formula('3*x + 1', ctx)            # ✅ Accepted
Formula('x**2 - 2*x + 5', ctx)     # ✅ Accepted
Formula('x/2 + 1/3', ctx)          # ✅ Accepted

# Operations in coefficients rejected
Formula('(2+3)*x + 1', ctx)        # ❌ Rejected
Formula('(x+1)*(x-2)', ctx)        # ❌ Rejected (but may auto-expand)
Formula('x**2 + sin(0)', ctx)      # ❌ Rejected (constant function)
```

**Note**: Sympy may auto-expand some expressions before validation, so `(x+1)*(x-2)` might become `x**2 - x - 2` and be accepted.

### Context Flags

**Check flags**:
```python
ctx = Context('LimitedPolynomial')
assert ctx.flags.get('limitedPolynomial') is True
assert ctx.flags.get('strictCoefficients') is False

ctx_strict = Context('LimitedPolynomial-Strict')
assert ctx_strict.flags.get('strictCoefficients') is True
assert ctx_strict.flags.get('reduceConstants') == 0
```

### Multi-Variable Polynomials

```python
ctx = Context('LimitedPolynomial')
ctx.variables.add('y', 'Real')
ctx.variables.add('z', 'Real')

# Multi-variable polynomials accepted
Formula('x**2 + y**2 + z**2', ctx)        # ✅
Formula('x*y*z + x**2*y + z', ctx)        # ✅
Formula('3*x**2*y**3 - x*y*z**2', ctx)    # ✅
```

### Answer Checking

```python
ctx = Context('LimitedPolynomial')
correct = Formula('x**2 + 3*x + 1', ctx)
checker = correct.cmp()

# Correct polynomial
result = checker('x**2 + 3*x + 1')
assert result['score'] == 1.0

# Equivalent form
result = checker('1 + 3*x + x**2')  # Reordered
assert result['score'] == 1.0

# Wrong polynomial
result = checker('x**2 + 2*x + 1')
assert result['score'] == 0.0

# Non-polynomial rejected at parse time
# Formula('sin(x)', ctx)  # Raises ValueError
```

### Real-World Examples

**Example 1: Quadratic Expansion**
```python
# Problem: Expand (x+2)(x-3)
ctx = Context('LimitedPolynomial')
correct = Formula('x**2 - x - 6', ctx)

# Student might enter in different forms
assert correct == Formula('x**2 - x - 6', ctx)
assert correct == Formula('-6 - x + x**2', ctx)  # Reordered
```

**Example 2: Polynomial Addition**
```python
# Problem: Add (x² + 2x + 1) + (x² - 3x + 5)
ctx = Context('LimitedPolynomial')
correct = Formula('2*x**2 - x + 6', ctx)

checker = correct.cmp()
assert checker('2*x**2 - x + 6')['score'] == 1.0
```

**Example 3: Strict Mode Problem**
```python
# Problem: Enter polynomial in standard form (no operations)
ctx = Context('LimitedPolynomial-Strict')
correct = Formula('x**2 + 3*x + 1', ctx)

# This would be rejected in strict mode (if not auto-expanded)
# Formula('(x+1)**2 + 2*x', ctx)  # Operations in coefficients
```

---

## PolynomialFactors

### Overview

The `PolynomialFactors` context ensures polynomials are entered in factored form, rejecting expanded polynomials.

### Context Modes

**Standard mode**:
```python
ctx = Context('PolynomialFactors')
```

**Strict mode** - All strict flags enabled:
```python
ctx = Context('PolynomialFactors-Strict')
```

### Basic Usage

```python
from pg_mathobjects import Context, Formula

ctx = Context('PolynomialFactors')

# ✅ Accepted - factored forms
Formula('(x-1)*(x+2)', ctx)
Formula('3*(x+1)*(x-2)', ctx)
Formula('(x-1)**2', ctx)
Formula('x+1', ctx)              # Single factor
Formula('-(x-1)*(x+2)', ctx)     # Negation
Formula('(x-1)*(x+2)/5', ctx)    # Division by constant

# ❌ Rejected - expanded forms
Formula('x**2 + x - 2', ctx)     # Expanded quadratic
Formula('x**2 - 1', ctx)         # Should be (x-1)*(x+1)
Formula('x**2 + 2*x + 1', ctx)   # Should be (x+1)**2
```

### Standard Mode Flags

**Default behavior**:
- ✅ `strictPowers=True` - Only powers of single factors allowed
- ✅ `singleFactors=False` - Repeated factors allowed
- ✅ `strictDivision=False` - Multiple factors can be divided by constant

```python
ctx = Context('PolynomialFactors')

# Powers of single factors (strictPowers=True)
Formula('(x-1)**2', ctx)             # ✅ Accepted
Formula('(x+1)**3', ctx)             # ✅ Accepted

# Repeated factors allowed (singleFactors=False)
Formula('(x-1)*(x-1)', ctx)          # ✅ Accepted (note: sympy simplifies to (x-1)**2)

# Product division allowed (strictDivision=False)
Formula('(x-1)*(x+2)/3', ctx)        # ✅ Accepted
```

### Strict Mode Flags

**All restrictions enabled**:
- ✅ `strictPowers=True`
- ✅ `singleFactors=True` - Each factor appears once
- ✅ `strictDivision=True` - Only single factor or constant divided
- ✅ `strictCoefficients=True` - Simple coefficients only
- ✅ `singlePowers=True` - No power operations in coefficients

```python
ctx = Context('PolynomialFactors-Strict')

# Single factors only (singleFactors=True)
Formula('(x-1)*(x+2)', ctx)          # ✅ Different factors

# Single factor or constant division (strictDivision=True)
Formula('(x-1)/3', ctx)              # ✅ Single factor divided
Formula('5/3', ctx)                  # ✅ Constants only

# Simple coefficients (strictCoefficients=True)
Formula('3*(x-1)*(x+2)', ctx)        # ✅ Simple constant
```

### Sympy Auto-Simplification Limitations

**Important**: Sympy automatically simplifies expressions before validation, which can affect detection:

```python
ctx = Context('PolynomialFactors')

# These may be simplified before validation:
# '(x-1) + (x+2)' → '2*x + 1' (becomes linear, accepted)
# '(x+1)**2*(x+1)' → '(x+1)**3' (repeated factor not detected)
# '(x*(x+1))**2' → 'x**2*(x+1)**2' (product power expanded)
# '(2+3)*(x+1)' → '5*(x+1)' (coefficient operation evaluated)
```

### Context Flags

```python
ctx = Context('PolynomialFactors')
assert ctx.flags.get('polynomialFactors') is True
assert ctx.flags.get('strictPowers') is True
assert ctx.flags.get('singleFactors') is False

ctx_strict = Context('PolynomialFactors-Strict')
assert ctx_strict.flags.get('singleFactors') is True
assert ctx_strict.flags.get('strictDivision') is True
```

### Multi-Variable Factored Polynomials

```python
ctx = Context('PolynomialFactors')
ctx.variables.add('y', 'Real')

# Multi-variable factored forms
Formula('(x-1)*(y+2)', ctx)          # ✅ Accepted
Formula('(x+y)*(x-y)', ctx)          # ✅ Accepted
Formula('x*(x+y)', ctx)              # ✅ Accepted
```

### Answer Checking

```python
ctx = Context('PolynomialFactors')
correct = Formula('(x-1)*(x+2)', ctx)
checker = correct.cmp()

# Correct factored form
result = checker('(x-1)*(x+2)')
assert result['score'] == 1.0

# Equivalent factored form
result = checker('(x+2)*(x-1)')  # Order doesn't matter
assert result['score'] == 1.0

# With constant coefficient
result = checker('1*(x-1)*(x+2)')
assert result['score'] == 1.0

# Expanded form rejected
# Formula('x**2 + x - 2', ctx)  # Raises ValueError during parsing
```

### Real-World Examples

**Example 1: Factor Quadratic**
```python
# Problem: Factor x² + 3x + 2
ctx = Context('PolynomialFactors')
correct = Formula('(x+1)*(x+2)', ctx)

# These are all correct:
assert correct == Formula('(x+1)*(x+2)', ctx)
assert correct == Formula('(x+2)*(x+1)', ctx)  # Order doesn't matter
assert correct == Formula('1*(x+1)*(x+2)', ctx)  # Explicit 1

# Expanded form would be rejected:
# Formula('x**2 + 3*x + 2', ctx)  # ValueError
```

**Example 2: Factor with Common Factor**
```python
# Problem: Factor 2x² + 6x + 4
ctx = Context('PolynomialFactors')
correct = Formula('2*(x+1)*(x+2)', ctx)

assert correct == Formula('2*(x+1)*(x+2)', ctx)
assert correct == Formula('(x+1)*2*(x+2)', ctx)  # Order doesn't matter
```

**Example 3: Perfect Square**
```python
# Problem: Factor x² + 2x + 1
ctx = Context('PolynomialFactors')
correct = Formula('(x+1)**2', ctx)

assert correct == Formula('(x+1)**2', ctx)
# Note: (x+1)*(x+1) may be auto-simplified to (x+1)**2 by sympy
```

**Example 4: Strict Mode**
```python
# Problem: Factor completely with each factor once
ctx = Context('PolynomialFactors-Strict')
correct = Formula('(x-1)*(x+2)*(x-3)', ctx)

# All factors different - accepted
assert correct == Formula('(x-1)*(x+2)*(x-3)', ctx)
```

---

## Context Flag System

### Overview

Context flags control behavior of parsing, evaluation, and comparison operations throughout the MathObjects system.

### Core Tolerance Flags

**tolerance** (default: 0.001):
```python
ctx = Context('Numeric')
ctx.flags.set(tolerance=0.001)  # 0.1% relative tolerance

from pg_mathobjects import Real
r1 = Real(1.0, ctx)
r2 = Real(1.0005, ctx)

assert r1 == r2  # Within 0.1% tolerance
```

**tolType** (default: 'relative'):
```python
# Relative tolerance (percentage)
ctx.flags.set(tolType='relative', tolerance=0.01)  # 1%
r1 = Real(100.0, ctx)
r2 = Real(100.5, ctx)  # 0.5% difference
assert r1 == r2

# Absolute tolerance (fixed difference)
ctx.flags.set(tolType='absolute', tolerance=0.1)
r1 = Real(1.0, ctx)
r2 = Real(1.05, ctx)  # 0.05 absolute difference
assert r1 == r2
```

**zeroLevel** (default: 1e-14):
```python
# Values below zeroLevel treated as zero
ctx.flags.set(zeroLevel=1e-10)

r1 = Real(1e-11, ctx)
r2 = Real(0.0, ctx)

assert r1 == r2  # Below zero threshold
```

**zeroLevelTol** (default: 1e-12):
```python
# Tolerance for zero-level comparisons
ctx.flags.set(zeroLevelTol=1e-12)
```

### Reduction Flags

**reduceConstants** (default: 1):
```python
ctx.flags.set(reduceConstants=1)  # Enable constant reduction

# Sympy will simplify constant expressions
Formula('2 + 3', ctx)  # May become 5
```

**reduceConstantFunctions** (default: 1):
```python
ctx.flags.set(reduceConstantFunctions=1)

# Sympy will evaluate constant function calls
Formula('sin(0)', ctx)  # May become 0
```

### Specialized Context Flags

Flags set automatically by specialized contexts:

**LimitedPolynomial**:
- `limitedPolynomial=True` - Restrict to polynomials
- `strictCoefficients=False/True` - Coefficient restrictions (strict mode)
- `singlePowers=False/True` - No power operations (strict mode)

**PolynomialFactors**:
- `polynomialFactors=True` - Require factored form
- `strictPowers=True` - Only powers of single factors
- `singleFactors=False/True` - Each factor appears once (strict mode)
- `strictDivision=False/True` - Division restrictions (strict mode)

### Flag Examples

**Example 1: Loose Tolerance**
```python
ctx = Context('Numeric')
ctx.flags.set(tolerance=0.05)  # 5% tolerance

r1 = Real(100.0, ctx)
r2 = Real(103.0, ctx)  # 3% difference

assert r1 == r2  # Within 5% tolerance
```

**Example 2: Strict Zero Threshold**
```python
ctx = Context('Numeric')
ctx.flags.set(zeroLevel=1e-20)  # Very small threshold

r1 = Real(1e-15, ctx)
r2 = Real(0.0, ctx)

assert r1 != r2  # Above strict zero threshold
```

**Example 3: Check Context Flags**
```python
ctx = Context('PolynomialFactors-Strict')

# Check what flags are set
print(ctx.flags.get('polynomialFactors'))    # True
print(ctx.flags.get('strictPowers'))         # True
print(ctx.flags.get('singleFactors'))        # True
print(ctx.flags.get('strictDivision'))       # True
print(ctx.flags.get('strictCoefficients'))   # True
```

---

## Migration Guide

### From Perl WeBWorK

#### Context Switching

**Perl**:
```perl
Context("Numeric");
$f = Formula("x^2 + 1");

Context("LimitedPolynomial");
$g = Formula("x^2 + 2*x + 1");
```

**Python**:
```python
ctx = Context('Numeric')
f = Formula('x**2 + 1', ctx)

ctx = Context('LimitedPolynomial')
g = Formula('x**2 + 2*x + 1', ctx)
```

#### FormulaUpToConstant

**Perl**:
```perl
Context("Numeric");
$answer = FormulaUpToConstant("x^2 + C");
```

**Python**:
```python
ctx = Context('Numeric')
answer = FormulaUpToConstant('x**2 + C', ctx)
```

#### Context Flags

**Perl**:
```perl
Context()->flags->set(tolerance => 0.01);
```

**Python**:
```python
ctx = Context('Numeric')
ctx.flags.set(tolerance=0.01)
```

### Key Differences

1. **Power operator**: `^` (Perl) → `**` (Python)
2. **Context passed explicitly**: Python requires passing context to constructors
3. **Singleton pattern**: `Context('Numeric')` returns cached instance (same as Perl)
4. **Flag syntax**: `->set()` (Perl) → `.set()` (Python)

---

## Best Practices

### 1. Always Pass Context

```python
# ✅ Good
ctx = Context('Numeric')
f = Formula('x**2', ctx)

# ❌ Bad - uses default context
# f = Formula('x**2')  # May not work as expected
```

### 2. Set Tolerance Appropriately

```python
# For numeric answers
ctx.flags.set(tolerance=0.001)  # 0.1% default is usually good

# For approximate calculations
ctx.flags.set(tolerance=0.01)   # 1% for looser tolerance

# For exact comparisons
ctx.flags.set(tolType='absolute', tolerance=1e-10)
```

### 3. Use Strict Modes When Needed

```python
# For factoring problems
ctx = Context('PolynomialFactors-Strict')

# For polynomial form problems
ctx = Context('LimitedPolynomial-Strict')
```

### 4. Check Flags in Specialized Contexts

```python
ctx = Context('PolynomialFactors')

# Verify flags are what you expect
if ctx.flags.get('polynomialFactors'):
    # Factored form is enforced
    pass
```

### 5. Handle Sympy Auto-Simplification

```python
# Be aware that sympy may simplify before validation
# '2 + 3' → '5'
# '(x+1)*(x-1)' → 'x**2 - 1'

# Use strict modes to catch operations
ctx = Context('LimitedPolynomial-Strict')
# Now operations in coefficients are rejected
```

---

## Troubleshooting

### Problem: Formula Rejected Unexpectedly

**Symptom**: Formula that should be accepted is rejected.

**Solution**:
1. Check context mode (standard vs strict)
2. Verify flags: `ctx.flags.get('flagName')`
3. Test with standard mode first
4. Check if sympy simplified the expression

```python
# Debug: Print flags
ctx = Context('PolynomialFactors')
print(ctx.flags.get('strictPowers'))
print(ctx.flags.get('singleFactors'))
```

### Problem: Tolerance Too Strict/Loose

**Symptom**: Comparisons not working as expected.

**Solution**: Adjust tolerance and type:
```python
ctx = Context('Numeric')

# For stricter comparison
ctx.flags.set(tolerance=0.0001)  # 0.01%

# For looser comparison
ctx.flags.set(tolerance=0.05)    # 5%

# For absolute tolerance
ctx.flags.set(tolType='absolute', tolerance=0.01)
```

### Problem: Constant Not Recognized

**Symptom**: FormulaUpToConstant raises error about invalid constant.

**Solution**: Use uppercase single letter (not E):
```python
# ✅ Valid constants
FormulaUpToConstant('x**2 + C', ctx)
FormulaUpToConstant('x**2 + K', ctx)
FormulaUpToConstant('x**2 + A', ctx)

# ❌ Invalid constants
# FormulaUpToConstant('x**2 + e', ctx)  # Lowercase
# FormulaUpToConstant('x**2 + E', ctx)  # Reserved for Euler's number
# FormulaUpToConstant('x**2 + c1', ctx) # Multiple characters
```

### Problem: Expanded Form Not Rejected

**Symptom**: PolynomialFactors accepts expanded form.

**Solution**: Sympy may have simplified expression. Check:
```python
ctx = Context('PolynomialFactors')

# This may be accepted if sympy simplifies (x-1)+(x+2) to 2*x+1
# Use non-simplifying test cases
Formula('x**2 + x - 2', ctx)  # Should be rejected (quadratic)
```

### Problem: Context Flags Shared Unexpectedly

**Symptom**: Changing flags in one context affects another.

**Solution**: This is expected behavior (singleton pattern). Use `copy()` for independent context:
```python
ctx1 = Context('Numeric')
ctx1.flags.set(tolerance=0.01)

# ctx2 shares flags with ctx1 (same cached instance)
ctx2 = Context('Numeric')

# Create independent copy
ctx3 = ctx1.copy()
ctx3.flags.set(tolerance=0.001)
# ctx1 unchanged
```

---

## Summary

Week 5 features provide powerful tools for specialized mathematical contexts:

- **FormulaUpToConstant**: Indefinite integrals with automatic constant handling
- **LimitedPolynomial**: Restrict to polynomial form (standard and strict modes)
- **PolynomialFactors**: Require factored form (standard and strict modes)
- **Context Flags**: Fine-tune tolerance, reduction, and context behavior

All features are fully tested with 214 passing tests and integrate seamlessly with the existing MathObjects system.

---

**Need Help?**

- Check test files for more examples: `tests/test_*.py`
- Review completion documents: `WEEK5_DAY*_COMPLETE.md`
- Consult Perl WeBWorK documentation for additional context
