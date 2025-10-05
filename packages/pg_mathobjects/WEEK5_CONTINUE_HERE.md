# Week 5 Day 1: Continue Here

**Current Status**: 21/39 tests passing (54%)

## Quick Start

```powershell
cd d:\pg\packages\pg_mathobjects
pytest tests/test_formula_up_to_constant.py -v --tb=short
```

## Three Quick Fixes Needed

### Fix 1: Tolerance Attribute (2 minutes)

**File**: `formula_up_to_constant.py` line 254

**Change**:
```python
# OLD (line 254):
tolerance = self._private_context.tolerance

# NEW:
tolerance = getattr(self._private_context, 'tolerance', 0.001)
```

**Impact**: Fixes 10+ tests

### Fix 2: Formula Equality (5 minutes)

**File**: `tests/test_formula_up_to_constant.py`

**Line 302**:
```python
# OLD:
assert df == Formula("x")

# NEW:
assert df._tree.equals(Formula("x")._tree)
```

**Line 319**:
```python
# OLD:
assert f_no_c == Formula("x**2/2")

# NEW:
assert f_no_c._tree.equals(Formula("x**2/2")._tree)
```

**Impact**: Fixes 2 tests

### Fix 3: tex() Method Name (1 minute)

**File**: `tests/test_formula_up_to_constant.py` line 385

**Change**:
```python
# OLD:
tex = f.tex()

# NEW:
tex = f.TeX()
```

**Impact**: Fixes 1 test

## Run Tests Again

```powershell
pytest tests/test_formula_up_to_constant.py -v
```

**Expected Result**: 30+ tests passing (~77%)

## If Issues Persist

### Check Context Implementation

```powershell
grep -r "class Context" pg_mathobjects/
```

### Check Formula.__eq__

```powershell
grep -A 10 "__eq__" pg_mathobjects/formula.py
```

### Debug Answer Checker

```python
# Test manually:
python -c "
from pg_mathobjects import FormulaUpToConstant
f = FormulaUpToConstant('x^2/2 + C')
checker = f.cmp()
result = checker('x^2/2 + K')
print('Correct:', result.get('correct'))
print('Score:', result.get('score'))
"
```

## Next After Fixes

1. **Test with real problem** - IndefiniteIntegrals.pg
2. **Integration test** - With Week 4 tests
3. **Document completion** - WEEK5_DAY1_COMPLETE.md
4. **Move to Day 2** - LimitedPolynomial context

## Time Estimate

- Fixes: 10 minutes
- Testing: 5 minutes
- Validation: 15 minutes
- **Total**: 30 minutes to 80%+ passing

## Files to Edit

1. `pg_mathobjects/formula_up_to_constant.py` (line 254)
2. `tests/test_formula_up_to_constant.py` (lines 302, 319, 385)

## Success Criteria

- ✅ 30+ tests passing (77%)
- ✅ All creation tests pass
- ✅ Most comparison tests pass
- ✅ Answer checker works
- ✅ No AttributeError exceptions

## Then Move to Day 2

**Next Feature**: LimitedPolynomial Context
- Restrict formulas to polynomial form
- No division, radicals, trig
- 15+ tests
- 3-4 hours

---

**Quick Action**: Make the 3 fixes above and rerun tests! 🚀
