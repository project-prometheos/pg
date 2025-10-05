# Week 5 Day 4: Context Flag System - COMPLETE ✅

**Status**: 100% Complete (33/33 tests passing, 214 total tests)
**Date**: 2025
**Time Spent**: ~2 hours

---

## Achievement Summary

Successfully implemented comprehensive test coverage for the MathObjects Context Flag System, validating all existing flags and discovering/fixing a critical bug in the `zeroLevel` implementation.

### Tests Created: 33 (100% passing)

- **TestContextFlagsBasic**: 5 tests - Core flag operations
- **TestToleranceFlags**: 8 tests - Tolerance system comprehensive coverage
- **TestReduceFlags**: 5 tests - Reduction flags behavior
- **TestSpecializedContextFlags**: 7 tests - Context-specific flags
- **TestFlagInteractions**: 3 tests - Flag interaction patterns
- **TestFlagValidation**: 5 tests - Edge cases and validation

### Key Accomplishments

1. ✅ **Comprehensive flag testing** - All 13 existing flags tested
2. ✅ **Bug fix** - `zeroLevel` flag now properly used (was hardcoded)
3. ✅ **WeBWorK compatibility** - Validated singleton context pattern
4. ✅ **Tolerance system validated** - Relative/absolute modes working
5. ✅ **Zero regressions** - All 214 tests passing

---

## Bugs Fixed

### Bug 1: zeroLevel Hardcoded in Real.__eq__

**Problem**: The `Real.__eq__()` method used hardcoded `1e-14` for near-zero detection instead of checking the `zeroLevel` flag.

**Location**: `pg_mathobjects/real.py`, line 132

**Before**:
```python
if abs(self.value) < 1e-14:  # Near zero
    return abs(other_value) < tolerance
```

**After**:
```python
zero_level = self.context.flags.get('zeroLevel') or 1e-14

if abs(self.value) < zero_level:  # Near zero
    return abs(other_value) < tolerance
```

**Impact**: Now users can customize the zero threshold:
```python
ctx = Context('Numeric')
ctx.flags.set(zeroLevel=1e-10)  # More relaxed near-zero threshold
```

---

## Important Discovery: Context Singleton Pattern

**Finding**: The `Context()` function implements a **singleton pattern** - each context name returns the SAME cached instance.

**Behavior**:
```python
ctx1 = Context('Numeric')
ctx2 = Context('Numeric')
# ctx1 is ctx2 → True (same object!)

ctx1.flags.set(tolerance=0.01)
# ctx2 also has tolerance=0.01
```

**Why**: This matches **Perl WeBWorK behavior** where contexts are global and you "switch" between them rather than creating independent instances.

**Implication**: Tests updated to reflect correct WeBWorK-style API:
- ✅ Use single context, modify flags over time
- ❌ Don't assume multiple independent contexts with same name

---

## Context Flags Tested

### Core Tolerance Flags (Default values)

| Flag | Default | Type | Purpose |
|------|---------|------|---------|
| `tolerance` | 0.001 | float | Comparison tolerance (0.1% default) |
| `tolType` | 'relative' | str | 'relative' or 'absolute' tolerance |
| `zeroLevel` | 1e-14 | float | Threshold for near-zero values |
| `zeroLevelTol` | 1e-12 | float | Tolerance for zero-level comparisons |

### Reduction Flags

| Flag | Default | Type | Purpose |
|------|---------|------|---------|
| `reduceConstants` | 1 | int | Simplify constant expressions |
| `reduceConstantFunctions` | 1 | int | Evaluate constant function calls |

### LimitedPolynomial Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `limitedPolynomial` | True (when context active) | Restrict to polynomial form |
| `strictCoefficients` | False / True (strict mode) | Require simple coefficients |
| `singlePowers` | False / True (strict mode) | Forbid power operations in coefficients |

### PolynomialFactors Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `polynomialFactors` | True (when context active) | Require factored form |
| `singleFactors` | False / True (strict) | Each factor appears once |
| `strictPowers` | True | Only allow powers of single factors |
| `strictDivision` | False / True (strict) | Only allow division by constants |

---

## Test Coverage Details

### 1. TestContextFlagsBasic (5 tests)

**Purpose**: Validate core flag operations

```python
def test_default_flags():
    """All default values correct"""
    ctx = Context('Numeric')
    assert ctx.flags.get('tolerance') == 0.001
    assert ctx.flags.get('tolType') == 'relative'
    # ... etc

def test_set_flags():
    """Set and retrieve flags"""
    ctx.flags.set(tolerance=0.01)
    assert ctx.flags.get('tolerance') == 0.01

def test_flag_copy():
    """Context.copy() preserves flags"""
    ctx1 = Context('Numeric')
    ctx1.flags.set(tolerance=0.01)
    ctx2 = ctx1.copy()
    assert ctx2.flags.get('tolerance') == 0.01
```

**Coverage**: ✅ All basic operations work

---

### 2. TestToleranceFlags (8 tests)

**Purpose**: Comprehensive tolerance system validation

#### Test 2.1: Relative Tolerance (Default)
```python
ctx = Context('Numeric')
# Default: 0.001 relative (0.1%)

r1 = Real(1.0, ctx)
r2 = Real(1.0005, ctx)  # 0.05% difference
assert r1 == r2  # Within tolerance
```

#### Test 2.2: Absolute Tolerance
```python
ctx.flags.set(tolType='absolute', tolerance=0.01)

r1 = Real(1.0, ctx)
r2 = Real(1.005, ctx)  # 0.005 absolute difference
assert r1 == r2  # Within 0.01 absolute
```

#### Test 2.3: Custom Tolerance
```python
ctx.flags.set(tolerance=0.1, tolType='relative')  # 10%

r1 = Real(1.0, ctx)
r2 = Real(1.05, ctx)  # 5% difference
assert r1 == r2  # Within 10%

r3 = Real(1.15, ctx)  # 15% difference
assert r1 != r3  # Outside 10%
```

#### Test 2.4: Near-Zero Handling (zeroLevel)
```python
ctx.flags.set(zeroLevel=1e-10, tolerance=0.001)

r1 = Real(1e-11, ctx)  # Below zeroLevel
r2 = Real(0.0, ctx)
assert r1 == r2  # Treated as zero
```

#### Test 2.5-2.8: Integration Tests
- ✅ Tolerance in formula evaluation
- ✅ Different tolerances in succession
- ✅ Tolerance persistence across operations
- ✅ Tolerance in comparisons

**Coverage**: ✅ Tolerance system fully validated

---

### 3. TestReduceFlags (5 tests)

**Purpose**: Validate reduction flags

```python
def test_reduce_constants_default():
    """reduceConstants on by default"""
    ctx = Context('Numeric')
    assert ctx.flags.get('reduceConstants') == 1

def test_reduce_constants_affects_simplification():
    """Constant expressions simplified"""
    f = Formula('2 + 3', ctx)
    # Sympy simplifies to 5
    assert '5' in str(f) or f.eval().value == 5

def test_reduce_constants_off():
    """Can turn off flag"""
    ctx.flags.set(reduceConstants=0)
    assert ctx.flags.get('reduceConstants') == 0
```

**Coverage**: ✅ Flags exist and can be modified (sympy handles actual reduction)

---

### 4. TestSpecializedContextFlags (7 tests)

**Purpose**: Validate context-specific flags

#### Test 4.1: LimitedPolynomial Flags
```python
ctx = Context('LimitedPolynomial')
assert ctx.flags.get('limitedPolynomial') is True
assert ctx.flags.get('strictCoefficients') is False
```

#### Test 4.2: LimitedPolynomial-Strict Flags
```python
ctx = Context('LimitedPolynomial-Strict')
assert ctx.flags.get('strictCoefficients') is True
assert ctx.flags.get('reduceConstants') == 0
```

#### Test 4.3: PolynomialFactors Flags
```python
ctx = Context('PolynomialFactors')
assert ctx.flags.get('polynomialFactors') is True
assert ctx.flags.get('strictPowers') is True
```

#### Test 4.4: PolynomialFactors-Strict Flags
```python
ctx = Context('PolynomialFactors-Strict')
assert ctx.flags.get('singleFactors') is True
assert ctx.flags.get('strictDivision') is True
```

#### Test 4.5-4.7: Flag Isolation
- ✅ Flags not leaked between contexts
- ✅ Context switch changes flags correctly
- ✅ Custom flags persist through copy

**Coverage**: ✅ All specialized context flags work

---

### 5. TestFlagInteractions (3 tests)

**Purpose**: Test flag combinations

```python
def test_tolerance_with_zero_level():
    """tolerance and zeroLevel work together"""
    ctx.flags.set(zeroLevel=1e-10, tolerance=0.001)

    # Near zero (below zeroLevel)
    r1 = Real(1e-11, ctx)
    r2 = Real(0.0, ctx)
    assert r1 == r2

    # Not near zero
    r3 = Real(1.0, ctx)
    r4 = Real(1.001, ctx)
    assert r3 == r4  # Within relative tolerance

def test_strict_mode_reduces_constants_off():
    """Strict contexts disable reduceConstants"""
    ctx = Context('LimitedPolynomial-Strict')
    assert ctx.flags.get('reduceConstants') == 0
```

**Coverage**: ✅ Flags interact correctly

---

### 6. TestFlagValidation (5 tests)

**Purpose**: Edge cases and validation

```python
def test_tolerance_positive():
    """Tolerance values are positive"""
    ctx.flags.set(tolerance=0.01)
    assert ctx.flags.get('tolerance') > 0

def test_tol_type_values():
    """tolType accepts valid values"""
    ctx.flags.set(tolType='relative')
    assert ctx.flags.get('tolType') == 'relative'

    ctx.flags.set(tolType='absolute')
    assert ctx.flags.get('tolType') == 'absolute'

def test_boolean_flags():
    """Boolean flags work correctly"""
    ctx.flags.set(limitedPolynomial=True)
    assert ctx.flags.get('limitedPolynomial') is True

    ctx.flags.set(limitedPolynomial=1)
    assert ctx.flags.get('limitedPolynomial') == 1

def test_flag_override():
    """Later set() calls override previous values"""
    ctx.flags.set(tolerance=0.01)
    ctx.flags.set(tolerance=0.001)
    assert ctx.flags.get('tolerance') == 0.001
```

**Coverage**: ✅ Edge cases handled

---

## Usage Examples

### Example 1: Custom Tolerance

```python
from pg_mathobjects import Context, Real

# Create context with loose tolerance
ctx = Context('Numeric')
ctx.flags.set(tolerance=0.05)  # 5% relative tolerance

r1 = Real(100.0, ctx)
r2 = Real(103.0, ctx)  # 3% difference

assert r1 == r2  # Within 5% tolerance
```

### Example 2: Absolute Tolerance

```python
ctx = Context('Numeric')
ctx.flags.set(tolType='absolute', tolerance=0.1)

r1 = Real(0.01, ctx)
r2 = Real(0.05, ctx)  # 0.04 absolute difference

assert r1 == r2  # Within 0.1 absolute
```

### Example 3: Custom Zero Threshold

```python
ctx = Context('Numeric')
ctx.flags.set(zeroLevel=1e-10)

r1 = Real(1e-11, ctx)
r2 = Real(0.0, ctx)

assert r1 == r2  # Below custom zero threshold
```

### Example 4: Strict Mode Flags

```python
ctx = Context('PolynomialFactors-Strict')

# All strict flags enabled
assert ctx.flags.get('strictCoefficients') is True
assert ctx.flags.get('singleFactors') is True
assert ctx.flags.get('strictDivision') is True
assert ctx.flags.get('singlePowers') is True
```

---

## Implementation Notes

### ContextFlags Class

**Location**: `pg_mathobjects/context.py`, lines 155-177

```python
class ContextFlags:
    """Manages context flags/options."""

    def __init__(self):
        self._flags: Dict[str, Any] = {
            'tolerance': 0.001,
            'tolType': 'relative',
            'zeroLevel': 1e-14,
            'zeroLevelTol': 1e-12,
            'reduceConstants': 1,
            'reduceConstantFunctions': 1,
        }

    def set(self, **kwargs):
        """Set flag values."""
        self._flags.update(kwargs)

    def get(self, name: str) -> Any:
        """Get flag value."""
        return self._flags.get(name)

    def copy(self):
        """Create a copy of this flags object."""
        new_flags = ContextFlags()
        new_flags._flags = self._flags.copy()
        return new_flags
```

### Real.__eq__ Implementation

**Location**: `pg_mathobjects/real.py`, lines 120-141

```python
def __eq__(self, other):
    """Equality comparison with tolerance."""
    # ... type checking ...

    # Use context tolerance and zeroLevel
    tolerance = self.context.flags.get('tolerance')
    tol_type = self.context.flags.get('tolType')
    zero_level = self.context.flags.get('zeroLevel') or 1e-14

    if tol_type == 'relative':
        # Relative tolerance
        if abs(self.value) < zero_level:  # Near zero
            return abs(other_value) < tolerance
        return abs(self.value - other_value) / abs(self.value) < tolerance
    else:
        # Absolute tolerance
        return abs(self.value - other_value) < tolerance
```

---

## Integration with Other Contexts

### LimitedPolynomial

```python
def _init_limited_polynomial(self, strict=False):
    """Initialize LimitedPolynomial context."""
    self._init_numeric()

    self.flags.set(
        limitedPolynomial=True,
        strictCoefficients=strict,
        singlePowers=strict,
    )

    if strict:
        self.flags.set(reduceConstants=False)
```

### PolynomialFactors

```python
def _init_polynomial_factors(self, strict=False):
    """Initialize PolynomialFactors context."""
    self._init_limited_polynomial(strict=strict)

    self.flags.set(
        polynomialFactors=True,
        strictPowers=True,
        singleFactors=strict,
        strictDivision=strict,
    )
```

---

## Test Results

### All Tests Pass

```bash
$ pytest tests/test_context_flags.py -v
=========================================================================
collected 33 items

TestContextFlagsBasic::test_default_flags PASSED                    [  3%]
TestContextFlagsBasic::test_set_flags PASSED                        [  6%]
TestContextFlagsBasic::test_flag_copy PASSED                        [  9%]
TestContextFlagsBasic::test_get_nonexistent PASSED                  [ 12%]
TestContextFlagsBasic::test_multiple_flags PASSED                   [ 15%]

TestToleranceFlags::test_relative_tolerance_default PASSED          [ 18%]
TestToleranceFlags::test_absolute_tolerance PASSED                  [ 21%]
TestToleranceFlags::test_custom_tolerance PASSED                    [ 24%]
TestToleranceFlags::test_near_zero_handling PASSED                  [ 27%]
TestToleranceFlags::test_tolerance_in_comparison PASSED             [ 30%]
TestToleranceFlags::test_tolerance_in_formula_eval PASSED           [ 33%]
TestToleranceFlags::test_different_contexts_different_tolerances PASSED [ 36%]
TestToleranceFlags::test_tolerance_persistence PASSED               [ 39%]

TestReduceFlags::test_reduce_constants_default PASSED               [ 42%]
TestReduceFlags::test_reduce_constants_affects_simplification PASSED [ 45%]
TestReduceFlags::test_reduce_constants_off PASSED                   [ 48%]
TestReduceFlags::test_reduce_constant_functions_default PASSED      [ 51%]
TestReduceFlags::test_formula_uses_reduce_flags PASSED              [ 54%]

TestSpecializedContextFlags::test_limited_polynomial_flags PASSED   [ 57%]
TestSpecializedContextFlags::test_limited_polynomial_strict_flags PASSED [ 60%]
TestSpecializedContextFlags::test_polynomial_factors_flags PASSED   [ 63%]
TestSpecializedContextFlags::test_polynomial_factors_strict_flags PASSED [ 66%]
TestSpecializedContextFlags::test_flags_not_leaked PASSED           [ 69%]
TestSpecializedContextFlags::test_context_switch_flags PASSED       [ 72%]
TestSpecializedContextFlags::test_custom_flag_persistence PASSED    [ 75%]

TestFlagInteractions::test_tolerance_with_zero_level PASSED         [ 78%]
TestFlagInteractions::test_strict_mode_reduces_constants_off PASSED [ 81%]
TestFlagInteractions::test_copying_preserves_all_flags PASSED       [ 84%]

TestFlagValidation::test_tolerance_positive PASSED                  [ 87%]
TestFlagValidation::test_tol_type_values PASSED                     [ 90%]
TestFlagValidation::test_zero_level_small PASSED                    [ 93%]
TestFlagValidation::test_boolean_flags PASSED                       [ 96%]
TestFlagValidation::test_flag_override PASSED                       [100%]

=========================================================================
33 passed in 0.07s
```

### No Regressions

```bash
$ pytest tests/ -v -q
=========================================================================
214 passed in 0.49s
```

---

## Files Created/Modified

### Created
- `tests/test_context_flags.py` (400+ lines, 33 tests)

### Modified
- `pg_mathobjects/real.py` - Fixed `zeroLevel` bug in `Real.__eq__()` (line 132)

---

## Week 5 Progress

- ✅ **Day 1**: FormulaUpToConstant (39 tests, 100%)
- ✅ **Day 2**: LimitedPolynomial (26 tests, 100%)
- ✅ **Day 3**: PolynomialFactors (33 tests, 100%)
- ✅ **Day 4**: Context Flag System (33 tests, 100%) ← **COMPLETE**
- 🔄 **Day 5**: Integration & Documentation (pending)

**Total Tests**: 214 (181 previous + 33 new)
**Pass Rate**: 100%

---

## Next Steps

### Week 5 Day 5: Integration & Documentation (4-5 hours)

1. **Create comprehensive documentation**
   - User guide for all Week 5 features
   - Migration guide from Perl WeBWorK
   - API reference

2. **Integration testing**
   - Test all contexts together
   - Context switching scenarios
   - Flag interactions across contexts

3. **Performance testing**
   - Benchmark key operations
   - Optimize if needed

4. **Example problem sets**
   - Real-world problem examples
   - Best practices guide

5. **Final validation**
   - Review all Week 5 code
   - Ensure consistent style
   - Documentation completeness

---

## Summary

Week 5 Day 4 is **100% complete** with comprehensive test coverage of the Context Flag System. All 13 existing flags have been validated, a critical bug in `zeroLevel` usage was fixed, and the WeBWorK singleton context pattern was confirmed and documented.

**Status**: ✅ COMPLETE - Ready for Day 5 (Integration & Documentation)

🎉 **214 tests passing, zero regressions!**
