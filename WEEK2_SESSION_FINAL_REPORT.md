# PG to Python Translation - Week 2 Session Results

**Date**: November 9, 2025
**Session Goal**: Continue fixing sample problems, improve from 73% pass rate
**Result**: ✅ Achieved 82% pass rate (129/157 problems)

## Key Accomplishments

### 1. Grammar Bug Discovery & Fix: || and && Operators
The Lark parser was silently dropping `||` and `&&` operators due to confusion with Lark's own syntax.

```perl
# Before (broken)
$a || $b   →   (a)  # Entire || $b disappeared!

# After (fixed)
$a || $b   →   (a or b)  ✓
```

**Root Cause**: String literals `"||"` and `"&&"` were being interpreted as regex alternation syntax by Lark.
**Solution**: Changed to proper terminal definitions `OR_OP: "||"` and `AND_OP: "&&"`.

### 2. Perl do-until Loop Preprocessing
Perl allows multi-line `do { } until` blocks where the condition spans multiple lines:

```perl
# Before (broken - indentation error)
do { $x2 = random(-8, 8); $y2 = random(-8, 8) }
    until ($y3 - $y1) * ($x2 - $x1) != ($y2 - $y1) * ($x3 - $x1);

# After (fixed - proper while True loop)
while True:
    x2 = random((-8), 8)
    y2 = random((-8), 8)
    if (y3 - y1) * (x2 - x1) != (y2 - y1) * (x3 - x1):
        break
```

**Key Fix**: Don't include condition lines in the body extraction - they are separate!

## Pass Rate Improvement

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Pass Rate | 73% | 82% | +9% |
| Problems Passing | 115 | 129 | +14 |
| Problems Failing | 42 | 28 | -14 |

## Problems Fixed This Session (14 total)

**From || and && fix (~4 problems)**:
- Complex boolean expressions now correctly parsed
- Multi-line conditions with logical operators work

**From do-until fix (5 problems - specifically identified)**:
- ✅ NoSolution
- ✅ LinearApprox  
- ✅ LineSegmentGraphTool
- ✅ QuadrilateralGraphTool
- ✅ TriangleGraphTool

**From combined fixes (~5 more problems)**:
- Various problems using complex conditions and loops

## Remaining Work (28 problems, 18%)

Most failures are now individual/diverse:
- 1 problem: Nested hash with lambda
- 1 problem: Unterminated string literal
- 1 problem: Invalid decimal literal
- 25 problems: Various "invalid syntax" errors

These require problem-specific investigation rather than systemic fixes.

## Technical Details

### Files Modified
- `packages/pg_translator/pg_translator/pg_preprocessor_pygment.py`
  - Lines 653-654: Added OR_OP and AND_OP terminals
  - Lines 636-637: Updated or_expr and and_expr rules
  - Lines 408-453: Rewrote multi-line do-until detection
  - Lines 462-510: Fixed body extraction logic

### Grammar Changes
```
# Before (broken)
?or_expr: and_expr (("||" | "or") and_expr)*
?and_expr: comp_expr (("&&" | "and") comp_expr)*

# After (fixed)
OR_OP: "||"
AND_OP: "&&"
?or_expr: and_expr ((OR_OP | "or") and_expr)*
?and_expr: comp_expr ((AND_OP | "and") comp_expr)*
```

## Next Steps to Reach 90% (10 more problems needed)

1. **Quick Wins** (2-3 problems):
   - Unterminated string literal in PrimesInFormulas
   - Invalid decimal literal in MatchingAlt
   - Generic syntax errors

2. **Medium Effort** (5-10 problems):
   - Investigate pattern in "invalid syntax" errors
   - Fix issues in plotting/input modules (ParametricPlot, BarGraph, etc.)
   - Handle complex subscripting and formatting

3. **Complex Issues** (15+ problems):
   - Nested structures with lambdas/closures
   - Complex dynamic string generation
   - Advanced GraphTool configurations

## Lessons Learned

1. **Lark Syntax Collision**: String literals in grammar rules can conflict with Lark's own operators. Use terminals for operators.
2. **Multi-line Perl Constructs**: Many Perl idioms span multiple lines - need to track this during preprocessing.
3. **Body Extraction Complexity**: When splitting code into body and condition, don't accidentally include both parts of non-sequential lines.
4. **Operator Translation**: Must handle both Perl `||`/`&&` and textual `or`/`and` keywords.

## Conclusion

Achieved significant improvement (73% → 82%) by fixing two critical systemic bugs in the Lark grammar. Remaining 28 problems appear to require individual investigation, suggesting the preprocessor's core logic is now quite solid.
