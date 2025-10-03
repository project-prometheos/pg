# Phase 5: Problem Translator - Analysis & Gap Report

**Date**: October 3, 2025
**Status**: CRITICAL BLOCKER - 18/34 tests passing (53%)

---

## Executive Summary

Phase 5 (Problem Translator & Execution) is the **CRITICAL PATH** to achieving 1:1 parity with the Perl PG system. This phase implements the execution engine that actually runs .pg problem files. Without this working perfectly, we cannot achieve parity.

**Current Implementation**: ~690 lines Python
**Perl Implementation**: ~2,170 lines (Translator.pm + PGcore.pm)
**Gap**: ~1,500 lines needed

---

## Perl Implementation Analysis

### WeBWorK::PG::Translator.pm (1,385 lines)

#### Architecture Overview

```perl
# Core workflow
1. new()               - Create translator with WWSafe compartment
2. environment()       - Set problem environment hash
3. initialize()        - Share symbols to safe compartment
4. source_string()     - Load problem source
5. unrestricted_load() - Load PG.pl with full permissions (empty opset)
6. set_mask()          - Restrict allowed operations
7. translate()         - Main execution pipeline
8. process_answers()   - Evaluate student answers
9. grade_problem()     - Grade using problem grader
10. post_process_content() - Apply content hooks
11. stringify_answers() - Convert objects to strings
```

#### Key Systems

**1. Safe Compartment (lines 52-122, 195-224)**
- Uses Perl's `Safe.pm` + `Opcode` module for sandboxing
- Cached compartment saves 200ms per render (standalone mode)
- Module pre-loading into cache
- Symbol sharing between `main::` and safe compartment
- Operation mask: permit `time`, trig functions; deny `eval`, `system`, `exec`, `print`, `require`

**2. Preprocessing (lines 1348-1378)**
```perl
# Block transformations
BEGIN_TEXT    → TEXT(EV3(<<'END_TEXT'))
BEGIN_PGML    → STATEMENT(PGML::Format2(<<'END_PGML'))
BEGIN_SOLUTION → SOLUTION(EV3(<<'END_SOLUTION'))
BEGIN_HINT    → HINT(EV3(<<'END_HINT'))
BEGIN_TIKZ    → $obj->tex(<<END_TIKZ)

# Escape sequences
\  → \\  (TeX compatibility - backslash doubling)
~~ → \   (Perl escape alternative)

# Cleanup
ENDDOCUMENT.* → ENDDOCUMENT(); (strip after ENDDOCUMENT)
\r\n → \n (normalize line endings)
```

**3. Execution Pipeline (lines 679-794)**
```perl
# Preprocess source
$evalString = preprocess_code($source);

# Add file tracking
$evalString = 'BEGIN { ... $main::envir{__files__}{$eval} = "..." };' . $evalString;

# Evaluate in safe compartment
($PG_PROBLEM_TEXT_REF, $PG_HEADER_TEXT_REF, $PG_POST_HEADER_TEXT_REF,
 $PG_ANSWER_HASH_REF, $PG_FLAGS_REF, $PGcore) = $safe->reval($evalString);

# Error handling
$self->{errors} .= "ERRORS from evaluating PG file:\n$@\n" if $@;

# Postprocessing
$PG_PROBLEM_TEXT_REF = postprocess_code($PG_PROBLEM_TEXT_REF);

# Pack results
$self->{PG_PROBLEM_TEXT_REF} = \$PG_PROBLEM_TEXT;
$self->{PG_HEADER_TEXT_REF} = $PG_HEADER_TEXT_REF // \('');
...
```

**4. Error Handling (lines 533-586)**
- `PG_errorMessage()`: Traceback with file name resolution
- Replace `(eval nnn)` with actual file names via `$main::__files__`
- Skip Parser/Value frames in stack trace (act like built-ins)
- Path shortening: `$tmpl → [TMPL]`, `$root → [WW]`, `$pg → [PG]`
- Two modes: 'message' (just error), 'traceback' (full stack)

**5. Answer Processing (lines 848-977)**
```perl
# For each answer in PG_ANSWERS_HASH
for my $ans_name (keys %{ $PG->{PG_ANSWERS_HASH} }) {
    my $answergrp = $PG->{PG_ANSWERS_HASH}->{$ans_name};
    my $ans_eval = $answergrp->ans_eval;
    my $ans = $responsegrp->get_response($ans_name);

    # Handle arrays (checkboxes/radios)
    if (ref($ans) eq 'ARRAY') {
        $ans = [ map { $_->[0] } grep { $_->[1] eq 'CHECKED' } @$ans ];
    }

    # Evaluate
    $result = $safe->reval('$ans_eval->evaluate($ans, ans_label => "...")');

    # Store
    $self->{rh_evaluated_answers}->{$ans_name} = $result;
}
```

**6. Grading (lines 986-1142)**
```perl
# std_problem_grader: All-or-nothing
sub std_problem_grader {
    my $allCorrect = 1;
    for my $ans (keys %evaluated_answers) {
        $allCorrect = 0 unless $evaluated_answers{$ans}->{score} == 1;
    }
    $problem_result{score} = $allCorrect;
    ...
}

# avg_problem_grader: Weighted average
sub avg_problem_grader {
    my ($score, $total) = (0, 0);
    for my $ans (keys %answers) {
        my $weight = $answers->{$ans}{weight} // 1;
        $total += $weight;
        $score += $weight * $credit{$ans};
    }
    $problem_result{score} = $total ? $score / $total : 0;
    ...
}
```

**7. Post-Processing (lines 1165-1207)**
```perl
if ($self->{displayMode} eq 'TeX') {
    # TeX mode: pass text reference
    $safe->reval('for (@{ $main::PG->{content_post_processors} }) {
        $_->($PG_PROBLEM_TEXT_REF);
    }');
} else {
    # HTML mode: parse and pass DOM objects
    my $problemDOM = Mojo::DOM->new($PG_PROBLEM_TEXT);
    my $pageHeader = Mojo::DOM->new($PG_HEADER_TEXT);
    $safe->reval('for (@{ $main::PG->{content_post_processors} }) {
        $_->($problemDOM, $pageHeader, $problemResult);
    }');
    # Convert back
    $PG_PROBLEM_TEXT = $problemDOM->to_string;
}
```

**8. Eval Functions (lines 1209-1346)**
```perl
# PG_restricted_eval: General code evaluation
sub PG_restricted_eval {
    my $string = shift;
    local $SIG{__WARN__} = sub { ... PG_errorMessage ... };
    local $SIG{__DIE__} = 'DEFAULT';
    no strict;
    no warnings 'redefine';
    return eval("package main; $string");
}

# PG_macro_file_eval: Load macro files
sub PG_macro_file_eval {
    my ($string, $filePath) = @_;
    # Track file in __files__
    my ($out, $errors) = PG_macro_file_eval_helper(
        'package main; strict->import;' .
        'BEGIN { my $eval = __FILE__; $main::envir{__files__}{$eval} = "' . $filePath . '" };' .
        $string
    );
    ...
}

# PG_answer_eval: Answer evaluator execution
sub PG_answer_eval {
    my $string = shift;
    local $SIG{__WARN__} = sub { die(@_) };  # make warn die
    no strict;
    my $out = eval('package main;' . $string);
    ...
}
```

**9. Unrestricted Loading (lines 346-392)**
```perl
sub unrestricted_load {
    my $filePath = shift;  # e.g., PG.pl

    # Temporarily disable all restrictions
    my $store_mask = $safe->mask();
    $safe->mask(Opcode::empty_opset());  # Allow everything

    # Load file
    my $rdoResult = $safe->rdo($filePath);

    # Restore restrictions
    $safe->mask($store_mask);

    # Call initialization subroutine (_PG_init)
    my $init_sub = eval { \&{"${safe_pkg}::_PG_init"} };
    &$init_sub() if ref($init_sub) eq 'CODE';
    ...
}
```

### PGcore.pm (785 lines)

#### Core Object Structure

```perl
my $self = {
    OUTPUT_ARRAY      => [],  # Body text accumulator
    HEADER_ARRAY      => [],  # Header text accumulator
    POST_HEADER_ARRAY => [],  # Post-header text
    PG_ANSWERS_HASH   => {},  # Tie::IxHash for order

    # State
    answer_name_count => 0,
    implicit_named_answer_stack => [],
    implicit_answer_eval_stack  => [],
    explicit_answer_name_evals  => {},

    # Configuration
    ANSWER_PREFIX     => 'AnSwEr',
    QUIZ_PREFIX       => $envir->{QUIZ_PREFIX},

    # Subsystems
    PG_random_generator => PGrandom->new($seed),
    PG_alias          => PGalias->new($envir),
    PG_loadMacros     => PGloadfiles->new($envir),

    # Flags
    flags => {
        showPartialCorrectAnswers => 1,
        hintExists => 0,
        solutionExists => 0,
        ...
    },

    # Messages
    WARNING_messages => [],
    DEBUG_messages   => [],

    # Hooks
    content_post_processors => [],
};
```

#### Key Methods

**Text Accumulation**:
```perl
sub TEXT {
    push @{ $self->{OUTPUT_ARRAY} }, map { (defined($_)) ? $_ : '' } @_;
}

sub HEADER_TEXT {
    push @{ $self->{HEADER_ARRAY} }, map { (defined($_)) ? $_ : '' } @_;
}
```

**Answer Registration**:
```perl
sub ANS {
    # Implicit pairing with answer blanks
    while (@in) {
        if (my $label = shift @{ $self->{implicit_named_answer_stack} }) {
            $self->NAMED_ANS($label, shift @in);
        } else {
            push(@{ $self->{implicit_answer_eval_stack} }, shift @in);
        }
    }
}

sub NAMED_ANS {
    # Explicit pairing by name
    my ($label, $ans_eval) = @_;
    # Create PGanswergroup, associate evaluator
    ...
}

sub record_ans_name {
    # Called when answer blank created
    my ($self, $label, $value) = @_;
    my $response_group = new PGresponsegroup($label, $label, $value);

    if ($self->{explicit_answer_name_evals}{$label}) {
        # Explicit name: create answer group with evaluator
        $self->{PG_ANSWERS_HASH}{$label} = PGanswergroup->new(...);
        $self->NAMED_ANS($label, delete $self->{explicit_answer_name_evals}{$label});
    } elsif (my $evaluator = shift @{ $self->{implicit_answer_eval_stack} }) {
        # Implicit: pair with next evaluator from stack
        $self->{PG_ANSWERS_HASH}{$label} = PGanswergroup->new(...);
        $self->NAMED_ANS($label, $evaluator);
    } else {
        # No evaluator yet: create group, wait for ANS() call
        $self->{PG_ANSWERS_HASH}{$label} = PGanswergroup->new(...);
    }
    ...
}
```

**Message Channels**:
```perl
sub debug_message {
    push @{ $self->{DEBUG_messages} }, @str;
}

sub warning_message {
    push @{ $self->{WARNING_messages} }, @str;
}
```

**Graph Insertion**:
```perl
sub insertGraph {
    my ($self, $graph) = @_;
    my $fileName = $graph->imageName . '.' . $graph->ext;
    my $filePath = $self->surePathToTmpFile("images/$fileName");

    # Check if cached (by file mtime comparison)
    if (!-e $filePath || (stat $pgFile)[9] > (stat $filePath)[9] || ...) {
        my $graphData = $graph->draw;
        saveDataToFile($graphData, $filePath);
    }
    return $filePath;
}
```

---

## Python Implementation Status

### What We Have

**1. preprocessor.py** (150 statements)
```python
class PGPreprocessor:
    BLOCK_PATTERNS = {
        "TEXT": (r"BEGIN_TEXT\s*$", r"^END_TEXT"),
        "PGML": (r"BEGIN_PGML\s*$", r"^END_PGML"),
        "SOLUTION": (r"BEGIN_SOLUTION\s*$", r"^END_SOLUTION"),
        "HINT": (r"BEGIN_HINT\s*$", r"^END_HINT"),
        # Missing: TIKZ, LATEX_IMAGE
    }

    def preprocess(self, pg_source: str) -> PreprocessResult:
        # Process blocks
        # Missing: \ → \\, ~~ → \
```

**2. executor.py** (380 statements)
```python
class PGExecutor:
    def execute(self, code: str, seed: int, context: Context | None = None) -> PGEnvironment:
        # Build safe globals
        safe_builtins = self._build_safe_globals(env)

        # Compile with RestrictedPython
        byte_code = compile_restricted(code, filename="<pg>", mode="exec")

        # Execute
        globals_dict = {"__builtins__": safe_builtins, ...}
        exec(byte_code, globals_dict, locals_dict)

        # ISSUES:
        # - Variable naming (_env not allowed)
        # - Missing guards (_write_, _getattr_)
        # - Tests hanging
```

**3. translator.py** (160 statements)
```python
class PGTranslator:
    def translate(self, pg_file_path: str | Path, seed: int, ...) -> ProblemResult:
        # 1. Load .pg file
        # 2. Preprocess
        # 3. Execute in sandbox
        # 4. Render text (PGML → HTML)
        # 5. Collect answers
        # 6. Check answers (if inputs provided)
        # 7. Return result

        # Missing: Full pipeline, error handling, post-processing
```

### What We're Missing

#### 1. Sandboxing ❌ (CRITICAL)
**Perl**: Safe.pm + Opcode (mature, battle-tested)
**Python**: RestrictedPython (compatibility issues)

**Problems**:
- Variables starting with `_` rejected
- Missing guard functions
- Tests hanging
- Too strict for PG use case

**Options**:
1. Fix RestrictedPython (add guards, refactor)
2. Alternative: PyPy sandbox, codejail, subprocess
3. Custom AST rewriting

#### 2. Preprocessing ⚠️ (PARTIAL)
**Missing**:
- [ ] BEGIN_TIKZ, BEGIN_LATEX_IMAGE
- [ ] \ → \\ (TeX compatibility)
- [ ] ~~ → \ (Perl escape)
- [ ] Whitespace normalization edge cases

#### 3. Environment & Initialization ❌
**Missing**:
- [ ] PGrandom integration
- [ ] PGalias integration
- [ ] Symbol sharing mechanism
- [ ] Module pre-loading/caching
- [ ] Flags dict initialization

#### 4. Execution Pipeline ❌
**Missing**:
- [ ] Multi-stage execution
- [ ] BEGIN block for __files__ tracking
- [ ] Result extraction (PGcore object)
- [ ] Signal handler integration (__WARN__, __DIE__)

#### 5. Error Handling ❌
**Missing**:
- [ ] PG_errorMessage implementation
- [ ] File name resolution
- [ ] Traceback filtering
- [ ] Path shortening
- [ ] Error display in problem text
- [ ] Source code display with line numbers

#### 6. Answer Pipeline ❌
**Missing**:
- [ ] Answer name generation (AnSwEr0001)
- [ ] Implicit vs explicit naming stacks
- [ ] PGanswergroup integration
- [ ] Array answer handling
- [ ] process_answers() implementation

#### 7. Grading ❌
**Missing**:
- [ ] Problem grader registry
- [ ] std_problem_grader
- [ ] avg_problem_grader
- [ ] Custom grader support
- [ ] Problem state management

#### 8. Post-Processing ❌
**Missing**:
- [ ] Hook system (add_content_post_processor)
- [ ] TeX mode (text modification)
- [ ] HTML mode (DOM manipulation)

#### 9. Eval Functions ❌
**Missing**:
- [ ] PG_restricted_eval
- [ ] PG_macro_file_eval
- [ ] PG_answer_eval

#### 10. Unrestricted Loading ❌
**Missing**:
- [ ] unrestricted_load() for PG.pl
- [ ] Empty opset execution
- [ ] Initialization subroutine pattern
- [ ] Macro caching

---

## Gap Analysis Summary

| Feature | Perl | Python | Gap |
|---------|------|--------|-----|
| Safe Execution | ✅ Safe.pm + Opcode | ⚠️ RestrictedPython (broken) | **CRITICAL** |
| Preprocessing | ✅ Full | ⚠️ Partial | 70% |
| Environment | ✅ Full | ❌ Basic | 30% |
| Execution Pipeline | ✅ Multi-stage | ❌ Single-stage | 40% |
| Error Handling | ✅ PG_errorMessage | ❌ Basic traceback | 20% |
| Answer Pipeline | ✅ Full | ❌ None | 0% |
| Grading | ✅ 2 graders + custom | ❌ None | 0% |
| Post-Processing | ✅ Hooks + DOM | ❌ None | 0% |
| Eval Functions | ✅ 3 eval types | ❌ None | 0% |
| Unrestricted Load | ✅ Full | ❌ None | 0% |

**Overall Completion**: ~25% (mostly preprocessing + basic execution)

---

## Critical Path Forward

### Week 1: Unblock Execution (CRITICAL)
**Goal**: Fix/replace RestrictedPython, get to 80% test pass rate

**Option A**: Fix RestrictedPython
- Add all guard functions (_write_, _getattr_, etc.)
- Refactor variable naming
- Debug hanging tests
- Estimated: 3-5 days

**Option B**: Alternative Sandbox (RECOMMENDED)
- Evaluate: PyPy sandbox, codejail, subprocess isolation
- Implement proof-of-concept
- Migrate tests
- Estimated: 3-5 days

### Week 2: Core Pipeline
1. Complete preprocessing (1-2 days)
2. Environment & initialization (2-3 days)
3. Multi-stage execution pipeline (2-3 days)

### Week 3: Answer & Grading
4. Answer integration (3-4 days)
5. Grading system (2-3 days)

### Week 4: Advanced Features
6. Error handling (2-3 days)
7. Unrestricted loading (2-3 days)
8. Post-processing (1-2 days)

### Week 5: Testing & Validation
9. Fix all failing tests
10. Integration tests with real .pg files
11. Performance optimization

---

## Success Metrics

- [ ] **100% test pass rate** (currently 53%)
- [ ] **All preprocessing transformations** working
- [ ] **Safe execution** without issues
- [ ] **Answer pipeline** fully integrated
- [ ] **Grading** complete with all graders
- [ ] **Error messages** match Perl quality
- [ ] **Performance** within 2x of Perl
- [ ] **Integration tests** passing

---

## References

- **Detailed TODO**: [PHASE_5_TODO.md](./PHASE_5_TODO.md)
- **Perl Source**:
  - `lib/WeBWorK/PG/Translator.pm` (1,385 lines)
  - `lib/PGcore.pm` (785 lines)
- **Python Source**: `packages/pg_translator/`
