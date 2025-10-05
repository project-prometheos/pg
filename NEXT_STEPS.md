# Next Steps: Macro System Implementation
## Immediate Action Plan

**Date**: October 5, 2025
**Priority**: CRITICAL
**Estimated Time**: 4 weeks (1 developer) | 2 weeks (2 developers)

---

## 🎯 GOAL

**Get 10 simple PG problems rendering correctly by implementing core macro system.**

This unlocks everything else - without macros, nothing works.

---

## 📋 WEEK 1: Macro Loader (Days 1-5)

### Day 1-2: Complete unrestricted_load()

**File**: `packages/pg_translator/pg_translator/macro_loader.py`

**Tasks**:
1. ✅ Implement permission mask save/restore
2. ✅ Add Python macro execution via exec()
3. ✅ Implement init function discovery and calling
4. ✅ Add error handling and reporting

**Reference**: Translator.pm lines 346-392

**Test**: Load a simple Python macro with `_test_init()` function

### Day 3: PG_macro_file_eval()

**File**: `packages/pg_translator/pg_translator/macro_loader.py`

**Tasks**:
1. ✅ Implement code evaluation with file tracking
2. ✅ Add warning capture system
3. ✅ Integrate with error message formatter

**Reference**: Translator.pm lines 1253-1288

**Test**: Evaluate macro code with proper error reporting

### Day 4-5: Namespace Integration

**Files**:
- `packages/pg_translator/pg_translator/sandbox.py`
- `packages/pg_translator/pg_translator/environment.py`

**Tasks**:
1. ✅ Create macro namespace in sandbox
2. ✅ Implement function registration
3. ✅ Add variable sharing between macros
4. ✅ Test loadMacros() end-to-end

**Test**: Load multiple macros that depend on each other

---

## 📋 WEEK 2: PG.pl Core Functions (Days 6-10)

### Day 6-7: TEXT() and Friends

**File**: `packages/pg_macros/pg_macros/core/pg_core.py` (NEW)

**Implement**:
```python
def TEXT(*args: str) -> None:
    """Append text to problem output."""
    env = get_environment()
    env.append_text("".join(str(arg) for arg in args))

def BEGIN_TEXT() -> str:
    """Start text block."""
    return ""

def END_TEXT() -> str:
    """End text block."""
    return ""
```

**Reference**: PG.pl lines 400-600

**Test**:
```python
TEXT("Hello ", "world")
assert env.get_text() == "Hello world"
```

### Day 8: ANS() Functions

**File**: Same as above

**Implement**:
```python
def ANS(*evaluators: AnswerEvaluator) -> None:
    """Register answer evaluators."""
    env = get_environment()
    for evaluator in evaluators:
        answer_name = env.next_answer_name()
        env.register_answer(answer_name, evaluator)

def NAMED_ANS(name: str, evaluator: AnswerEvaluator) -> None:
    """Register named answer evaluator."""
    env = get_environment()
    env.register_answer(name, evaluator)
```

**Reference**: PG.pl lines 700-950

**Test**:
```python
from pg_answer import NumericEvaluator
ANS(NumericEvaluator(42))
assert len(env.answers) == 1
```

### Day 9: DOCUMENT/ENDDOCUMENT

**File**: Same as above

**Implement**:
```python
def DOCUMENT() -> None:
    """Start problem document."""
    env = get_environment()
    env.start_document()

def ENDDOCUMENT() -> None:
    """End problem document and finalize."""
    env = get_environment()
    env.end_document()

def SOLUTION(*args: str) -> None:
    """Add solution text."""
    env = get_environment()
    env.append_solution("".join(str(arg) for arg in args))

def HINT(*args: str) -> None:
    """Add hint text."""
    env = get_environment()
    env.append_hint("".join(str(arg) for arg in args))
```

**Reference**: PG.pl lines 1000-1400

**Test**: Complete problem workflow

### Day 10: loadMacros() Integration

**File**: `packages/pg_macros/pg_macros/core/pg_core.py`

**Implement**:
```python
def loadMacros(*macro_files: str) -> None:
    """Load macro files into problem namespace."""
    loader = get_macro_loader()
    for macro in macro_files:
        loader.load_macro(macro)

def _PG_init():
    """Initialize PG environment in sandbox."""
    # Register all PG functions
    sandbox = get_sandbox()
    sandbox.register_function("TEXT", TEXT)
    sandbox.register_function("BEGIN_TEXT", BEGIN_TEXT)
    sandbox.register_function("END_TEXT", END_TEXT)
    sandbox.register_function("ANS", ANS)
    # ... etc
```

**Reference**: PG.pl lines 1-200, 250-350

**Test**: Load PG.pl and call functions

---

## 📋 WEEK 3: PGbasicmacros.pl Essentials (Days 11-15)

### Day 11-12: Answer Blanks

**File**: `packages/pg_macros/pg_macros/core/pg_basic_macros.py` (NEW)

**Implement**:
```python
def ans_rule(width: int = 20) -> str:
    """Create answer blank."""
    env = get_environment()
    name = env.next_answer_name()
    return f'<input type="text" name="{name}" size="{width}" />'

def ans_radio_buttons(*options: tuple[str, str]) -> str:
    """Create radio button answer group."""
    # Implementation...

def pop_up_list(options: list | dict) -> str:
    """Create dropdown select."""
    # Implementation...
```

**Reference**: PGbasicmacros.pl lines 200-900

**Test**: Generate HTML input elements

### Day 13: Display Constants

**File**: Same as above

**Implement**:
```python
class DisplayConstants:
    """Display mode-specific constants."""

    @staticmethod
    def PAR(mode: str = "HTML") -> str:
        return {"HTML": "<p>", "TeX": "\\n\\n", "PTX": "<p>"}[mode]

    @staticmethod
    def BR(mode: str = "HTML") -> str:
        return {"HTML": "<br/>", "TeX": "\\\\", "PTX": "<br/>"}[mode]

    # ... 50+ more constants

def _PGbasicmacros_init():
    """Initialize basic macros in sandbox."""
    mode = get_display_mode()
    constants = DisplayConstants()
    for const_name in dir(constants):
        if const_name.isupper():
            value = getattr(constants, const_name)(mode)
            set_sandbox_var(const_name, value)
```

**Reference**: PGbasicmacros.pl lines 40-170

**Test**: Constants available in problem

### Day 14: MODES() and Helpers

**File**: Same as above

**Implement**:
```python
def MODES(*, HTML: str = "", TeX: str = "", PTX: str = "") -> str:
    """Mode-specific text."""
    mode = get_display_mode()
    return {"HTML": HTML, "TeX": TeX, "PTX": PTX}.get(mode, HTML)

def image(filename: str, width: int = None, height: int = None,
          tex_size: int = None, alt_text: str = "") -> str:
    """Insert image."""
    if get_display_mode() == "TeX":
        return f"\\includegraphics[width={tex_size}pt]{{{filename}}}"
    else:
        attrs = f'width="{width}"' if width else ""
        if height:
            attrs += f' height="{height}"'
        return f'<img src="{filename}" alt="{alt_text}" {attrs}/>'
```

**Reference**: PGbasicmacros.pl lines 1000-2500

**Test**: Mode-specific rendering

### Day 15: Integration & Testing

**Tasks**:
1. ✅ Create test problems using macros
2. ✅ Verify loadMacros() works
3. ✅ Test TEXT() + ANS() + ans_rule()
4. ✅ Fix any integration issues

**Test Problems**:
```python
# Problem 1: Basic text and answer
"""
DOCUMENT();
loadMacros("PG.pl", "PGbasicmacros.pl");

TEXT("What is 2+2?");
ANS(num_cmp(4));

ENDDOCUMENT();
"""

# Problem 2: With answer rule
"""
DOCUMENT();
loadMacros("PG.pl", "PGbasicmacros.pl");

BEGIN_TEXT
Enter a number: \\{ ans_rule(20) \\}
END_TEXT

ANS(num_cmp(42));

ENDDOCUMENT();
"""
```

---

## 📋 WEEK 4: Polish & Validation (Days 16-20)

### Day 16-17: Error Handling

**File**: `packages/pg_translator/pg_translator/error_handler.py` (NEW)

**Implement**:
```python
def PG_errorMessage(return_type: str = "traceback", *messages: str) -> str:
    """Format error messages with file name mapping and stack traces."""
    # Implementation per Plan 02, Phase 2.1
```

**Reference**: Translator.pm lines 533-586

**Test**: Error messages show file names and line numbers

### Day 18: Problem Testing

**Tasks**:
1. ✅ Test 10 different simple problems
2. ✅ Verify all render correctly
3. ✅ Check answer grading works
4. ✅ Document any issues

**Test Coverage**:
- Text-only problems
- Problems with numeric answers
- Problems with text answers
- Problems with multiple answers
- Problems with radio buttons
- Problems with dropdowns

### Day 19: Documentation

**Files to Create/Update**:
1. ✅ `packages/pg_macros/README.md` - Macro system overview
2. ✅ `packages/pg_macros/PORTING_GUIDE.md` - How to port Perl macros
3. ✅ Update `PARITY_STATUS.md` - Current progress
4. ✅ Update `IMPLEMENTATION_ANALYSIS.md` - Week 4 results

### Day 20: Performance & Cleanup

**Tasks**:
1. ✅ Add caching where needed
2. ✅ Optimize macro loading
3. ✅ Clean up code
4. ✅ Add type hints
5. ✅ Run linters

---

## 📊 SUCCESS METRICS

### Week 1 Complete When:
- ✅ Macro loader can load Python macros
- ✅ Init functions are called correctly
- ✅ Multiple macros can be loaded
- ✅ Error messages show file names

### Week 2 Complete When:
- ✅ TEXT() outputs text
- ✅ ANS() registers answers
- ✅ DOCUMENT/ENDDOCUMENT work
- ✅ loadMacros() integration complete

### Week 3 Complete When:
- ✅ ans_rule() generates input fields
- ✅ Display constants available
- ✅ MODES() works
- ✅ image() renders images

### Week 4 Complete When:
- ✅ 10 simple problems render
- ✅ Answers can be graded
- ✅ Error handling works
- ✅ Documentation complete

---

## 🚀 AFTER WEEK 4

### Immediate Next (Week 5-6):
1. **PGML Integration**
   - PGML.pl as loadable macro
   - BEGIN_PGML/END_PGML
   - Answer blanks in PGML
   - See Plan 01, Phase 2.3

2. **More Macros**
   - PGauxiliaryFunctions.pl
   - Choice macros completion
   - See Plan 01, Phase 3

### Then (Week 7-8):
3. **Answer System Enhancement**
   - Filter chains
   - cmp() methods on all types
   - MultiAnswer
   - See Plan 04

### Finally (Week 9+):
4. **Formula Enhancements**
   - Adaptive parameters
   - Advanced features
   - See Plan 03

---

## 📁 FILES TO CREATE

### New Files:
1. `packages/pg_macros/pg_macros/core/pg_core.py` (~1,800 lines)
2. `packages/pg_macros/pg_macros/core/pg_basic_macros.py` (~2,200 lines)
3. `packages/pg_macros/pg_macros/core/__init__.py` (~100 lines)
4. `packages/pg_translator/pg_translator/error_handler.py` (~300 lines)
5. `packages/pg_macros/README.md`
6. `packages/pg_macros/PORTING_GUIDE.md`

### Files to Modify:
1. `packages/pg_translator/pg_translator/macro_loader.py` (complete it)
2. `packages/pg_translator/pg_translator/sandbox.py` (add function registration)
3. `packages/pg_translator/pg_translator/environment.py` (add text/answer methods)
4. `packages/pg_translator/pg_translator/translator.py` (integrate macros)

### Test Files:
1. `packages/pg_macros/tests/test_pg_core.py` (~400 lines)
2. `packages/pg_macros/tests/test_pg_basic_macros.py` (~500 lines)
3. `packages/pg_macros/tests/test_macro_loader.py` (~200 lines)
4. `packages/pg_translator/tests/test_error_handler.py` (~200 lines)

---

## 🎯 FOCUS AREAS

### DO:
✅ Implement one function at a time
✅ Test each function immediately
✅ Use real problem examples
✅ Document as you go
✅ Stay focused on core macros

### DON'T:
❌ Try to implement everything at once
❌ Skip testing
❌ Refactor existing code extensively
❌ Add features not in plans
❌ Get distracted by "nice to haves"

---

## 📚 REFERENCE DOCUMENTS

1. **IMPLEMENTATION_ANALYSIS.md** - Overall gap analysis
2. **STRATEGIC_THINKING.md** - Why macros first
3. **plans/01_MACRO_SYSTEM_IMPLEMENTATION.md** - Detailed specifications
4. **plans/02_TRANSLATOR_FEATURES_IMPLEMENTATION.md** - Translator details
5. **PARITY_STATUS.md** - Current progress tracking

---

## 💡 GETTING STARTED

### Right Now:
1. Read `plans/01_MACRO_SYSTEM_IMPLEMENTATION.md` in full
2. Start with Week 1, Day 1: Complete unrestricted_load()
3. Test with a simple Python macro
4. Move to next task when current one works

### When Stuck:
1. Check Perl reference (lib/PG.pl, lib/PGbasicmacros.pl)
2. Look at existing Python implementations
3. Review implementation plan
4. Start with simplest version that works

### When Complete:
1. Update PARITY_STATUS.md with progress
2. Document what works
3. Create test problems
4. Move to next week's tasks

---

**Remember**: The goal is not perfection, it's progress. Get macros working, then improve.

---

**Start Now**: Week 1, Day 1 - Complete `unrestricted_load()`
