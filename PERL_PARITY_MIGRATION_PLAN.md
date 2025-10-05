# Perl 1:1 Parity Migration Plan

**Goal**: Achieve complete Perl MathObjects parity by migrating to `pg_math` as the single source of truth.

**Date**: October 5, 2025
**Status**: Planning Phase

## Executive Summary

We currently have **two Formula implementations**:

1. **`pg_math`** (193 tests) - Complete Perl reference port with full parity
2. **`pg_mathobjects`** (243 tests) - Simplified implementation with Week 5 features

**Decision**: Migrate everything to `pg_math` and deprecate `pg_mathobjects`.

## Why `pg_math` Should Be The Winner

### Perl Parity Features (Only in `pg_math`)

| Feature | Perl Reference | `pg_math` | `pg_mathobjects` |
|---------|---------------|-----------|------------------|
| **Test point generation** | ✅ `createRandomPoints` | ✅ `create_random_points` | ❌ Missing |
| **Test point evaluation** | ✅ `createPointValues` | ✅ `create_point_values` | ❌ Missing |
| **Numeric comparison** | ✅ `compare()` via test points | ✅ `compare()` method | ❌ No `__eq__()` |
| **Domain checking** | ✅ Undefined point handling | ✅ Full implementation | ❌ Basic |
| **Python function gen** | ✅ `perlFunction` | ✅ `python_function()` | ❌ Missing |
| **Adaptive parameters** | ✅ Yes | ✅ `adapt_parameters()` | ❌ Missing |
| **Type precedence** | ✅ Full hierarchy | ✅ `TypePrecedence` enum | ❌ No hierarchy |
| **Tolerance modes** | ✅ Relative/Absolute/Sigfigs | ✅ `ToleranceMode` | ❌ Basic |
| **Complete value types** | ✅ Real/Complex/Point/Vector/Matrix/Interval/Set/Union | ✅ All types | ❌ Only Real/Formula |

### Architecture Comparison

**`pg_math`**:
- ✅ Base class: `MathValue` (matches Perl's `Value.pm` design)
- ✅ Type promotion system with precedence
- ✅ Operator overloading for all math types
- ✅ Fuzzy comparison with multiple tolerance modes
- ✅ Complete geometric types (Point, Vector, Matrix)
- ✅ Complete set types (Interval, Set, Union)
- ✅ Collections (List, String)
- ✅ 193 tests covering all types

**`pg_mathobjects`**:
- ⚠️ Base class: `Value` (simpler but less Perl-like)
- ⚠️ No type promotion system
- ⚠️ Only Real and Formula implemented
- ✅ Tight Context integration
- ✅ Week 5 features (FormulaUpToConstant, LimitedPolynomial, PolynomialFactors)
- ✅ 243 tests (includes Week 5 integration)

## Migration Strategy

### Phase 1: Port Week 5 Features to `pg_math` ✅ (Recommended Start)

**Duration**: 1-2 days

**Tasks**:
1. ✅ Add `Context` class to `pg_math` (port from `pg_mathobjects`)
2. ✅ Add `FormulaUpToConstant` to `pg_math`
3. ✅ Add `LimitedPolynomial` validation to `pg_math`
4. ✅ Add `PolynomialFactors` validation to `pg_math`
5. ✅ Add `Compute()` function to `pg_math`
6. ✅ Port all 243 tests to `pg_math`

**Files to Create in `pg_math`**:
```
packages/pg_math/pg_math/
  ├── context.py              (NEW - port from pg_mathobjects)
  ├── formula_up_to_constant.py  (NEW - port from pg_mathobjects)
  ├── limited_polynomial.py      (NEW - port from pg_mathobjects)
  ├── polynomial_factors.py      (NEW - port from pg_mathobjects)
  ├── compute.py                 (NEW - port from pg_mathobjects)
  └── answer_checker.py          (NEW - enhanced from pg_mathobjects)
```

**Tests to Port**:
```
packages/pg_math/tests/
  ├── test_context.py           (17 tests)
  ├── test_context_flags.py     (33 tests - Day 4)
  ├── test_formula_up_to_constant.py  (39 tests - Day 1)
  ├── test_limited_polynomial.py      (26 tests - Day 2)
  ├── test_polynomial_factors.py      (33 tests - Day 3)
  ├── test_week5_integration.py       (29 tests - Day 5)
  └── test_compute.py           (NEW - port compute tests)
```

### Phase 2: Implement Missing Perl Parity Features ⏭️

**Duration**: 2-3 days

**Priority 1 (Critical for Answer Checking)**:
1. ✅ Implement `Formula.__eq__()` using Perl's numeric comparison
   - Port test point generation if not already complete
   - Implement tolerance-based comparison at test points
   - **Effort**: 2-3 hours

2. ✅ Enhance `Formula.cmp()` to return proper evaluator
   - Should return `FormulaEvaluator` compatible with Perl
   - **Effort**: 2 hours

**Priority 2 (Important for Completeness)**:
3. ✅ Add remaining Context features
   - OperatorManager completion
   - FunctionManager completion
   - Full flag system
   - **Effort**: 4 hours

4. ✅ Add answer evaluators for all types
   - RealEvaluator, ComplexEvaluator
   - PointEvaluator, VectorEvaluator
   - IntervalEvaluator, etc.
   - **Effort**: 6 hours

**Priority 3 (Polish)**:
5. ✅ Complete FormEnhanced features
   - Granularity support
   - RNG seeding
   - Advanced domain checking
   - **Effort**: 4 hours

### Phase 3: Update All Imports and Dependencies 🔄

**Duration**: 1 day

**Files to Update**:
1. **Backend** (`apps/backend/`):
   - Update imports from `pg_mathobjects` → `pg_math`
   - No backend files currently import either (verified)

2. **Translator** (`packages/pg_translator/`):
   - ✅ Already imports from `pg_math` (sandbox.py)
   - Update test imports from `pg_mathobjects` → `pg_math`
   - Files to update:
     - `tests/test_tutorial_problems.py` (16 imports)
     - `tests/test_mathobjects_sandbox.py` (5 imports)

3. **Documentation**:
   - Update all Week 5 docs to reference `pg_math`
   - Update README files

### Phase 4: Deprecate `pg_mathobjects` 🗑️

**Duration**: 2 hours

**Tasks**:
1. Add deprecation warnings to `pg_mathobjects/__init__.py`
2. Update package metadata to mark as deprecated
3. Add redirect imports for backward compatibility (temporary)
4. Create migration guide for any external users

### Phase 5: Verification and Testing ✅

**Duration**: 1 day

**Tasks**:
1. Run full test suite (should have 436 tests total)
   - 193 original `pg_math` tests
   - 243 ported `pg_mathobjects` tests
2. Run integration tests
3. Test tutorial problem rendering
4. Verify no regressions in answer checking
5. Performance benchmarking

## Implementation Order (Detailed)

### Step 1: Port Context System (4 hours)

**File**: `packages/pg_math/pg_math/context.py`

```python
# Port from pg_mathobjects/context.py
# Key features:
- VariableManager
- ConstantManager
- FunctionManager
- OperatorManager
- ContextFlags
- Context class with singleton pattern
- get_current_context()
```

**Changes Needed**:
- Integrate with existing `MathValue` base class
- Ensure compatibility with Formula constructor
- Add all Perl context types (Numeric, Complex, Point, Vector, etc.)

### Step 2: Port Week 5 Features (8 hours)

**FormulaUpToConstant** (2 hours):
```python
# File: packages/pg_math/pg_math/formula_up_to_constant.py
- Inherit from pg_math.Formula (not pg_mathobjects.Formula)
- Use pg_math.Real instead of pg_mathobjects.Real
- Integrate with pg_math.Context
- Port all 39 tests
```

**LimitedPolynomial** (2 hours):
```python
# File: packages/pg_math/pg_math/limited_polynomial.py
- Port validation logic
- Integrate with Context flags
- Port all 26 tests
```

**PolynomialFactors** (2 hours):
```python
# File: packages/pg_math/pg_math/polynomial_factors.py
- Port factored validation
- Integrate with Context
- Port all 33 tests
```

**Compute()** (2 hours):
```python
# File: packages/pg_math/pg_math/compute.py
- Port Compute() function
- Integrate with pg_math types
- Port compute tests
```

### Step 3: Implement Formula.__eq__() (3 hours)

**File**: `packages/pg_math/pg_math/formula.py`

```python
def __eq__(self, other: Any) -> bool:
    """
    Compare formulas for equality using Perl's numeric test point strategy.

    Reference: lib/Value/Formula.pm::compare (lines 169-235)
    """
    if not isinstance(other, Formula):
        return False

    # Use existing compare() method which implements Perl strategy
    return self.compare(other, tolerance=0.001, mode=ToleranceMode.RELATIVE)
```

**Tests to Add**:
```python
# Add to test_formula.py
def test_formula_equality_same_expression():
    f1 = Formula("x^2 + 2*x + 1", ["x"])
    f2 = Formula("x^2 + 2*x + 1", ["x"])
    assert f1 == f2  # Should be True now

def test_formula_equality_equivalent_forms():
    f1 = Formula("x^2 + 2*x + 1", ["x"])
    f2 = Formula("(x+1)^2", ["x"])
    assert f1 == f2  # Equivalent via test points

def test_formula_inequality():
    f1 = Formula("x^2", ["x"])
    f2 = Formula("x^3", ["x"])
    assert f1 != f2
```

### Step 4: Update Imports (2 hours)

**Script**: `bin/migrate_imports.py`

```python
#!/usr/bin/env python3
"""Migrate imports from pg_mathobjects to pg_math."""

import re
from pathlib import Path

def migrate_file(filepath: Path):
    content = filepath.read_text()

    # Replace imports
    content = re.sub(
        r'from pg_mathobjects import',
        'from pg_math import',
        content
    )
    content = re.sub(
        r'import pg_mathobjects',
        'import pg_math',
        content
    )

    filepath.write_text(content)

# Migrate all Python files
for pattern in ['packages/pg_translator/**/*.py', 'apps/**/*.py']:
    for filepath in Path('.').glob(pattern):
        migrate_file(filepath)
```

### Step 5: Integration Testing (4 hours)

**Test Suite**: `packages/pg_math/tests/test_full_integration.py`

```python
"""Integration tests for complete pg_math system."""

def test_all_week5_features_work_together():
    """Verify all Week 5 features integrated properly."""
    # Test context switching
    # Test FormulaUpToConstant + LimitedPolynomial
    # Test PolynomialFactors + Context flags
    # Test answer checking across all types
    pass

def test_perl_parity_formula_comparison():
    """Verify Formula comparison matches Perl behavior."""
    # Test numeric comparison at test points
    # Test tolerance modes
    # Test domain mismatch detection
    pass

def test_all_mathvalue_types():
    """Verify all MathValue types work correctly."""
    # Real, Complex, Point, Vector, Matrix
    # Interval, Set, Union
    # List, String
    # Formula, FormulaUpToConstant
    pass
```

## Success Criteria

### Must Have ✅
- [ ] All 436 tests passing (193 + 243)
- [ ] Formula.__eq__() implemented with Perl numeric comparison
- [ ] All Week 5 features working in pg_math
- [ ] Context system fully integrated
- [ ] Zero regressions in existing functionality

### Should Have ⭐
- [ ] Complete answer evaluator system
- [ ] All MathValue types with cmp() methods
- [ ] FormulaEnhanced features complete
- [ ] Performance equal to or better than current

### Nice to Have 🎯
- [ ] Deprecation warnings in pg_mathobjects
- [ ] Migration guide documentation
- [ ] Performance benchmarks
- [ ] Memory profiling

## Risk Assessment

### High Risk ⚠️
1. **Breaking changes in pg_translator**
   - Mitigation: Comprehensive import migration + testing
   - Fallback: Keep pg_mathobjects temporarily with redirects

2. **Test failures during migration**
   - Mitigation: Port tests incrementally, verify at each step
   - Fallback: Fix compatibility issues in pg_math before deprecating

### Medium Risk ⚡
1. **Performance regressions**
   - Mitigation: Benchmark before/after
   - Fallback: Optimize critical paths

2. **API incompatibilities**
   - Mitigation: Maintain compatibility layer temporarily
   - Fallback: Update calling code

### Low Risk ✅
1. **Documentation updates**
   - Mitigation: Update docs as we go
   - Impact: Low (doesn't affect functionality)

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1. Port Week 5 to pg_math | 2 days | None |
| 2. Implement Perl parity | 3 days | Phase 1 |
| 3. Update imports | 1 day | Phase 1-2 |
| 4. Deprecate pg_mathobjects | 2 hours | Phase 3 |
| 5. Testing & verification | 1 day | All phases |
| **TOTAL** | **7-8 days** | Sequential |

With focused work: **5-6 days** (parallel where possible)

## Next Steps (Immediate)

### Step 1: Create Feature Branch
```bash
git checkout -b feature/perl-parity-migration
```

### Step 2: Port Context to pg_math (Start Here)
```bash
cd packages/pg_math
cp ../pg_mathobjects/pg_mathobjects/context.py pg_math/
# Edit to integrate with MathValue
# Run tests
```

### Step 3: Port First Week 5 Feature
```bash
# Start with FormulaUpToConstant (easiest, well-tested)
cp ../pg_mathobjects/pg_mathobjects/formula_up_to_constant.py pg_math/
cp ../pg_mathobjects/tests/test_formula_up_to_constant.py tests/
# Edit imports and integration
# Run tests
```

### Step 4: Iterate
- Port one feature at a time
- Verify tests pass before moving to next
- Commit after each successful port

## Completion Checklist

- [ ] Context system ported and integrated
- [ ] FormulaUpToConstant ported (39 tests)
- [ ] LimitedPolynomial ported (26 tests)
- [ ] PolynomialFactors ported (33 tests)
- [ ] Context flags ported (33 tests)
- [ ] Integration tests ported (29 tests)
- [ ] Compute() ported
- [ ] Formula.__eq__() implemented
- [ ] All 436 tests passing
- [ ] pg_translator imports updated
- [ ] Documentation updated
- [ ] pg_mathobjects deprecated
- [ ] Migration guide created

## References

- **Perl Reference**: `lib/Value.pm`, `lib/Value/*.pm`
- **pg_math Package**: `packages/pg_math/`
- **pg_mathobjects Package**: `packages/pg_mathobjects/`
- **Week 5 Documentation**: `packages/pg_mathobjects/WEEK5_*.md`
- **Test Suites**: Both packages' `tests/` directories

---

**Author**: GitHub Copilot
**Review Status**: Awaiting approval
**Target Completion**: October 12, 2025 (1 week from today)
