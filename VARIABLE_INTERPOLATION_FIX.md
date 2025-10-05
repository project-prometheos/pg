# Variable Interpolation Fix - October 5, 2024

## Problem
Frontend was showing literal variable names like `[a]`, `[b]`, `[c]` instead of their numeric values in PGML markup.

Example from AlgebraicFractionAnswer:
```
[a]yy−[c]+[b][c]−y=
```

Should have shown:
```
8y/(y-1) + 9/(1-y) =
```

## Root Cause
The PGML renderer's variable interpolation pattern was not matching variables correctly after preprocessing:

1. **Original PGML**: `[$a]`, `[$b]`, `[$c]` (with `$` prefix)
2. **After Preprocessing**: `[a]`, `[b]`, `[c]` (preprocessor removes `$`)
3. **Renderer Pattern**: `r'\[\$(\w+)\]'` - Only matches `[$var]`, misses `[var]`

Result: Variables weren't interpolated because the pattern expected a `$` that was already removed.

## Solution
Updated the variable interpolation regex pattern in `packages/pg_renderer/pg_renderer/pgml.py`:

### Before
```python
html = re.sub(r'\[\$(\w+)\]', self._interpolate_var, html)
```

### After
```python
html = re.sub(r'\[\$?([a-zA-Z]\w*)\]', self._interpolate_var, html)
```

### Key Changes
1. **`\$?`** - Makes the `$` optional to match both `[$a]` and `[a]`
2. **`[a-zA-Z]\w*`** - Must start with a letter (not underscore)
   - This prevents matching `[_]` answer blank patterns
   - Avoids conflict with `[_]{$answer}` syntax

## Files Modified
- `packages/pg_renderer/pg_renderer/pgml.py` (line 31)

## Testing
Verified with multiple problems and seeds:

```bash
# AlgebraicFractionAnswer - seed 0
# Shows: 8y/(y-1) + 9/(1-y) = 
✅ Variables: a=8, b=9, c=1

# AlgebraicFractionAnswer - seed 42
# Shows: 2y/(y-5) + 3/(5-y) =
✅ Variables: a=2, b=3, c=5

# ExpandedPolynomial - seed 0
✅ Variables interpolated correctly
```

## Related Work
This completes the variable interpolation fix that was mentioned as a pending issue in the answer checking implementation. Now:

✅ **Answer Checking** - Working correctly (fixed attribute name: `answer_message`)
✅ **Variable Interpolation** - Working correctly (fixed regex pattern)
⏳ **Variable Substitution in Formulas** - Still shows `b*x + c` instead of `-6*x + 4` (separate issue)

## Impact
All PGML variable interpolation now works correctly. Problems that use `[$varname]` syntax will display the actual numeric values instead of showing the literal variable names.
