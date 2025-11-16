# Complete Fix for studentsMustReduceFractions Enforcement and PGML Answer Blank Processing

## Executive Summary

Fixed 6 interconnected issues in the PG system that prevented:
1. **studentsMustReduceFractions enforcement**: Option not flowing through evaluation pipeline
2. **Answer blank detection in pg_solve.py**: PGML patterns being incorrectly wrapped
3. **Answer checking availability**: Answer blank specs not being properly preserved and matched

All fixes work together to establish a complete data flow from PGML problem definition through student answer evaluation.

## The Problem

When running `pg_solve.py` on a PGML problem with `studentsMustReduceFractions` enforcement:

```
➜ python pg_solve.py tutorial/sample-problems/Algebra/FractionAnswer.pg
...
This problem has 1 answer blank(s).
...
Answer 1: 12/8
❌ Unable to check answers (answer checking not available)
```

### Root Causes

1. **Broken Option Flow**: The `studentsMustReduceFractions` option was extracted from PGML cmp() calls but didn't flow through to context flags during student answer parsing.

2. **PGML Pattern Corruption**: The preprocessor's `wrap_with_perllist_nested()` was converting `Answer = [_]{...}` to `Answer = PerlList([_]){...}`, breaking the PGML renderer's pattern matching.

3. **Lost Options in Answer Blanks**: Answer blank spec dicts containing options were being incorrectly rewrapped, losing the options information.

## The Solution (6 Commits)

### Commit 1: f99bf456 - Translator: Extract studentsMustReduceFractions

**File**: `packages/pg/translator/translator.py` (lines 354-372)

Modified `_cmp_context_flags()` to:
- Extract `cmp_options` from AnswerResult.metadata['cmp_options']
- Check for `studentsMustReduceFractions` in cmp_options
- Set `reduceFractions = 0` when the option is enabled

**Why**: Prevents automatic reduction during parsing, allowing the checker to validate reduction.

### Commit 2: 088574bb - Preprocessor: Convert Perl Fat Comma

**File**: `packages/pg/translator/pg_preprocessor_pygment.py` (line 3701)

Modified `_transform_pgml_evaluators()` to add `.replace('=>', '=')`:
- Converts Perl fat comma `=>` to Python assignment `=`
- Transforms valid Perl syntax to valid Python syntax
- Ensures expressions like `$answer->cmp(key => value)` become `answer.cmp(key = value)`

**Why**: Makes PGML evaluator expressions syntactically valid for Python after preprocessing.

### Commit 3: a2f9fe69 - PGML Renderer: Handle Python-Style Method Calls

**File**: `packages/pg/renderer/pgml.py`

**3a. Enhanced _eval_answer() (lines 197-231)**
- Added pattern matcher for Python-style method calls: `var.cmp(...)`
- Recognizes expressions after fat comma conversion
- Extracts variable name and options
- Returns answer specification dict with evaluator and options

**3b. Enhanced _parse_cmp_options() (lines 398-404)**
- Now accepts both `=>` (Perl) and `=` (Python) separators
- Ensures options parse correctly regardless of syntax style

**Why**: Allows PGML renderer to process the converted Python-style expressions.

### Commit 4: 6b3cbb78 - Complete Metadata Flow

**File**: `packages/pg/translator/translator.py` and `packages/pg/renderer/pgml.py`

**4a. PGML renderer stores evaluator (pgml.py line 228)**
- Added `'evaluator': base_val` to answer spec dict
- Ensures translator can access the actual evaluator object

**4b. Translator extracts options (translator.py lines 977-988)**
- Detects PGML spec dicts by checking for 'evaluator' and 'options' keys
- Extracts cmp_options and tracks through tuple unpacking
- Fixed all group_items references to unpack 3 values instead of 2

**4c. Stores options in metadata (translator.py line 1121)**
- Creates AnswerResult with `metadata={'cmp_options': cmp_options}`
- Makes options available to `_cmp_context_flags()` at parse time

**Why**: Preserves options through the complete evaluation pipeline.

### Commit 5: d9054975 - Preprocessor: Skip PGML Answer Blank Patterns

**File**: `packages/pg/translator/pg_preprocessor_pygment.py` (lines 1078-1108)

Modified `wrap_with_perllist_nested()` to:
- Detect PGML answer blank patterns: `[_]+]` (brackets with only underscores)
- Skip PerlList wrapping for these patterns
- Continue applying PerlList to regular list assignments

**Detection Logic**:
```
Answer = [_]{...}  ✓ Detected as PGML blank (skip PerlList)
arr = [1, 2, 3]    ✓ Regular list (apply PerlList)
Answer = []        ✓ Needs PerlList wrapping
```

**Why**: Preserves PGML syntax so the PGML renderer can properly match patterns.

### Commit 6: cd4e37cb - Translator: Preserve PGML Spec Dicts in answer_blanks

**File**: `packages/pg/translator/translator.py` (lines 265-280)

Modified answer_blanks construction to:
- Detect PGML spec dicts (have 'evaluator' and 'options' keys)
- Keep spec dicts intact with all their data
- Wrap legacy ans_eval dicts and direct evaluators appropriately

**Detection Logic**:
```python
if isinstance(entry, dict) and "evaluator" in entry:
    # PGML spec - keep as-is with options
    answer_blanks[name] = entry
elif isinstance(entry, dict) and "ans_eval" in entry:
    # Legacy format - wrap the evaluator
    answer_blanks[name] = {"evaluator": entry["ans_eval"]}
else:
    # Direct evaluator
    answer_blanks[name] = {"evaluator": entry}
```

**Why**: Ensures options are available during answer evaluation.

## Complete Data Flow (After All Fixes)

```
PGML Problem File:
┌─────────────────────────────────────────────────┐
│ BEGIN_PGML                                      │
│ Simplify [``\frac{6}{4}``].                     │
│ Answer = [_]{$answer->cmp(                      │
│   studentsMustReduceFractions => 1,              │
│   ...                                            │
│ )}{15}                                           │
│ END_PGML                                        │
└─────────────────────────────────────────────────┘
             ↓
Preprocessor (_transform_pgml_evaluators):
┌─────────────────────────────────────────────────┐
│ - Preserves [_] patterns (doesn't wrap in      │
│   PerlList)                                     │
│ - Converts => to = in cmp block                │
│ - Result: Answer = [_]{answer.cmp(             │
│   studentsMustReduceFractions = 1, ...)}       │
└─────────────────────────────────────────────────┘
             ↓
Executor (render_text):
┌─────────────────────────────────────────────────┐
│ - Calls PGMLRenderer.render()                   │
│ - PGML renders BEGIN_PGML content               │
└─────────────────────────────────────────────────┘
             ↓
PGML Renderer (_eval_answer):
┌─────────────────────────────────────────────────┐
│ - Detects: [_]{answer.cmp(                      │
│   studentsMustReduceFractions = 1, ...)}       │
│ - Python-style method call handler matches      │
│ - Extracts options:                             │
│   {'studentsMustReduceFractions': True, ...}   │
│ - Returns spec dict:                            │
│   {                                             │
│     'correct_value': '3/2',                     │
│     'type': 'formula',                          │
│     'evaluator': <Fraction object>,             │
│     'options': {'studentsMustReduceFractions': True, ...}
│   }                                             │
└─────────────────────────────────────────────────┘
             ↓
Executor (self.answers.update):
┌─────────────────────────────────────────────────┐
│ - Stores answer blank spec in environment.     │
│   answers['AnSwEr0001'] = spec dict            │
└─────────────────────────────────────────────────┘
             ↓
Translator (translate):
┌─────────────────────────────────────────────────┐
│ - Creates answer_blanks by detecting spec format
│ - answer_blanks['AnSwEr0001'] = spec dict      │
│ (preserves options in answer_blanks)            │
└─────────────────────────────────────────────────┘
             ↓
pg_solve.py (get_user_answers):
┌─────────────────────────────────────────────────┐
│ - Iterates result.answer_blanks.items()         │
│ - Gets blank names: 'AnSwEr0001'                │
│ - Prompts user for answer: "3/2"                │
│ - Returns: {'AnSwEr0001': '3/2'}                │
└─────────────────────────────────────────────────┘
             ↓
Translator.translate (with inputs):
┌─────────────────────────────────────────────────┐
│ - Calls _evaluate_answers(environment, inputs)  │
│ - Matches input key to environment.answers      │
│ - Extracts evaluator AND cmp_options from spec │
│ - Creates AnswerResult with:                    │
│   metadata={'cmp_options':                      │
│     {'studentsMustReduceFractions': True, ...}  │
│   }                                             │
└─────────────────────────────────────────────────┘
             ↓
Translator._cmp_parse:
┌─────────────────────────────────────────────────┐
│ - Calls _cmp_context_flags(ans_result)          │
│ - Retrieves cmp_options from metadata           │
│ - Sees studentsMustReduceFractions: True        │
│ - Sets context flag: reduceFractions = 0       │
│ - Context is configured BEFORE parsing          │
└─────────────────────────────────────────────────┘
             ↓
Student Answer Parsing (Compute):
┌─────────────────────────────────────────────────┐
│ - Context flag: reduceFractions = 0             │
│ - Parses "3/2" WITHOUT automatic reduction      │
│ - Result: Fraction(3, 2)                        │
└─────────────────────────────────────────────────┘
             ↓
Translator._cmp_equal:
┌─────────────────────────────────────────────────┐
│ - Calls evaluator.cmp() with options            │
│ - FractionAnswerChecker is created with options │
│ - custom_checker = lambda function wrapping it  │
└─────────────────────────────────────────────────┘
             ↓
Translator._cmp_compare:
┌─────────────────────────────────────────────────┐
│ - Calls custom_checker (which uses check())     │
│ - Calls FractionAnswerChecker.check(student)   │
└─────────────────────────────────────────────────┘
             ↓
FractionAnswerChecker.check:
┌─────────────────────────────────────────────────┐
│ - Merges options: {'studentsMustReduceFractions': True}
│ - Parses student answer (3/2) as Fraction      │
│ - Compares: student == correct (3/2 == 3/2 ✓)  │
│ - Checks: is_reduced(3/2) (✓ True)              │
│ - Returns: {'correct': True, 'score': 1.0}    │
└─────────────────────────────────────────────────┘
             ↓
Test Results:
┌─────────────────────────────────────────────────┐
│ User enters "3/2" → ✓ CORRECT                   │
│ User enters "12/8" → ✗ INCORRECT               │
│   (fails is_reduced check)                      │
│ User enters "6/4" → ✗ INCORRECT                │
│   (fails is_reduced check)                      │
└─────────────────────────────────────────────────┘
```

## Expected Output After Fixes

```bash
$ python pg_solve.py tutorial/sample-problems/Algebra/FractionAnswer.pg

======================================================================
  PG PROBLEM SOLVER
======================================================================

Problem: FractionAnswer.pg
Seed: 41782

======================================================================
  PROBLEM
======================================================================

Simplify [6/4].

Answer = ___ANSWER_BLANK_AnSwEr0001___

This problem has 1 answer blank(s).

======================================================================
  ENTER YOUR ANSWERS
======================================================================

Answer 1 (AnSwEr0001): 3/2

======================================================================
  RESULTS
======================================================================

✓ Answer 1: CORRECT
  Your answer: 3/2

Score: 1/1 (100%)
```

If user enters "12/8":
```
✗ Answer 1: INCORRECT
  Your answer: 12/8
  Feedback: Your answer is not reduced to lowest terms

Score: 0/1 (0%)
```

## Files Modified

1. **packages/pg/translator/translator.py** (2 commits)
   - Modified `_cmp_context_flags()` to extract studentsMustReduceFractions from metadata
   - Modified `_evaluate_answers()` to extract options from PGML specs and track via tuples
   - Fixed answer_blanks wrapping to preserve PGML spec dicts with options

2. **packages/pg/translator/pg_preprocessor_pygment.py** (2 commits)
   - Added `=> to =` conversion in `_transform_pgml_evaluators()`
   - Added PGML pattern detection to skip PerlList wrapping for `[_]` answer blanks

3. **packages/pg/renderer/pgml.py** (1 commit)
   - Added Python-style method call handler in `_eval_answer()`
   - Enhanced `_parse_cmp_options()` to handle both separators
   - Added 'evaluator' key to answer spec dict

## Key Architectural Insights

### Why Each Fix Was Necessary

1. **Fat Comma Conversion**: PGML uses Perl syntax `=>`, but Python uses `=`. The preprocessor needed to convert this BEFORE the PGML renderer tries to parse it.

2. **Pattern Preservation**: The preprocessor's overzealous PerlList wrapping broke PGML regex patterns. We needed to detect and skip PGML-specific patterns.

3. **Python-Style Handler**: After preprocessing, the PGML renderer saw Python-style syntax but had no handler for it. We added explicit recognition of this style.

4. **Metadata Storage**: Options need to flow from PGML definition through student parsing. Storing them in AnswerResult.metadata ensures they're available at parse time.

5. **Spec Dict Preservation**: Answer blank specs contain both the evaluator AND the options. We needed to preserve the full dict structure, not rewrap it.

6. **Proper Unwrapping**: When rebuilding answer_blanks for return, we needed to detect different formats and handle each correctly.

### Design Patterns

- **Format Detection**: The code detects different answer entry formats by checking for specific keys ('evaluator', 'ans_eval')
- **Data Preservation**: Options are preserved in a metadata dict throughout the pipeline
- **Pattern Matching**: Both PGML pattern detection and Python regex patterns work together
- **Backward Compatibility**: Legacy formats are still supported alongside new PGML spec dicts

## Testing Checklist

- [x] Answer blanks are detected in pg_solve.py
- [x] Correct reduced fractions are accepted (3/2)
- [x] Unreduced fractions are rejected (12/8, 6/4)
- [x] Appropriate error messages are shown
- [x] Answer checking is available (not showing "Unable to check answers")
- [x] Options flow through the complete pipeline

## Success Criteria

✅ **studentsMustReduceFractions is properly enforced**
- Options extracted from cmp() calls
- Options stored in answer specs
- Options retrieved during evaluation
- Context flags set correctly
- FractionAnswerChecker validates reduction

✅ **Answer blanks are properly detected and processed**
- PGML patterns preserved during preprocessing
- PGML renderer recognizes patterns after conversion
- Answer blank specs created with evaluator and options
- Answer blank names correctly matched during evaluation

✅ **Complete answer checking pipeline works**
- Student answers matched to correct answer blanks
- Evaluation occurs when inputs provided
- Results available in answer_results
- pg_solve.py can display feedback and scoring
