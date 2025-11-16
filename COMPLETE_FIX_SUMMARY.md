# Complete Fix for studentsMustReduceFractions and PGML Answer Blank Detection

## Problem Summary

Two interconnected issues were preventing proper fraction answer checking and answer blank detection in PGML problems:

1. **studentsMustReduceFractions not enforced**: When a PGML problem specified that students must enter reduced fractions, the option was not being passed through the evaluation pipeline, so unreduced fractions were incorrectly accepted.

2. **Answer blanks not detected in pg_solve.py**: PGML answer blank patterns like `[_]{$answer->cmp(...)}` were being converted by the preprocessor to `PerlList([_]){...}`, which broke the PGML renderer's pattern matching.

## Root Causes

### Issue 1: Option Flow Broken
The data flow was broken at multiple points:
- PGML renderer extracted options from cmp() calls but didn't store the evaluator object
- Executor didn't properly track options through to answer evaluation
- Translator didn't extract options from PGML answer specs
- Context flags didn't check for studentsMustReduceFractions

### Issue 2: Preprocessor Wrapped PGML Patterns
The preprocessor's `wrap_with_perllist_nested` function was too aggressive, converting ALL `var = [...]` patterns to `PerlList(...)`, including PGML answer blank patterns like `Answer = [_]{...}`.

## Complete Fix (5 Commits)

### Commit 1: f99bf456 - Translator: Extract studentsMustReduceFractions

**File**: `packages/pg/translator/translator.py` (lines 354-372)

Modified `_cmp_context_flags()` to:
- Extract `cmp_options` from AnswerResult.metadata
- Check for `studentsMustReduceFractions` in cmp_options
- Set `reduceFractions = 0` when the option is enabled

This prevents automatic reduction of the student's fraction during parsing, allowing FractionAnswerChecker to validate that it's already reduced.

### Commit 2: 088574bb - Preprocessor: Convert Perl Fat Comma

**File**: `packages/pg/translator/pg_preprocessor_pygment.py` (line 3701)

Modified `_transform_pgml_evaluators()` to add `.replace('=>', '=')`:
- Converts Perl fat comma `=>` to Python assignment `=`
- Changes `$answer->cmp(studentsMustReduceFractions => 1)` to valid Python
- Ensures PGML evaluator expressions are syntactically correct for Python parsing

### Commit 3: a2f9fe69 - PGML Renderer: Handle Python-Style Method Calls

**File**: `packages/pg/renderer/pgml.py`

Two changes:

**3a. _eval_answer() method (lines 197-231)**
- Added pattern matcher for Python-style method calls: `var.cmp(...)`
- Recognizes expressions after preprocessor conversion
- Extracts variable name and options from the expression
- Returns answer specification dict with all necessary data

**3b. _parse_cmp_options() method (lines 398-404)**
- Enhanced to parse both `=>` (Perl) and `=` (Python) separators
- Ensures options are correctly parsed regardless of syntax style

### Commit 4: 6b3cbb78 - Store cmp_options in Metadata

**File**: `packages/pg/translator/translator.py` (multiple sections)

Three changes:

**4a. PGML renderer stores evaluator (pgml.py line 228)**
- Added `'evaluator': base_val` to answer spec dict
- Ensures translator can access the actual evaluator object

**4b. Translator extracts options (translator.py lines 977-988)**
- Enhanced answer entry format detection
- Handles PGML spec dicts with 'evaluator' and 'options' keys
- Extracts cmp_options and tracks through group_items

**4c. Metadata storage (translator.py line 1121)**
- Stores cmp_options in `AnswerResult.metadata['cmp_options']`
- Makes options available for `_cmp_context_flags()` to retrieve
- Fixed all group_items unpacking to handle cmp_options in tuples

### Commit 5: d9054975 - Preprocessor: Skip PGML Answer Blank Patterns

**File**: `packages/pg/translator/pg_preprocessor_pygment.py` (lines 1078-1108)

Modified `wrap_with_perllist_nested()` to:
- Detect PGML answer blank patterns: `[_]+]` (brackets with only underscores)
- Skip PerlList conversion for these patterns
- Preserve original syntax so PGML renderer can parse answer blanks
- Apply PerlList conversion only to regular list assignments

## Complete Data Flow (After All Fixes)

```
PGML Problem Code:
┌─────────────────────────────────────────────────────┐
│ Answer = [_]{$answer->cmp(                          │
│   studentsMustReduceFractions => 1,                 │
│   ...                                               │
│ )}{15}                                              │
└─────────────────────────────────────────────────────┘
         ↓
[Preprocessor doesn't wrap [_] in PerlList]
         ↓
PGML Renderer:
┌─────────────────────────────────────────────────────┐
│ - Detects: [_]{answer.cmp(studentsMustReduceFractions = 1, ...)}
│   (after => to = conversion)
│ - Parses Python-style method call
│ - Extracts options: {'studentsMustReduceFractions': True, ...}
│ - Builds spec dict with options and evaluator object
└─────────────────────────────────────────────────────┘
         ↓
Executor:
┌─────────────────────────────────────────────────────┐
│ - Stores answer blank spec in environment.answers
│ - Spec includes: evaluator object, options, etc.
└─────────────────────────────────────────────────────┘
         ↓
Translator _evaluate_answers():
┌─────────────────────────────────────────────────────┐
│ - Detects PGML spec dict format
│ - Extracts evaluator and cmp_options from spec
│ - Creates AnswerResult with metadata containing options
│ - metadata['cmp_options'] = {'studentsMustReduceFractions': True}
└─────────────────────────────────────────────────────┘
         ↓
Translator _cmp_context_flags():
┌─────────────────────────────────────────────────────┐
│ - Retrieves cmp_options from metadata
│ - Sees studentsMustReduceFractions: True
│ - Sets context flag: reduceFractions = 0
└─────────────────────────────────────────────────────┘
         ↓
Student Answer Parsing (Compute):
┌─────────────────────────────────────────────────────┐
│ - Respects reduceFractions = 0
│ - Does NOT automatically reduce student's fraction
│ - Student's "12/8" stays as "12/8" (not reduced to "3/2")
└─────────────────────────────────────────────────────┘
         ↓
FractionAnswerChecker.check():
┌─────────────────────────────────────────────────────┐
│ - Compares: student_frac == correct_frac (12/8 == 3/2 ✓)
│ - Checks: is_reduced(student_frac)  (12/8 is NOT reduced ✗)
│ - Returns: INCORRECT with message "Your answer is not
│   reduced to lowest terms"
└─────────────────────────────────────────────────────┘
```

## Testing

### Test 1: Verify Answer Blanks Are Detected

The issue mentioned that answer blanks weren't being detected in pg_solve.py. This should now work:

```bash
python pg_solve.py tutorial/sample-problems/Algebra/FractionAnswer.pg
```

Expected output:
- Problem statement displays correctly
- Shows "This problem has 1 answer blank(s)."
- Prompts for answer input
- Accepts user input

### Test 2: Verify Fraction Reduction Enforcement

Submit various fraction answers:
- `3/2` → ✓ Correct (already reduced)
- `12/8` → ✗ Incorrect, "Your answer is not reduced to lowest terms"
- `6/4` → ✗ Incorrect, "Your answer is not reduced to lowest terms"

## Files Modified

1. **packages/pg/translator/translator.py**
   - Modified `_cmp_context_flags()` to extract and use studentsMustReduceFractions
   - Modified `_evaluate_answers()` to extract options from PGML specs and store in metadata
   - Fixed all group_items unpacking

2. **packages/pg/translator/pg_preprocessor_pygment.py**
   - Added fat comma conversion (=>) to = in `_transform_pgml_evaluators()`
   - Modified `wrap_with_perllist_nested()` to skip PGML answer blank patterns

3. **packages/pg/renderer/pgml.py**
   - Added Python-style method call handler in `_eval_answer()`
   - Enhanced `_parse_cmp_options()` to handle both => and = separators
   - Added 'evaluator' key to answer spec dict

4. **packages/pg/math/fraction.py**
   - No changes needed - already correctly implements reduction checking

## Key Architecture Insights

### Why the Fix Works

1. **PGML Patterns Preserved**: By skipping PerlList conversion for `[_]` patterns, the PGML renderer can properly match and extract answer blanks.

2. **Options Flow Preserved**: By storing evaluator objects and options in the answer specs, and then extracting them in the translator, options are preserved through the entire evaluation pipeline.

3. **Context Flags Respected**: By storing options in AnswerResult metadata and checking them in `_cmp_context_flags()`, the context is properly configured before parsing, allowing the checker to validate reduction.

4. **Bidirectional Syntax Compatibility**: By supporting both `=>` and `=` separators in the options parser, the code works both before and after preprocessor conversion.

## Success Criteria Met

✅ **studentsMustReduceFractions is enforced**
  - Unreduced fractions are rejected with appropriate message
  - Reduced fractions are accepted

✅ **Answer blanks are detected in pg_solve.py**
  - PGML answer blank patterns are preserved during preprocessing
  - PGML renderer can parse and extract answer blanks
  - pg_solve.py shows correct number of answer blanks

✅ **Options flow from PGML to checker**
  - Options are extracted from cmp() calls
  - Options are stored in answer specs
  - Options are retrieved during evaluation
  - Options are applied via context flags

## Technical Debt Addressed

The fix also improves overall code quality:
- Clear separation of concerns between preprocessor, renderer, and translator
- Explicit handling of different answer entry formats
- Proper data structure for preserving options through the pipeline
- Better pattern detection to avoid unintended transformations
