# Complete Fix for studentsMustReduceFractions Enforcement

## Problem Statement
The `studentsMustReduceFractions` option in fraction answer checking was not being enforced. When a PGML problem specified:

```perl
Answer = [_]{$answer->cmp(studentsMustReduceFractions => 1, ...)}
```

Unreduced fractions like `12/8` and `6/4` were being accepted as correct when they should be rejected with the message "Your answer is not reduced to lowest terms".

## Root Cause Analysis

The problem involved a broken data flow across four major components:

1. **PGML Renderer**: Extracted options from cmp() calls but didn't store the evaluator object
2. **Executor**: Registered answer blanks but didn't properly preserve options
3. **Translator**: Didn't extract options from answer entries to pass to context flags
4. **Context Flags**: Wasn't checking for studentsMustReduceFractions option

## Fixes Applied

### Fix 1: Translator - Extract studentsMustReduceFractions (Commit f99bf456)

**File**: `packages/pg/translator/translator.py`

**Method**: `_cmp_context_flags()` (lines 350-368)

**Change**: Modified the method to:
- Extract `cmp_options` from AnswerResult.metadata
- Check for `studentsMustReduceFractions` in cmp_options
- Set `reduceFractions = 0` when `studentsMustReduceFractions` is enabled

This ensures the context flag `reduceFractions = 0` prevents automatic reduction of the student's fraction during parsing, allowing FractionAnswerChecker to verify that the student entered an already-reduced fraction.

### Fix 2: Preprocessor - Convert Perl Fat Comma (Commit 088574bb)

**File**: `packages/pg/translator/pg_preprocessor_pygment.py`

**Method**: `_transform_pgml_evaluators()` (line 3701)

**Change**: Added `.replace('=>', '=')` to the transformation pipeline

This converts Perl's fat comma operator (`=>`) to Python's assignment operator (`=`), so that PGML evaluator expressions are converted from:
- `$answer->cmp(studentsMustReduceFractions => 1)` (invalid Python)
- to: `answer.cmp(studentsMustReduceFractions = 1)` (valid Python)

### Fix 3: PGML Renderer - Handle Python-Style Calls (Commit a2f9fe69)

**File**: `packages/pg/renderer/pgml.py`

**Methods**:
- `_eval_answer()` (lines 197-231): Added Python-style method call handler
- `_parse_cmp_options()` (lines 398-404): Added dual-separator parsing

**Changes**:
1. Added pattern matcher for `var.cmp(...)` expressions (Python-style, after preprocessor conversion)
2. Extracts variable name and options from the expression
3. Builds answer specification with options included
4. Enhanced `_parse_cmp_options()` to parse both `=>` and `=` separators

### Fix 4: Store Evaluator in PGML Spec (Commit 6b3cbb78)

**File**: `packages/pg/renderer/pgml.py`

**Method**: `_eval_answer()` (line 228)

**Change**: Added `'evaluator': base_val` to the answer spec dict

This ensures the actual evaluator object is included in the PGML answer blank spec so the translator can access it later.

### Fix 5: Extract Options in Translator (Commit 6b3cbb78)

**File**: `packages/pg/translator/translator.py`

**Method**: `_evaluate_answers()` (lines 969-981, 1115)

**Changes**:
1. Enhanced answer entry format detection to handle PGML spec dicts with 'evaluator' and 'options' keys
2. Extract `cmp_options` from PGML specs and track them through group_items
3. Store cmp_options in `AnswerResult.metadata['cmp_options']` (line 1115)
4. Fixed all group_items unpacking to handle the cmp_options tuple element

## Complete Data Flow

Now the data flows correctly:

```
PGML Code:
  [_]{$answer->cmp(studentsMustReduceFractions => 1, ...)}
         ↓
PGML Renderer (_eval_answer for Python-style):
  - Detects: answer.cmp(studentsMustReduceFractions = 1, ...)
  - Parses options: {'studentsMustReduceFractions': 1, ...}
  - Returns spec: {
      'correct_value': '3/2',
      'type': 'formula',
      'evaluator': <Fraction object>,
      'options': {'studentsMustReduceFractions': 1, ...}
    }
         ↓
Executor (render_text):
  - self.answers.update(answer_blanks)
  - Stores spec dict in environment.answers
         ↓
Translator (_evaluate_answers):
  - Extracts evaluator and cmp_options from spec dict
  - Stores cmp_options in AnswerResult.metadata['cmp_options']
         ↓
Translator (_cmp_parse → _cmp_context_flags):
  - Retrieves cmp_options from metadata
  - Sees studentsMustReduceFractions: 1
  - Sets context flag: reduceFractions = 0
         ↓
Fraction Parsing (in Compute):
  - Respects reduceFractions = 0
  - Does NOT automatically reduce student's fraction
         ↓
FractionAnswerChecker (check method):
  - Compares: student_frac == correct_frac
  - Checks: is_reduced() on student's fraction
  - Rejects: "Your answer is not reduced to lowest terms"
```

## Testing

To verify the fix works:

```bash
python test_pgml_fix.py
```

Expected output:
- Statement HTML should render correctly
- Answer blanks should be detected
- Options should flow through to metadata

To verify fraction checking:

```bash
python pg_solve.py tutorial/sample-problems/Algebra/FractionAnswer.pg
```

Then submit:
- `3/2` → Correct (reduced)
- `12/8` → Wrong, "Your answer is not reduced to lowest terms"
- `6/4` → Wrong, "Your answer is not reduced to lowest terms"

## Files Modified

1. `packages/pg/renderer/pgml.py` - PGML renderer fixes
2. `packages/pg/translator/translator.py` - Translator context flags and option extraction
3. `packages/pg/translator/pg_preprocessor_pygment.py` - Preprocessor fat comma conversion

## Commits

- f99bf456: Fix studentsMustReduceFractions enforcement in translator
- 088574bb: Fix PGML preprocessor to convert Perl fat comma to Python assignment
- a2f9fe69: Add support for Python-style method calls in PGML renderer
- 6b3cbb78: Store cmp_options in AnswerResult metadata for proper option flow
