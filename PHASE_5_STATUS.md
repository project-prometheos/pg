# Phase 5: Problem Translator - Status Summary

**Date**: October 3, 2025
**Status**: 🔴 CRITICAL BLOCKER
**Progress**: 18/34 tests passing (53%)

---

## Quick Status

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Tests Passing** | 18/34 (53%) | 34/34 (100%) | 16 tests |
| **Lines Implemented** | ~690 | ~2,170 | ~1,500 lines |
| **Features Complete** | ~25% | 100% | 75% |
| **Blocker Status** | RestrictedPython compatibility | Working sandbox | **CRITICAL** |

---

## Current Implementation

✅ **What Works**:
- Basic preprocessing (BEGIN_TEXT, BEGIN_PGML, BEGIN_SOLUTION, BEGIN_HINT)
- RestrictedPython execution framework (with issues)
- Basic pipeline coordination
- ENDDOCUMENT trimming

⚠️ **Partial**:
- Preprocessing (missing BEGIN_TIKZ, escape sequences)
- Environment setup (basic dict, missing PGcore integration)
- Error handling (basic Python traceback, not PG-style)

❌ **Missing**:
- Safe execution (RestrictedPython broken)
- Full preprocessing (escape sequences, TIKZ blocks)
- Answer pipeline (name generation, PGanswergroup)
- Grading system (all graders)
- Post-processing (hooks, DOM manipulation)
- Eval functions (PG_restricted_eval, etc.)
- Unrestricted loading (PG.pl with full permissions)
- Error messages (PG_errorMessage style)

---

## Critical Blocker: RestrictedPython

**Problem**: RestrictedPython has fundamental compatibility issues with PG's requirements.

**Issues**:
1. ❌ Variables starting with `_` rejected (`_env`, `_block_`)
2. ❌ Missing guard functions (`_write_`, `_getattr_`, `_getitem_`, `_getiter_`)
3. ❌ Tests hanging when running full suite
4. ❌ Too strict security model for PG use case

**Impact**: Cannot execute .pg files reliably

**Options**:

### Option A: Fix RestrictedPython (3-5 days)
- Add all required guard functions
- Refactor all variable naming (no `_` prefix)
- Debug hanging tests
- Risk: May hit more incompatibilities

### Option B: Alternative Sandbox (3-5 days) ⭐ RECOMMENDED
- **PyPy sandbox**: Separate process isolation
- **codejail**: Used by edX, subprocess-based, battle-tested
- **pysandbox**: Lighter security model
- **subprocess isolation**: Run in separate Python process with timeout
- **Custom AST rewriting**: Modify AST before exec()

**Recommendation**: Evaluate **codejail** (edX uses it for similar sandboxing needs)

---

## Detailed Gaps vs Perl

See [PHASE_5_ANALYSIS.md](./PHASE_5_ANALYSIS.md) for line-by-line comparison.

**Key Missing Systems**:

1. **Safe Compartment** (Perl: Safe.pm + Opcode)
   - Cached compartment (200ms+ speedup)
   - Module pre-loading
   - Symbol sharing
   - Operation mask (permit/deny)

2. **Answer Pipeline** (Perl: PGcore.pm, lines 295-462)
   - ANS() - implicit answer registration
   - NAMED_ANS() - explicit answer registration
   - Answer name generation (AnSwEr0001, AnSwEr0002, ...)
   - PGanswergroup integration
   - Array answers (checkboxes/radios)

3. **Grading System** (Perl: Translator.pm, lines 986-1142)
   - std_problem_grader (all-or-nothing)
   - avg_problem_grader (weighted partial credit)
   - Custom grader support

4. **Error Handling** (Perl: Translator.pm, lines 533-586)
   - PG_errorMessage with traceback
   - File name resolution ((eval nnn) → actual files)
   - Parser/Value frame skipping
   - Path shortening ([TMPL], [WW], [PG])

5. **Unrestricted Loading** (Perl: Translator.pm, lines 346-392)
   - Load PG.pl with empty opset (full permissions)
   - Initialization subroutine pattern (_PG_init)
   - Macro caching

---

## Implementation Plan

### Week 1: Unblock Execution 🔴 CRITICAL
**Days 1-3**: Evaluate sandbox alternatives
- Research codejail, PyPy sandbox, subprocess isolation
- Implement proof-of-concept
- Benchmark performance

**Days 4-5**: Implement chosen solution
- Migrate from RestrictedPython
- Update tests
- **Goal**: 80%+ test pass rate

### Week 2: Core Pipeline
**Days 1-2**: Complete preprocessing
- BEGIN_TIKZ, BEGIN_LATEX_IMAGE
- Escape sequences (\ → \\, ~~ → \)
- Edge cases

**Days 3-5**: Environment & execution
- PGcore integration
- Multi-stage pipeline
- Signal handlers

### Week 3: Answer & Grading
**Days 1-4**: Answer pipeline
- Answer name generation
- ANS() / NAMED_ANS() implementation
- PGanswergroup integration
- process_answers()

**Days 5-7**: Grading system
- std_problem_grader
- avg_problem_grader
- Problem state management

### Week 4: Advanced Features
**Days 1-3**: Error handling
- PG_errorMessage implementation
- Traceback filtering
- Error display

**Days 4-5**: Unrestricted loading
- unrestricted_load() for PG.pl
- Initialization pattern
- Macro caching

**Days 6-7**: Post-processing
- Hook system
- DOM manipulation

### Week 5: Testing & Polish
**Days 1-5**: Testing & validation
- Fix all failing tests (100% pass rate)
- Integration tests with real .pg files
- Performance optimization
- Regression testing vs Perl

---

## Success Criteria

- [x] Comprehensive TODO list created → [PHASE_5_TODO.md](./PHASE_5_TODO.md)
- [x] Gap analysis complete → [PHASE_5_ANALYSIS.md](./PHASE_5_ANALYSIS.md)
- [ ] RestrictedPython blocker resolved
- [ ] 100% test pass rate (currently 53%)
- [ ] All preprocessing transformations working
- [ ] Answer pipeline fully integrated
- [ ] Grading system complete
- [ ] Error messages match Perl quality
- [ ] Performance within 2x of Perl
- [ ] Integration tests passing

---

## Next Immediate Action

**START HERE**:

```bash
# Step 1: Evaluate sandbox alternatives
cd packages/pg_translator

# Research codejail (used by edX)
# - GitHub: openedx/codejail
# - Purpose: Safe code execution in sandboxed subprocess
# - Features: AppArmor/SELinux integration, resource limits
# - Proven: Used in production by edX

# Alternative: subprocess isolation
# - Simpler: Run Python in subprocess with timeout
# - Resource limits: ulimit, timeout command
# - Less secure but may be sufficient

# Step 2: Implement proof-of-concept
# - Port one test to new sandbox
# - Benchmark performance
# - Verify security model

# Step 3: Make decision and implement
# Goal: 80%+ test pass rate by end of week
```

---

## Resources

📋 **Detailed TODO**: [PHASE_5_TODO.md](./PHASE_5_TODO.md) - Full implementation checklist

📊 **Gap Analysis**: [PHASE_5_ANALYSIS.md](./PHASE_5_ANALYSIS.md) - Line-by-line comparison with Perl

📁 **Source Code**:
- Python: `packages/pg_translator/`
- Perl: `lib/WeBWorK/PG/Translator.pm`, `lib/PGcore.pm`

---

## Timeline Estimate

- **Week 1**: Unblock execution (sandbox replacement) 🔴
- **Week 2**: Core pipeline (preprocessing, environment, execution)
- **Week 3**: Answer & grading
- **Week 4**: Advanced features (error handling, unrestricted load, post-processing)
- **Week 5**: Testing & validation

**Total**: 3-4 weeks to complete Phase 5

**Risk**: If sandbox replacement takes longer, could extend to 5-6 weeks
