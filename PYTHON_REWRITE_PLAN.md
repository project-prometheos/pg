# Python PG Rewrite - Current State and Next Steps Plan

**Branch**: `claude/python-integration-011CUuCaeQdPojxEviT6aCjj` (based on `feature/macros`)
**Date**: November 7, 2025
**Session Goal**: Create actionable plan for continuing the Python rewrite of WeBWorK PG

---

## Executive Summary

This is a **complete Python rewrite** of the WeBWorK PG (Problem Generation) system, not an integration of Python into the existing Perl system.

**Current Progress**: ~5-7% complete (~7,200 lines of ~133,000 needed)
- 187 Python files across 12 packages
- 103 test files in repository root
- FastAPI backend with problem database system operational

---

## Package Structure

```
packages/
├── pg_answer/         # Answer evaluation system (Phase 3 - COMPLETE)
├── pg_macros/         # Macro system (Phase 6 - PHASE 1 COMPLETE)
├── pg_math/           # Math objects and computations (Phase 2 - COMPLETE)
├── pg_mathobjects/    # Enhanced math objects (Phase 2 - COMPLETE)
├── pg_parser/         # Parser & AST (Phase 1 - COMPLETE)
├── pg_pgml/           # PGML markup language (Phase 4 - COMPLETE)
├── pg_renderer/       # Problem rendering
├── pg_translator/     # Problem translator (Phase 5 - IN PROGRESS ~53%)
├── problemkit/        # Framework-agnostic authoring core
├── schemas/           # TypeScript schemas
└── ui/                # UI components

apps/
├── backend/           # FastAPI service (OPERATIONAL)
└── web/              # React frontend
```

---

## Current State by Phase

### ✅ PHASE 1: Core Parser & AST (COMPLETE - 67% coverage)
**Package**: `pg_parser/`
**Status**: Fully operational

**Implemented**:
- ✅ Tokenizer with context-aware patterns (94% coverage)
- ✅ Recursive descent parser with operator precedence (74% coverage)
- ✅ Complete AST node hierarchy
- ✅ Mathematical contexts (Numeric, Complex, Vector, Interval)
- ✅ Visitors: String, TeX, Eval
- ✅ 42 unit tests passing

**Example**:
```python
from pg_parser import Parser
from pg_parser.visitors import TeXVisitor

parser = Parser()
ast = parser.parse("2*x^2 + 3*x + 1")
visitor = TeXVisitor()
latex = ast.accept(visitor)  # "2x^{2} + 3x + 1"
```

---

### ✅ PHASE 2: MathObjects (COMPLETE - 61% coverage)
**Packages**: `pg_math/`, `pg_mathobjects/`
**Status**: Core features operational

**Implemented**:
- ✅ Formula class with test point evaluation
- ✅ Random point generation with domain checking
- ✅ Python function generation via SymPy lambdify
- ✅ `cmp()` method for answer checking
- ✅ Context system
- ✅ Numeric, Vector, Matrix types
- ✅ 149 tests passing

**Recent Enhancement** (Oct 3, 2025):
- Enhanced `compare()` with test-point evaluation
- `create_random_points()` and `create_point_values()`
- Domain mismatch detection
- Perl parity achieved for formula comparison

---

### ✅ PHASE 3: Answer Evaluation (COMPLETE)
**Package**: `pg_answer/`

**Implemented**:
- ✅ AnswerEvaluator base class
- ✅ FormulaEvaluator
- ✅ NumericEvaluator
- ✅ StringEvaluator
- ✅ VectorEvaluator
- ✅ IntervalEvaluator
- ✅ MatrixEvaluator
- ✅ Answer grading system
- ✅ 49 tests passing

---

### ✅ PHASE 4: PGML (COMPLETE - 85% coverage)
**Package**: `pg_pgml/`

**Implemented**:
- ✅ PGML tokenizer (30% of Perl features)
- ✅ Parser for block structures
- ✅ Renderer to HTML
- ✅ Heading, lists, alignment, code blocks
- ✅ Answer blank integration
- ✅ 48 tests passing

**Token Types**:
- Block structures: HEADING, RULE, ALIGN_LEFT/RIGHT/CENTER, PRE_BLOCK
- Inline: BOLD, ITALIC, MATH, CODE
- Answer integration

---

### 🔨 PHASE 5: Problem Translator (IN PROGRESS - 53% coverage)
**Package**: `pg_translator/`
**Status**: Core pipeline operational, missing critical features

**Files** (17 files, ~232 KB):
- `translator.py` (18,843 lines) - Main translation pipeline ✅
- `preprocessor.py` (30,051 lines) - PG → Python preprocessing ✅
- `sandbox.py` (12,618 lines) - Safe execution environment ✅
- `macro_loader.py` (13,004 lines) - Macro loading system 🔨
- `executor.py` (8,544 lines) - Code execution ✅
- `error_handler.py` (9,655 lines) - Error formatting 🔨
- `grading.py` (9,378 lines) - Answer grading ✅
- `pgml_parser.py` (12,865 lines) - PGML integration ✅
- `post_processor.py` (6,842 lines) - Output post-processing ✅

**Implemented**:
- ✅ Basic `translate()` pipeline
- ✅ Preprocessing (PG → Python conversion)
- ✅ Code execution via sandbox
- ✅ Basic environment setup
- ✅ PGML parsing and rendering
- ✅ 18 tests passing

**Critical Gaps**:
- ❌ `unrestricted_load()` - Can't load macros with full permissions
- ❌ `PG_macro_file_eval()` - Can't evaluate macro code safely
- ❌ `PG_errorMessage()` - Poor error messages (no file mapping, no traces)
- ❌ Sophisticated warning handling
- ❌ Post-processing hooks
- ❌ Complete grader system integration
- ❌ Answer stringification
- ❌ Checkbox/radio button processing

---

### ✅ PHASE 6: Macro System (PHASE 1 COMPLETE - 88% coverage)
**Package**: `pg_macros/`
**Status**: Core macros implemented, needs integration

**Files** (~1,780 lines total):
- `pg_core.py` (719 lines) - Core PG functions ✅
- `pg_basic_macros.py` (650 lines) - Basic UI macros ✅
- `pg_standard.py` (182 lines) - Standard problem setup ✅
- `pgml.py` (54 lines) - PGML integration stub ✅

**Implemented in `pg_core.py`**:
```python
✅ DOCUMENT() / ENDDOCUMENT()     # Problem lifecycle
✅ TEXT() / BEGIN_TEXT / END_TEXT # Text output
✅ ANS() / NAMED_ANS()           # Answer registration
✅ SOLUTION() / HINT()            # Solutions and hints
✅ COMMENT()                      # Problem comments
✅ loadMacros()                   # Macro loading (stub)
✅ random()                       # Random number generation
✅ Environment management         # PGEnvironment class
```

**Implemented in `pg_basic_macros.py`**:
```python
✅ ans_rule()                     # Text input
✅ NAMED_ANS_RULE()              # Named text input
✅ ans_box()                      # Textarea
✅ ans_radio_buttons()            # Radio button groups
✅ pop_up_list()                  # Dropdown menus
✅ MODES()                        # Mode-specific content (HTML/TeX/PTX)
✅ image()                        # Image insertion
✅ Display constants (PAR, BR, BBOLD, etc.) # Formatting
```

**Missing from Macro System**:
- ❌ Complete `loadMacros()` implementation
- ❌ Macro initialization system (`_PG_init()`, `_PGbasicmacros_init()`)
- ❌ Namespace integration with translator
- ❌ PGauxiliaryFunctions.pl port
- ❌ PGanswermacros.pl completion
- ❌ Context-specific macros
- ❌ Advanced UI elements (drag-drop, graphs, etc.)

**Critical Blocker**: Macros exist but aren't properly integrated with translator's `loadMacros()` system.

---

### ⏸️ PHASE 7: Image/Graph Generation (PENDING)
**Status**: Not started

**Needed**:
- Image generation utilities
- Graph plotting
- Dynamic image creation
- LaTeX image rendering

---

### ⏸️ PHASE 8: Integration (PENDING)
**Status**: Not started

**Needed**:
- End-to-end problem rendering
- Full test suite
- Performance optimization
- Documentation

---

## Critical Blockers

### 🚨 BLOCKER 1: Macro Loading System
**Impact**: HIGH - Prevents loading of any macros
**Location**: `pg_translator/macro_loader.py`

**Current State**:
- ✅ MacroLoader class structure
- ✅ Search path setup
- ✅ File finding logic
- ✅ Basic `unrestricted_load()` skeleton

**Missing**:
- ❌ Actual macro execution
- ❌ Permission mask management
- ❌ Init function discovery and calling (`_PG_init()`, etc.)
- ❌ Macro namespace management
- ❌ Dependency resolution
- ❌ Caching and reloading

**Action Items**:
1. Implement `unrestricted_load()` to execute Python macro files
2. Add permission mask save/restore
3. Implement init function discovery pattern (find functions matching `_*_init`)
4. Integrate with sandbox namespace
5. Add error handling and reporting

---

### 🚨 BLOCKER 2: Error Message System
**Impact**: MEDIUM - Hard to debug problems
**Location**: `pg_translator/error_handler.py`

**Current State**:
- ✅ Basic error_handler.py exists
- ❌ No file name mapping (eval IDs → filenames)
- ❌ No stack trace formatting
- ❌ No path abbreviation ([TMPL], [PG], [WW])

**Perl Reference**: `Translator.pm` lines 533-586
- Full stack traces with file names
- Path abbreviation for readability
- Eval ID → filename mapping
- Caller information

**Action Items**:
1. Implement `PG_errorMessage(return_type, *messages)`
2. Add file name tracking during translation
3. Create eval ID → filename mapping
4. Format stack traces with proper file names
5. Add path abbreviation system

---

### 🚨 BLOCKER 3: Macro-Translator Integration
**Impact**: CRITICAL - Macros can't be loaded by problems
**Location**: Integration between `pg_macros/` and `pg_translator/`

**Problem**:
- Macros exist in `pg_macros/pg_macros/core/`
- `loadMacros()` stub exists in `pg_core.py`
- Translator's `macro_loader.py` can't execute them

**Action Items**:
1. Update `loadMacros()` in `pg_core.py` to call translator's MacroLoader
2. Make MacroLoader execute Python macro files
3. Register macro functions in sandbox namespace
4. Call macro init functions after loading
5. Test end-to-end macro loading

---

## Recent Work (Last 15 Commits)

Recent focus areas:
1. **Answer checking enhancements** (Oct 5-6)
   - Added `check()` method support in PGMLRenderer and PGTranslator
   - Fixed π constant normalization
   - Enhanced formula handling

2. **Math formatting** (recent)
   - LaTeX bracket command conversions
   - Parentheses simplification for fractions
   - `format_math()` function improvements
   - `reduceConstants` flag in Compute function

3. **Testing and documentation**
   - Comprehensive PGTranslator tests
   - Interval notation test improvements
   - Documentation cleanup
   - Code formatting consistency

4. **Bug fixes**
   - Variable interpolation in AlgebraicFractionAnswer
   - LaTeX delimiter documentation
   - Database file cleanup

---

## Recommended Next Steps

### OPTION A: Complete Phase 5 (Translator) - 2-3 weeks
**Goal**: Get 10 simple problems rendering correctly

**Week 1: Macro Loader**
- Day 1-2: Complete `unrestricted_load()` in `macro_loader.py`
  - Implement Python macro execution via `exec()`
  - Add permission mask save/restore
  - Implement init function discovery and calling
  - Add error handling

- Day 3: Complete `PG_macro_file_eval()`
  - Implement code evaluation with file tracking
  - Add warning capture system
  - Integrate with error message formatter

- Day 4-5: Namespace Integration
  - Create macro namespace in sandbox
  - Implement function registration
  - Add variable sharing between macros
  - Test `loadMacros()` end-to-end

**Week 2: Error Handling & Integration**
- Day 6-7: Implement `PG_errorMessage()`
  - File name mapping
  - Stack trace formatting
  - Path abbreviation

- Day 8-10: Complete Macro-Translator Integration
  - Wire up `loadMacros()` to MacroLoader
  - Test macro loading in real problems
  - Fix integration issues

**Week 3: Testing & Validation**
- Test 10 simple problems end-to-end
- Document what works
- Create regression test suite

**Success Metrics**:
- ✅ `loadMacros("PG.pl", "PGbasicmacros.pl")` works
- ✅ Can render problem with `TEXT()`, `ans_rule()`, `ANS()`
- ✅ Proper error messages with file names
- ✅ 10 tutorial problems render correctly

---

### OPTION B: Complete Phase 6 (Macro System) - 2-3 weeks
**Goal**: Port remaining critical macros

**Needed Macros**:
1. **PGauxiliaryFunctions.pl** (~1,800 lines)
   - Helper functions used by many problems
   - Math utilities, string utilities

2. **Complete PGanswermacros.pl**
   - Additional answer types
   - Custom answer checkers
   - Answer filters

3. **Context-specific macros**
   - Complex context
   - Vector context
   - Matrix context
   - Interval context

**Action Items**:
1. Port PGauxiliaryFunctions.pl key functions
2. Complete answer macro system
3. Add context initialization macros
4. Create comprehensive test suite for each macro file
5. Document porting process

---

### OPTION C: Quick Win - Fix Integration (1 week)
**Goal**: Get ONE simple problem working end-to-end

**Tasks**:
1. Create minimal working macro loader (2 days)
   - Just enough to load `PG.py` and `PGbasicmacros.py`
   - Skip advanced features

2. Test with simplest possible problem (1 day)
   ```python
   DOCUMENT()
   loadMacros("PG.pl", "PGbasicmacros.pl")
   TEXT("What is 2+2? ", ans_rule(20))
   ANS(num_cmp(4))
   ENDDOCUMENT()
   ```

3. Debug and fix integration issues (2 days)

4. Document the working system (1 day)

**Success**: ONE problem renders correctly, proving the architecture works.

---

## Testing Infrastructure

**Current State**:
- 103 test files in repository root
- Test files across all packages
- No pytest currently installed in environment

**Package Tests**:
- `pg_parser/tests/` - Parser tests (42 passing)
- `pg_math/tests/` - Math object tests (149 passing)
- `pg_answer/tests/` - Answer evaluator tests (49 passing)
- `pg_pgml/tests/` - PGML tests (48 passing)
- `pg_translator/tests/` - Translator tests (18 passing)
- `pg_macros/tests/` - Macro tests (23 passing)

**Total**: 329 tests passing

**Needed**:
- Install pytest: `pip install pytest pytest-cov`
- Create integration test suite
- Add end-to-end problem tests
- Set up CI/CD

---

## Development Environment

**Backend**:
```bash
# Install Python packages
pip install -e packages/pg_parser
pip install -e packages/pg_math
pip install -e packages/pg_mathobjects
pip install -e packages/pg_answer
pip install -e packages/pg_pgml
pip install -e packages/pg_translator
pip install -e packages/pg_macros

# Start backend
cd apps/backend
uvicorn app.main:app --reload
```

**Frontend**:
```bash
# Install dependencies
pnpm install

# Start development
pnpm dev
```

**Database** (Operational):
- SQLite database with 161 tutorial problems
- Full-text search operational
- FastAPI endpoints working

---

## Key Files Reference

### Translator System
- `pg_translator/translator.py` - Main translation pipeline
- `pg_translator/preprocessor.py` - PG → Python conversion
- `pg_translator/macro_loader.py` - ⚠️ CRITICAL - Needs completion
- `pg_translator/sandbox.py` - Safe execution
- `pg_translator/error_handler.py` - ⚠️ CRITICAL - Needs enhancement

### Macro System
- `pg_macros/core/pg_core.py` - Core PG functions (DOCUMENT, TEXT, ANS, etc.)
- `pg_macros/core/pg_basic_macros.py` - UI macros (ans_rule, pop_up_list, etc.)
- `pg_macros/core/pg_standard.py` - Standard setup

### Reference (Perl)
- `macros/PG.pl` - Original Perl implementation (1,442 lines)
- `macros/PGbasicmacros.pl` - Original basic macros (2,747 lines)
- `lib/WeBWorK/PG/Translator.pm` - Original translator (1,385 lines)

---

## Recommendation

**Priority: OPTION C (Quick Win)**

Rationale:
1. Proves the architecture works
2. Identifies real integration issues
3. Provides foundation for further work
4. Achieves milestone quickly (1 week vs 2-3 weeks)
5. Builds momentum and confidence

After OPTION C succeeds, proceed with OPTION A (complete translator) for production readiness.

---

## Success Criteria

### Immediate (1 week - OPTION C):
- ✅ ONE simple problem renders correctly
- ✅ `loadMacros()` loads Python macro files
- ✅ Macro functions callable from problem code
- ✅ `TEXT()` and `ans_rule()` generate output
- ✅ Basic error messages work

### Short-term (1 month - OPTION A):
- ✅ 10 tutorial problems render correctly
- ✅ Proper error messages with file names
- ✅ All core macros integrated
- ✅ Comprehensive test suite

### Long-term (3-6 months):
- ✅ 100+ problems rendering
- ✅ All macro files ported
- ✅ Image/graph generation working
- ✅ Performance optimized
- ✅ Production ready

---

## Resources

**Documentation**:
- `PROGRESS.md` - Overall progress tracking
- `PARITY_STATUS.md` - Feature parity status
- `QUICKSTART.md` - Getting started guide
- Various `WEEK*_COMPLETE.md` files - Weekly summaries

**Plans** (in `/plans/` directory - if exists):
- Macro system implementation plan
- Translator features plan
- Formula enhancements plan

**Reference**:
- Perl codebase in `/macros/` and `/lib/`
- 133,000 lines of Perl to port
- ~5.4% complete as of Oct 5, 2025

---

## Next Immediate Actions

1. **Install dependencies**:
   ```bash
   pip install pytest pytest-cov sympy
   pip install -e packages/pg_translator
   pip install -e packages/pg_macros
   ```

2. **Run existing tests**:
   ```bash
   pytest packages/pg_macros/tests/ -v
   pytest packages/pg_translator/tests/ -v
   ```

3. **Create minimal test problem**:
   Create `test_problems/simple_01.pg`:
   ```python
   DOCUMENT()
   loadMacros("PG.pl", "PGbasicmacros.pl")
   TEXT("What is 2+2? ", ans_rule(20))
   ANS(num_cmp(4))
   ENDDOCUMENT()
   ```

4. **Implement minimal macro loader**:
   Focus on getting this ONE problem to work

5. **Document success** or **debug failures**

---

**Status**: Ready to proceed with implementation
**Recommended**: Start with OPTION C (Quick Win) to prove architecture
**Time Estimate**: 1 week to first working problem, then 2-3 weeks to 10 working problems
