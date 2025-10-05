# Week 5 Day 4: Context Flag System - Implementation Plan

**Goal**: Enhance and test the context flag system  
**Estimated Time**: 2-3 hours  
**Date**: October 5, 2025

## Overview

The Context flag system controls behavior of parsing, evaluation, and answer checking. Many flags are already implemented, but need comprehensive testing and a few additions.

## Existing Flags (Already Implemented)

From `context.py` ContextFlags.__init__():
- ✅ `tolerance`: 0.001 (used in Real equality)
- ✅ `tolType`: 'relative' or 'absolute' (used in Real equality)
- ✅ `zeroLevel`: 1e-14 (threshold for near-zero handling)
- ✅ `zeroLevelTol`: 1e-12 (tolerance when near zero)
- ✅ `reduceConstants`: 1 (whether to simplify constants)
- ✅ `reduceConstantFunctions`: 1 (whether to simplify constant function calls)

From specialized contexts:
- ✅ `limitedPolynomial`: Set by LimitedPolynomial context
- ✅ `strictCoefficients`: Set by strict contexts
- ✅ `singlePowers`: One term per degree
- ✅ `polynomialFactors`: Set by PolynomialFactors context
- ✅ `singleFactors`: No repeated factors
- ✅ `strictPowers`: Only single factors to powers
- ✅ `strictDivision`: Only single factors divided

## Flags to Add/Enhance

### 1. formatStudentAnswer (Medium Priority)
**Purpose**: Control how student answers are displayed in feedback  
**Values**: 'evaluated', 'parsed', 'reduced', etc.  
**Default**: 'evaluated'  
**Use**: Answer checker formatting

### 2. limits (Low Priority - Formula evaluation)
**Purpose**: Bounds for test point generation in Formula checking  
**Values**: Dictionary/list of [min, max] for each variable  
**Default**: None (use default ranges)  
**Use**: Formula answer checker

### 3. num_points (Low Priority - Formula evaluation)
**Purpose**: Number of test points for Formula comparison  
**Default**: 5  
**Use**: Formula answer checker

### 4. showTypeWarnings (Low Priority)
**Purpose**: Whether to warn about type mismatches  
**Default**: True  
**Use**: Error messages

## Implementation Strategy

### Phase 1: Comprehensive Flag Testing (1.5 hours)

Focus on testing existing flags that aren't well-tested yet:

1. **Tolerance Tests** (10 tests)
   - Test relative tolerance (default)
   - Test absolute tolerance
   - Test near-zero handling (zeroLevel)
   - Test custom tolerance values
   - Test in different operations

2. **Reduce Flags Tests** (5 tests)
   - Test reduceConstants behavior
   - Test reduceConstantFunctions behavior
   - Test with/without reduction
   - Verify Formula simplification

3. **Context-Specific Flags** (8 tests)
   - Verify LimitedPolynomial flags work correctly
   - Verify PolynomialFactors flags work correctly
   - Test flag inheritance in context copies

### Phase 2: Add New Flags (30-45 min)

1. **formatStudentAnswer Flag**
   - Add to ContextFlags defaults
   - Use in answer checker formatting
   - Test different format modes

2. **limits Flag**
   - Add to ContextFlags
   - Use in Formula evaluation test point generation
   - Test custom ranges

3. **num_points Flag**
   - Add to ContextFlags
   - Use in Formula answer checking
   - Test different point counts

### Phase 3: Documentation & Examples (30 min)

1. Document all flags in context.py
2. Create usage examples
3. Update API documentation

## Test Plan

**Target**: 20+ tests

### Test Suite Structure

#### TestContextFlagsBasic (5 tests)
- `test_default_flags()` - Verify default values
- `test_set_flags()` - Set and retrieve flags
- `test_flag_copy()` - Flags copied with context
- `test_get_nonexistent()` - Returns None for undefined
- `test_multiple_flags()` - Set multiple at once

#### TestToleranceFlags (8 tests)
- `test_relative_tolerance_default()` - Default relative tolerance
- `test_absolute_tolerance()` - Switch to absolute
- `test_custom_tolerance()` - Custom tolerance value
- `test_near_zero_handling()` - zeroLevel behavior
- `test_zero_level_tolerance()` - zeroLevelTol usage
- `test_tolerance_in_comparison()` - Real equality uses it
- `test_tolerance_in_checker()` - Answer checker uses it
- `test_tolerance_inheritance()` - Copied contexts preserve it

#### TestReduceFlags (5 tests)
- `test_reduce_constants_on()` - 2+3 → 5
- `test_reduce_constants_off()` - Keep as 2+3
- `test_reduce_constant_functions_on()` - sin(0) → 0
- `test_reduce_constant_functions_off()` - Keep as sin(0)
- `test_formula_simplification()` - Affects Formula.reduce()

#### TestSpecializedContextFlags (6 tests)
- `test_limited_polynomial_flags()` - Verify set correctly
- `test_polynomial_factors_flags()` - Verify set correctly
- `test_strict_mode_flags()` - All strict flags set
- `test_flag_not_leaked()` - Flags don't affect other contexts
- `test_context_switch_flags()` - Flags change with context
- `test_custom_flag_persistence()` - User flags persist

#### TestNewFlags (optional, if time permits)
- `test_format_student_answer()` - Different format modes
- `test_limits_flag()` - Custom variable ranges
- `test_num_points_flag()` - Test point count

## Success Criteria

- ✅ 20+ tests passing (100%)
- ✅ All existing flags tested
- ✅ tolerance/tolType working correctly in comparisons
- ✅ reduce flags working correctly
- ✅ Context-specific flags tested
- ✅ Documentation complete
- ✅ No regressions in existing tests

## Files to Create/Modify

**Create**:
- `tests/test_context_flags.py` (~300 lines, 20+ tests)

**Modify**:
- `pg_mathobjects/context.py` (add documentation, maybe new flags)
- `pg_mathobjects/real.py` (ensure zeroLevel used correctly)
- `pg_mathobjects/answer_checker.py` (if adding formatStudentAnswer)

## Technical Notes

### Tolerance Implementation

Already implemented in Real.__eq__():
```python
tolerance = self.context.flags.get('tolerance')
tol_type = self.context.flags.get('tolType')

if tol_type == 'relative':
    if abs(self.value) < 1e-14:  # Near zero
        return abs(other_value) < tolerance
    return abs(self.value - other_value) / abs(self.value) < tolerance
else:
    return abs(self.value - other_value) < tolerance
```

### Reduce Flags

Currently defined but may not be used:
- Need to check if Formula uses reduceConstants
- Need to check if function evaluation uses reduceConstantFunctions

### Context Isolation

Important: Flags should be per-context instance
- Different contexts shouldn't share flag state
- Context.copy() should copy flags
- Creating new context should have fresh flags

## Time Breakdown

- Phase 1: Comprehensive flag testing: 1.5 hours
  - Basic flags: 20 min
  - Tolerance: 30 min
  - Reduce: 20 min
  - Specialized: 20 min
  - Debug/fix: 20 min
- Phase 2: New flags (if time): 30-45 min
- Phase 3: Documentation: 30 min
- **Total**: 2-3 hours

## Next Steps After Completion

Week 5 Day 5: Integration & Documentation
- Test with real tutorial problems
- Performance analysis
- Complete Week 5 summary
- Final polish

---

**Ready to implement!** 🚀

Let's focus on thorough testing of existing flags to ensure quality over quantity.
