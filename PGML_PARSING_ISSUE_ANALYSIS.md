# PGML Parsing Issue - Analysis Report

## Problem Summary

The FractionAnswer.pg problem is not being rendered correctly. The PGML output shows raw syntax instead of being parsed into answer blanks:

**Current Output:**
```
Answer = PerlList([_]){answer.cmp(...)}{15}
```

**Expected Output:**
```
Simplify 6/4

Answer = [input field]
```

## Root Causes Identified

### 1. Missing Fat Comma (=>) to Equals (=) Conversion in PGML

**Location:** `packages/pg/translator/pg_preprocessor_pygment.py`, line 3677-3707 in `_transform_pgml_evaluators` method

**Issue:**
The `_transform_pgml_evaluators` method handles Perl-to-Python syntax conversion in PGML answer blank expressions, but it's missing the conversion of Perl's fat comma operator (`=>`) to Python's equals sign (`=`).

**Current Code (lines 3696-3699):**
```python
def _transform_pgml_evaluators(self, pgml_content: str) -> str:
    """Transform Perl syntax to Python in PGML evaluator expressions."""
    # ... iteration code ...
    transformed = code_block.replace(
        '->', '.').replace('::', '.')
    transformed = re.sub(
        r'\$([a-zA-Z_]\w*)', r'\1', transformed)
    # Missing: conversion of => to =
```

**What Happens:**
For the FractionAnswer.pg answer blank:
```perl
Answer = [_]{$answer->cmp(
    studentsMustReduceFractions => 1,
    reduceFractions => 1,
    allowMixedNumbers => 0
)}{15}
```

After transformation, it becomes:
```python
Answer = [_]{answer.cmp(
    studentsMustReduceFractions => 1,  # INVALID PYTHON!
    reduceFractions => 1,              # INVALID PYTHON!
    allowMixedNumbers => 0             # INVALID PYTHON!
)}{15}
```

This is invalid Python syntax because `=>` is not a valid operator in Python.

### 2. Variable Interpolation Not Accounting for $ Removal in Braces

**Location:** `packages/pg/renderer/pgml.py`, line 32

**Context:**
After `_transform_pgml_evaluators` removes the `$` prefix from variables inside braces (line 3699), the variable interpolation regex expects to match the variable. However:

```python
# Line 32 in pgml.py
html = re.sub(r'\[\$?([a-zA-Z]\w*)\]', self._interpolate_var, html)
```

This matches `[$varname]` for variable interpolation. But inside the answer blank braces, after preprocessing, we have just `answer` (without `$`), which doesn't need interpolation since it's already been processed.

The real issue is that the argument to `->cmp(...)` contains keyword arguments with `=>` that need conversion.

## Files Involved

### Primary Files:

1. **`packages/pg/translator/pg_preprocessor_pygment.py`** (lines 3677-3707)
   - Contains `_transform_pgml_evaluators` method
   - Currently missing `=>` to `=` conversion
   - Also missing `->` conversion in method calls within cmp() options

2. **`packages/pg/renderer/pgml.py`** (lines 19-82)
   - The PGMLRenderer that processes PGML blocks
   - Regex patterns for answer blank detection (line 53)
   - Should receive properly transformed PGML from preprocessor

3. **`packages/pg/translator/in_process_sandbox.py`** (line 480)
   - Calls PGMLRenderer after getting PGML string from preprocessor
   - Expects well-formed Python-compatible syntax

### Secondary Files:

4. **`tutorial/sample-problems/Algebra/FractionAnswer.pg`**
   - The problem file being rendered incorrectly
   - Has multi-line answer blank with cmp() options using `=>`

## How the Pipeline Works

1. **Preprocessing Phase:**
   - `pg_preprocessor_pygment.py` reads the .pg file
   - Detects `BEGIN_PGML ... END_PGML` blocks
   - Calls `_transform_pgml_evaluators()` to convert Perl syntax to Python
   - Stores transformed PGML and generates code like: `TEXT(PGML(PGML_BLOCK_0))`

2. **Execution Phase:**
   - The Python code is executed
   - `PGML(pgml_text)` function is called (from `in_process_sandbox.py`)
   - This instantiates `PGMLRenderer(variables=namespace)` and calls `renderer.render(pgml_text)`

3. **Rendering Phase:**
   - `PGMLRenderer.render()` processes PGML
   - Should convert `[_]{...}` patterns to answer blanks
   - Should interpolate `[$var]` patterns with variable values

## The Bug Chain

1. `_transform_pgml_evaluators` converts `->` to `.` but leaves `=>` untouched
2. The PGML string still contains invalid Python syntax `keyword => value`
3. When `PGMLRenderer.render()` tries to process the answer blank expression:
   ```
   [_]{answer.cmp(studentsMustReduceFractions => 1, ...)}
   ```
4. The regex on line 53 matches the answer blank correctly
5. But the `_create_answer_blank` method (line 153) tries to evaluate this invalid Python
6. The evaluation fails, and the raw PGML is returned as-is (or causes an error)

## Error Messages & Symptoms

- PGML is not being parsed - answer blank syntax `[_]{...}` shows as raw text
- Variable interpolation like `$answer` shows as "answer" instead of being interpolated
- Output shows `PerlList(...)` formatting from problem metadata being displayed
- No answer blanks are created in the output

## Solution

Add conversion of fat comma (`=>`) to equals (`=`) in the `_transform_pgml_evaluators` method.

**Fix Location:** `packages/pg/translator/pg_preprocessor_pygment.py`, line 3696-3702

**Required Changes:**
After converting `->` to `.` and removing `$` sigils, also convert `=>` to `=`.

This needs to handle:
1. Simple cases: `key => value` → `key = value`
2. Multi-line cases (already handled by the block extraction in lines 3683-3693)
3. Preserve the order of transformations

