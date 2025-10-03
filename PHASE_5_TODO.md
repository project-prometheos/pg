# Phase 5: Problem Translator - Complete TODO for 1:1 Parity

## Status: 18/34 tests passing (53%) - CRITICAL BLOCKER

## Executive Summary

Phase 5 (Problem Translator & Execution) is the **CRITICAL PATH** to achieving 1:1 parity with the Perl PG system. This is the execution engine that actually runs .pg files. Without this working perfectly, we cannot achieve parity.

### Current Implementation Status

✅ **Implemented (Partial)**:
- PGPreprocessor: BEGIN_TEXT/BEGIN_PGML expansion (150 lines)
- PGExecutor: Safe execution framework with RestrictedPython (380 lines)
- PGTranslator: Pipeline coordinator (160 lines)

❌ **Critical Issues**:
- RestrictedPython compatibility (variable naming restrictions)
- RestrictedPython security model too strict (tests hanging)
- Missing features from Perl implementation

## Perl Implementation Analysis

### WeBWorK::PG::Translator.pm (1,385 lines)

**Core Architecture:**
```perl
# Safe Compartment (Opcode-based sandboxing)
use Opcode;
use WWSafe;  # Custom Safe.pm wrapper

# Cached safe compartment for performance (standalone renderer)
my $safeCache = WWSafe->new if $ENV{MOJO_MODE};

# Translator workflow:
1. new()              - Create translator with WWSafe compartment
2. environment()      - Set problem environment
3. initialize()       - Share symbols to safe compartment
4. source_string()    - Load problem source
5. unrestricted_load()- Load PG.pl with full permissions
6. set_mask()         - Restrict allowed operations
7. translate()        - Main execution pipeline
8. process_answers()  - Evaluate student answers
9. grade_problem()    - Grade using problem grader
10. post_process_content() - Apply content hooks
```

**Key Features:**

1. **Safe Compartment System** (lines 52-122, 195-224)
   - Uses Perl's Safe.pm + Opcode for sandboxing
   - Cached compartment for performance (saves 200ms/render)
   - Module pre-loading into cache
   - Symbol sharing between main:: and Safe compartment

2. **Preprocessing** (lines 1348-1378)
   ```perl
   # BEGIN_TEXT → TEXT(EV3(<<'END_TEXT'));
   # \ → \\ (TeX compatibility)
   # ~~ → \ (Perl escape alternative)
   # ENDDOCUMENT trimming
   # BEGIN_PGML, BEGIN_SOLUTION, BEGIN_HINT, etc.
   ```

3. **Execution Pipeline** (lines 679-794)
   ```perl
   # Preprocessing
   $evalString = preprocess_code($source);

   # Evaluate in safe compartment
   ($PG_PROBLEM_TEXT_REF, $PG_HEADER_TEXT_REF, ...) = $safe->reval($evalString);

   # Error handling with PG_errorMessage
   # Postprocessing
   # Result packing
   ```

4. **Error Handling** (lines 533-586)
   - PG_errorMessage: Traceback with file name resolution
   - (eval nnn) → actual file names via $main::__files__
   - Parser/Value call skipping in stack trace
   - Path shortening ([TMPL], [WW], [PG])

5. **Answer Processing** (lines 848-977)
   - process_answers(): Evaluate all answer evaluators
   - Custom warn/die handlers during evaluation
   - Array answer handling (checkboxes/radios)
   - AnswerHash validation

6. **Grading** (lines 986-1142)
   - std_problem_grader: All-or-nothing
   - avg_problem_grader: Partial credit with weights
   - Custom grader support via rf_problem_grader

7. **Post-Processing** (lines 1165-1207)
   - Content post-processor hooks
   - Mojo::DOM manipulation (HTML modes)
   - TeX mode text processing

8. **Eval Functions** (lines 1209-1346)
   - PG_restricted_eval: General code evaluation
   - PG_macro_file_eval: Load macro files with strict
   - PG_answer_eval: Answer evaluator execution

9. **Security** (lines 489-502)
   ```perl
   # Allowed: time, atan2, sin, cos, exp, log, sqrt, :default
   # Denied: entereval, unlink, symlink, system, exec, print, require
   ```

### PGcore.pm (785 lines)

**Core Object:**
```perl
# PGcore holds problem state during execution
{
    OUTPUT_ARRAY      => [],  # Body text
    HEADER_ARRAY      => [],  # Header text
    POST_HEADER_ARRAY => [],  # Post-header text
    PG_ANSWERS_HASH   => {},  # Answer evaluators (Tie::IxHash for order)
    PG_random_generator => PGrandom,
    PG_alias          => PGalias,
    flags             => { showPartialCorrectAnswers, hintExists, ... },
    content_post_processors => [],
}
```

**Key Methods:**
1. TEXT() - Append to output array (lines 253-257)
2. HEADER_TEXT() - Append to header (lines 196-200)
3. ANS() - Register implicit answer evaluators (lines 351-363)
4. NAMED_ANS() - Register explicit answer evaluators (lines 295-329)
5. record_ans_name() - Create PGanswergroup (lines 418-441)
6. persistent_data() - Store/retrieve session data (lines 468-478)
7. insertGraph() - Write graph images (lines 562-582)
8. Message channels: debug_message(), warning_message() (lines 746-764)

## Detailed TODO List

### 1. Sandboxing Architecture [CRITICAL - BLOCKER]

**Problem**: RestrictedPython has compatibility issues
- Variables starting with `_` not allowed
- Missing guard functions (_write_, _getattr_, etc.)
- Tests hanging when running full suite
- Too strict security model

**Options**:

#### Option A: Fix RestrictedPython Integration
- [ ] Add all required guard functions
  - [ ] `_write_` - Allow variable assignments
  - [ ] `_getattr_` - Safer attribute access
  - [ ] `_getitem_` - Safer item access
  - [ ] `_getiter_` - Safer iteration
  - [ ] `_print_` - Allow print statements
- [ ] Refactor variable naming throughout
  - [x] `_env` → `pg_env` (DONE)
  - [x] `_block_` → `pg_block_` (DONE)
  - [ ] Check for other underscore-prefixed variables
- [ ] Debug test hanging issues
  - [ ] Add timeout protection
  - [ ] Isolate problematic test cases
  - [ ] Review RestrictedPython compilation errors
- [ ] Performance testing
  - [ ] Benchmark vs Perl Safe.pm
  - [ ] Optimize compilation caching

**Estimated**: 2-3 days

#### Option B: Alternative Sandboxing (RECOMMENDED)
- [ ] Evaluate alternatives to RestrictedPython:
  1. **PyPy sandbox** - Separate process isolation
  2. **codejail** - Used by edX, subprocess-based
  3. **pysandbox** - Lighter security model
  4. **Custom AST rewriting** - Modify AST before exec()
  5. **subprocess isolation** - Run in separate Python process
- [ ] Implement chosen solution
- [ ] Migrate existing tests
- [ ] Performance benchmarking

**Estimated**: 3-5 days

### 2. Preprocessing Completeness [HIGH PRIORITY]

**Current**: Basic BEGIN_TEXT/BEGIN_PGML expansion
**Missing**: Full Perl preprocessing parity

- [ ] Implement all block transformations
  - [x] BEGIN_TEXT → TEXT(EV3(<<'END_TEXT')) (DONE)
  - [x] BEGIN_PGML → TEXT(PGML::Format2(<<'END_PGML')) (DONE)
  - [x] BEGIN_SOLUTION → SOLUTION(EV3(<<'END_SOLUTION')) (DONE)
  - [x] BEGIN_HINT → HINT(EV3(<<'END_HINT')) (DONE)
  - [ ] BEGIN_TIKZ → $obj->tex(<<END_TIKZ)
  - [ ] BEGIN_LATEX_IMAGE → $obj->tex(<<END_LATEX_IMAGE)
  - [ ] Other BEGIN_* blocks from legacy .pg files

- [ ] Escape sequence handling
  - [ ] `\` → `\\` (TeX compatibility)
  - [ ] `~~` → `\` (Perl escape alternative)
  - [ ] Verify in all contexts (strings, heredocs, etc.)

- [ ] ENDDOCUMENT handling
  - [ ] Strip everything after ENDDOCUMENT()
  - [ ] Handle ENDDOCUMENT variations (with/without parens)

- [ ] Whitespace normalization
  - [ ] `\r\n` → `\n`
  - [ ] Trim whitespace around block markers
  - [ ] END_TEXT;; → END_TEXT (handle extra semicolons)

**Test Coverage**: Need tests for each transformation

**Estimated**: 1-2 days

### 3. Environment & Initialization [MEDIUM PRIORITY]

**Current**: Basic environment dict
**Missing**: Full PGcore integration

- [ ] PGEnvironment class enhancements
  - [ ] Add PGrandom integration (seed-based RNG)
  - [ ] Add PGalias integration (file aliasing)
  - [ ] Add content_post_processors list
  - [ ] Add flags dict (showPartialCorrectAnswers, etc.)
  - [ ] Add message channels (WARNING_messages, DEBUG_messages)

- [ ] Symbol sharing mechanism
  - [ ] Share %envir to execution context
  - [ ] Share preprocess function ($PREPROCESS_CODE)
  - [ ] Share translator methods (PG_restricted_eval, etc.)

- [ ] Module pre-loading
  - [ ] Load core modules into context
  - [ ] Cache compiled modules for performance
  - [ ] Share module symbols to safe compartment

**Estimated**: 2-3 days

### 4. Execution Pipeline [MEDIUM PRIORITY]

**Current**: Basic execute() with RestrictedPython
**Missing**: Full pipeline parity

- [ ] Multi-stage execution
  - [ ] Stage 1: Preprocess source
  - [ ] Stage 2: Add BEGIN block for __files__ tracking
  - [ ] Stage 3: Compile with sandbox
  - [ ] Stage 4: Execute and capture results
  - [ ] Stage 5: Extract PGcore results

- [ ] Result extraction
  - [ ] PG_PROBLEM_TEXT_REF
  - [ ] PG_HEADER_TEXT_REF
  - [ ] PG_POST_HEADER_TEXT_REF
  - [ ] PG_ANSWER_HASH_REF
  - [ ] PG_FLAGS_REF
  - [ ] PGcore object

- [ ] Signal handler integration
  - [ ] __WARN__ handler with PG_errorMessage
  - [ ] __DIE__ handler with traceback
  - [ ] Frontend vs backend warnings separation

**Estimated**: 2-3 days

### 5. Error Handling & Debugging [MEDIUM PRIORITY]

**Current**: Basic Python traceback
**Missing**: PG-style error messages

- [ ] PG_errorMessage implementation
  - [ ] File name resolution ((eval nnn) → actual files)
  - [ ] Traceback with frame filtering
  - [ ] Skip Parser/Value frames
  - [ ] Path shortening ([TMPL], [WW], [PG])
  - [ ] Line number correction

- [ ] Error display
  - [ ] Error rendering in problem text
  - [ ] Source code display with line numbers
  - [ ] XML entity escaping for display
  - [ ] Conditional display based on permissions

- [ ] Warning/debug channels
  - [ ] Separate frontend/backend warnings
  - [ ] DEBUG_MESSAGE() support
  - [ ] WARN_MESSAGE() support
  - [ ] Message collection and display

**Estimated**: 2-3 days

### 6. Answer Integration [HIGH PRIORITY]

**Current**: Basic answer checking via Phase 3
**Missing**: Full answer pipeline

- [ ] Answer name generation
  - [ ] ANSWER_PREFIX system (AnSwEr0001, etc.)
  - [ ] QUIZ_PREFIX support
  - [ ] Implicit vs explicit naming
  - [ ] Answer name stack

- [ ] PGanswergroup integration
  - [ ] Create from pg_answer package
  - [ ] Tie::IxHash ordering preservation
  - [ ] Response group handling
  - [ ] Array answer support (checkboxes/radios)

- [ ] Answer evaluation
  - [ ] process_answers() implementation
  - [ ] Evaluator validation (AnswerEvaluator type check)
  - [ ] Error handling during evaluation
  - [ ] Answer hash result validation

- [ ] Answer persistence
  - [ ] rh_correct_answers storage
  - [ ] rh_student_answers tracking
  - [ ] rh_evaluated_answers results

**Estimated**: 3-4 days

### 7. Grading System [MEDIUM PRIORITY]

**Current**: Basic grading via Phase 3
**Missing**: Full grader framework

- [ ] Problem grader registry
  - [ ] std_problem_grader (all-or-nothing)
  - [ ] avg_problem_grader (partial credit)
  - [ ] Custom grader support
  - [ ] Grader installation (install_problem_grader)

- [ ] Grading execution
  - [ ] grade_problem() implementation
  - [ ] Problem state management
  - [ ] Score calculation
  - [ ] Message generation

- [ ] Credit system
  - [ ] Answer weights
  - [ ] Optional answers (credit array)
  - [ ] Blank answer handling for optional fields

**Estimated**: 2-3 days

### 8. Post-Processing [LOW PRIORITY]

**Current**: Not implemented
**Missing**: Content hooks

- [ ] Hook system
  - [ ] add_content_post_processor()
  - [ ] Hook execution order preservation
  - [ ] Hook parameters (DOM/text based on mode)

- [ ] TeX mode
  - [ ] Text string modification
  - [ ] Pass PG_PROBLEM_TEXT_REF to hooks

- [ ] HTML modes
  - [ ] Parse with HTML parser (BeautifulSoup4 instead of Mojo::DOM)
  - [ ] Pass DOM objects to hooks
  - [ ] Serialize back to strings
  - [ ] PTX mode (XML) support

**Estimated**: 1-2 days

### 9. Macro Loading [MEDIUM PRIORITY]

**Current**: Basic loadMacros via Phase 6
**Missing**: Unrestricted loading

- [ ] Unrestricted load mechanism
  - [ ] unrestricted_load() for PG.pl
  - [ ] Execute with empty opset (full permissions)
  - [ ] Initialization subroutine pattern (_PG_init)
  - [ ] Macro caching for performance

- [ ] loadMacros() integration
  - [ ] Call from within problems
  - [ ] Module search path
  - [ ] Error handling for missing files
  - [ ] Macro file evaluation (PG_macro_file_eval)

- [ ] Module sharing
  - [ ] Share loaded modules to safe compartment
  - [ ] Symbol export handling
  - [ ] Package namespace management

**Estimated**: 2-3 days

### 10. Performance Optimization [LOW PRIORITY]

**Current**: No caching
**Missing**: Perl-level performance

- [ ] Safe compartment caching
  - [ ] Cache compiled compartment
  - [ ] Module pre-loading
  - [ ] Initialization subroutine caching
  - [ ] 200ms+ performance gain (per Perl comments)

- [ ] Source compilation caching
  - [ ] Cache compiled code objects
  - [ ] Invalidation on source change
  - [ ] Cache key generation (file path + mtime)

- [ ] Benchmark suite
  - [ ] Time vs Perl implementation
  - [ ] Memory usage profiling
  - [ ] Identify bottlenecks

**Estimated**: 2-3 days

### 11. Testing & Validation [HIGH PRIORITY]

**Current**: 18/34 tests (53%)
**Target**: 100% test coverage

- [ ] Fix failing tests
  - [ ] Debug RestrictedPython hanging issues
  - [ ] Fix variable naming throughout
  - [ ] Add missing guard functions
  - [ ] Verify error handling

- [ ] Add missing test coverage
  - [ ] Preprocessing edge cases
  - [ ] Error scenarios
  - [ ] Answer evaluation edge cases
  - [ ] Grading scenarios
  - [ ] Multi-stage execution
  - [ ] Signal handler testing

- [ ] Integration tests
  - [ ] Real .pg file execution
  - [ ] Answer checking workflow
  - [ ] Grading workflow
  - [ ] Error display workflow

- [ ] Regression tests
  - [ ] Test against legacy Perl output
  - [ ] Exact output matching where possible
  - [ ] Semantic equivalence verification

**Estimated**: 3-5 days

## Implementation Priority Order

### Week 1: Critical Path (Sandboxing)
1. **[BLOCKER] Fix/Replace RestrictedPython** (Option A or B)
   - Days 1-3: Evaluate alternatives, make decision
   - Days 4-5: Implement chosen solution
   - Test: Get to 80%+ test pass rate

### Week 2: Core Functionality
2. **Complete Preprocessing** (1-2 days)
3. **Environment & Initialization** (2-3 days)
4. **Execution Pipeline** (2-3 days)

### Week 3: Answer & Grading
5. **Answer Integration** (3-4 days)
6. **Grading System** (2-3 days)

### Week 4: Polish & Performance
7. **Error Handling & Debugging** (2-3 days)
8. **Macro Loading** (2-3 days)
9. **Post-Processing** (1-2 days)
10. **Performance Optimization** (2-3 days)

### Week 5: Testing & Validation
11. **Testing & Validation** (5 days)
    - Fix all failing tests
    - Add comprehensive test coverage
    - Integration testing
    - Regression testing against Perl

## Success Criteria

- [ ] **100% test pass rate** (currently 53%)
- [ ] **All Perl preprocessing transformations** implemented
- [ ] **Safe execution** without compatibility issues
- [ ] **Answer evaluation** fully integrated
- [ ] **Grading system** complete with all graders
- [ ] **Error messages** match Perl format and quality
- [ ] **Performance** within 2x of Perl implementation
- [ ] **Integration tests** passing for real .pg files

## Risk Assessment

### HIGH RISK
- **RestrictedPython compatibility** - May need alternative solution
- **Safe execution performance** - Must be within acceptable range
- **Signal handler integration** - Complex Python/sandbox interaction

### MEDIUM RISK
- **Answer pipeline complexity** - Many moving parts
- **Error message parity** - Subtle formatting differences
- **Module loading** - Python import vs Perl require differences

### LOW RISK
- **Preprocessing** - Straightforward regex replacements
- **Post-processing** - Can defer if needed
- **Performance optimization** - Can iterate after core works

## Dependencies

**Blocks**:
- Phase 7 (Image & Graph Generation) - needs working translator
- Phase 8 (Integration & Testing) - needs working translator
- Full system integration - needs 1:1 parity

**Blocked By**:
- Phase 3 (Answer Evaluation) - ✅ COMPLETE
- Phase 4 (PGML) - ✅ COMPLETE
- Phase 6 (Macro System) - ✅ Phase 1 COMPLETE

## Next Immediate Action

**START HERE**: Fix/Replace RestrictedPython sandbox

```bash
# Option A: Fix RestrictedPython
cd packages/pg_translator
# Add guard functions, fix tests, debug hanging issues

# Option B: Evaluate alternatives
# Research: PyPy sandbox, codejail, pysandbox, subprocess isolation
# Implement proof-of-concept
# Migrate tests

# Goal: Get to 80%+ test pass rate within 3-5 days
```

## Notes

- This is the CRITICAL PATH to 1:1 parity
- Phase 5 is ~690 lines Python vs ~2,170 lines Perl
- Need to add ~1,500 lines to match Perl functionality
- Focus on correctness first, performance second
- Extensive testing against legacy Perl output required
