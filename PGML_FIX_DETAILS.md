# PGML Parsing Issue - Fix Details

## Issue Summary

The `_transform_pgml_evaluators` method in `packages/pg/translator/pg_preprocessor_pygment.py` is missing the conversion of Perl's fat comma operator (`=>`) to Python's equals sign (`=`).

This causes PGML answer blank expressions like:
```perl
[_]{$answer->cmp(studentsMustReduceFractions => 1, ...)}
```

To become invalid Python:
```python
[_]{answer.cmp(studentsMustReduceFractions => 1, ...)}  # Invalid syntax!
```

## File to Fix

**File:** `d:\pg\packages\pg\translator\pg_preprocessor_pygment.py`

**Method:** `_transform_pgml_evaluators` (lines 3677-3707)

## Current Code (BROKEN)

```python
def _transform_pgml_evaluators(self, pgml_content: str) -> str:
    """Transform Perl syntax to Python in PGML evaluator expressions."""
    import re
    result: List[str] = []
    i = 0
    while i < len(pgml_content):
        if pgml_content[i] == '{':
            brace_depth = 1
            j = i + 1
            while j < len(pgml_content) and brace_depth > 0:
                if pgml_content[j] == '{':
                    brace_depth += 1
                elif pgml_content[j] == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        break
                j += 1
            if brace_depth == 0:
                code_block = pgml_content[i+1:j]
                transformed = code_block.replace(
                    '->', '.').replace('::', '.')
                transformed = re.sub(
                    r'\$([a-zA-Z_]\w*)', r'\1', transformed)
                # BUG: Missing conversion of => to =
                result.append('{')
                result.append(transformed)
                result.append('}')
                i = j + 1
                continue
        result.append(pgml_content[i])
        i += 1
    return ''.join(result)
```

## Root Cause

Line 3699 removes the `$` sigil but doesn't convert Perl's fat comma (`=>`) to Python's equals (`=`).

The transformations need to include:
1. `->` to `.` (method call operator) ✓ Already done
2. `::` to `.` (scope resolution) ✓ Already done  
3. `$var` to `var` (variable sigil removal) ✓ Already done
4. `=>` to `=` (fat comma operator) ✗ **MISSING**

## How to Fix

Add a regex substitution to convert `=>` to `=` after removing the `$` sigils:

```python
def _transform_pgml_evaluators(self, pgml_content: str) -> str:
    """Transform Perl syntax to Python in PGML evaluator expressions."""
    import re
    result: List[str] = []
    i = 0
    while i < len(pgml_content):
        if pgml_content[i] == '{':
            brace_depth = 1
            j = i + 1
            while j < len(pgml_content) and brace_depth > 0:
                if pgml_content[j] == '{':
                    brace_depth += 1
                elif pgml_content[j] == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        break
                j += 1
            if brace_depth == 0:
                code_block = pgml_content[i+1:j]
                # Transform Perl syntax to Python
                transformed = code_block.replace(
                    '->', '.').replace('::', '.')
                # Remove $ sigils from variable names
                transformed = re.sub(
                    r'\$([a-zA-Z_]\w*)', r'\1', transformed)
                # FIX: Convert Perl fat comma => to Python =
                transformed = re.sub(
                    r'\s*=>\s*', ' = ', transformed)
                result.append('{')
                result.append(transformed)
                result.append('}')
                i = j + 1
                continue
        result.append(pgml_content[i])
        i += 1
    return ''.join(result)
```

## What This Fixes

**Before Fix:**
```perl
BEGIN_PGML
Answer = [_]{$answer->cmp(
    studentsMustReduceFractions => 1,
    reduceFractions => 1,
    allowMixedNumbers => 0
)}{15}
END_PGML
```

Gets transformed to (INVALID):
```
Answer = [_]{answer.cmp(
    studentsMustReduceFractions => 1,
    reduceFractions => 1,
    allowMixedNumbers => 0
)}{15}
```

**After Fix:**
```
Answer = [_]{answer.cmp(
    studentsMustReduceFractions = 1,
    reduceFractions = 1,
    allowMixedNumbers = 0
)}{15}
```

This is now valid Python syntax that can be evaluated and rendered as an answer blank.

## Testing

After applying the fix, these should work:

1. FractionAnswer.pg should render correctly with answer blank
2. Variable interpolation should work properly
3. Answer checking with the cmp() options should work

Test command:
```bash
pytest packages/pg/translator/tests/test_tutorial_sample_problems_runtime.py::TestTutorialSampleProblemsRuntime::test_correct_answer_scores_full_credit -k "FractionAnswer" -v
```

