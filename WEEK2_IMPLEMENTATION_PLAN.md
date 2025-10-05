# Week 2 Implementation Plan
## Translator Integration & Answer Evaluators

**Date**: October 5, 2025
**Status**: IN PROGRESS
**Dependencies**: Week 1 complete (pg_core.py, pg_basic_macros.py)

---

## OBJECTIVES

**Primary Goal**: Connect Week 1 macro implementations to translator so real .pg problems can render.

**Success Metrics**:
- ✅ Translator can load and execute PG.pl and PGbasicmacros.pl
- ✅ Simple .pg problems render correctly
- ✅ Answer checking works with num_cmp()
- ✅ 10 real OPL problems render without errors

**Estimated Time**: 3 days (1 developer)

---

## PHASE 1: MACRO INTEGRATION (Day 1)

### Task 1.1: Update Sandbox to Support Macro Functions

**File**: `packages/pg_translator/pg_translator/sandbox.py`

**Changes Needed**:
1. Add function registration method
2. Add variable registration method
3. Connect PGEnvironment to sandbox namespace
4. Support macro init functions

**Implementation**:
```python
class PGSandbox:
    def register_function(self, name: str, func: Callable) -> None:
        """Register function in sandbox namespace."""
        self.namespace[name] = func

    def register_variable(self, name: str, value: Any) -> None:
        """Register variable in sandbox namespace."""
        self.namespace[name] = value

    def set_environment(self, env: PGEnvironment) -> None:
        """Set PG environment for this execution."""
        self._pg_environment = env
        # Make environment available to macros
        self.namespace["_pg_environment"] = env
```

### Task 1.2: Update Executor to Use Macro System

**File**: `packages/pg_translator/pg_translator/executor.py`

**Changes Needed**:
1. Import pg_core and pg_basic_macros
2. Initialize PGEnvironment from pg_core
3. Register macro functions in sandbox
4. Call macro init functions

**Implementation**:
```python
from pg_macros.core import pg_core, pg_basic_macros

class PGExecutor:
    def execute(self, code: str, seed: int, context: Context | None = None) -> PGEnvironment:
        # Create PGEnvironment from pg_core
        envir = {
            "problemSeed": seed,
            "displayMode": "HTML",
            "showPartialCorrectAnswers": 1,
        }
        pg_env = pg_core.PGEnvironment(envir)
        pg_core.set_environment(pg_env)

        # Register macro functions
        self._register_pg_macros()

        # Execute code
        self.sandbox.set_environment(pg_env)
        self.sandbox.exec(code)

        # Convert pg_core.PGEnvironment to executor.PGEnvironment
        return self._convert_environment(pg_env)
```

### Task 1.3: Update MacroLoader to Call Init Functions

**File**: `packages/pg_translator/pg_translator/macro_loader.py`

**Changes Needed**:
1. Ensure unrestricted_load() calls _PG_init()
2. Ensure _PGbasicmacros_init() is called
3. Add error handling for init failures

**Already mostly complete** - verify it works.

### Task 1.4: Create Test Problems

**File**: `packages/pg_translator/tests/test_macro_integration.py` (NEW)

**Test Cases**:
```python
def test_load_pg_core():
    """Test loading PG.pl macros."""

def test_TEXT_function():
    """Test TEXT() outputs text."""

def test_ANS_registration():
    """Test ANS() registers answers."""

def test_simple_problem_complete():
    """Test complete problem with TEXT, ans_rule, ANS."""
```

---

## PHASE 2: ANSWER EVALUATORS (Day 2)

### Task 2.1: Port num_cmp()

**File**: `packages/pg_answer/pg_answer/evaluators/numeric_cmp.py` (NEW)

**Reference**: macros/PGanswermacros.pl lines 400-800

**Implementation**:
```python
def num_cmp(
    correct_answer: float | int,
    mode: str = "std",
    tolType: str = "relative",
    tolerance: float = 0.001,
    zeroLevel: float = 1e-14,
    zeroLevelTol: float = 1e-12,
    **options
) -> NumericEvaluator:
    """
    Create numeric answer checker with tolerance.

    Args:
        correct_answer: The correct numerical answer
        mode: Comparison mode ('std', 'strict', 'arith')
        tolType: 'relative' or 'absolute'
        tolerance: Tolerance value
        zeroLevel: Numbers below this are zero
        zeroLevelTol: Absolute tolerance near zero
        **options: Additional options (units, format, etc.)

    Returns:
        NumericEvaluator configured for comparison

    Example:
        ANS(num_cmp(3.14159, tolType='absolute', tolerance=0.001))
    """
    return NumericEvaluator(
        correct_answer=correct_answer,
        tolerance=tolerance,
        tol_type=tolType,
        zero_level=zeroLevel,
        zero_level_tol=zeroLevelTol,
        **options
    )
```

### Task 2.2: Enhance NumericEvaluator

**File**: `packages/pg_answer/pg_answer/evaluators/numeric.py`

**Add Features**:
1. Relative vs absolute tolerance
2. Zero-level handling
3. Units support (basic)
4. Format options

**Implementation**:
```python
class NumericEvaluator(AnswerEvaluator):
    def evaluate(self, student_answer: str) -> AnswerResult:
        # Parse student answer
        try:
            student_value = float(student_answer)
        except ValueError:
            return AnswerResult(
                is_correct=False,
                score=0.0,
                message="Your answer must be a number."
            )

        # Check tolerance
        if self.tol_type == "relative":
            # Relative tolerance
            if abs(self.correct_answer) < self.zero_level:
                # Near zero, use absolute
                diff = abs(student_value - self.correct_answer)
                is_correct = diff < self.zero_level_tol
            else:
                rel_error = abs(student_value - self.correct_answer) / abs(self.correct_answer)
                is_correct = rel_error < self.tolerance
        else:
            # Absolute tolerance
            diff = abs(student_value - self.correct_answer)
            is_correct = diff < self.tolerance

        return AnswerResult(
            is_correct=is_correct,
            score=1.0 if is_correct else 0.0,
            student_answer=student_answer,
            correct_answer=str(self.correct_answer)
        )
```

### Task 2.3: Port str_cmp()

**File**: `packages/pg_answer/pg_answer/evaluators/string_cmp.py` (NEW)

**Implementation**:
```python
def str_cmp(
    correct_answer: str,
    mode: str = "std",
    ignoreCase: bool = False,
    ignoreWhitespace: bool = False,
    **options
) -> StringEvaluator:
    """
    Create string answer checker.

    Args:
        correct_answer: The correct string
        mode: Comparison mode
        ignoreCase: Ignore case differences
        ignoreWhitespace: Ignore whitespace
        **options: Additional options

    Returns:
        StringEvaluator

    Example:
        ANS(str_cmp("hello", ignoreCase=True))
    """
    return StringEvaluator(
        correct_answer=correct_answer,
        ignore_case=ignoreCase,
        ignore_whitespace=ignoreWhitespace,
        **options
    )
```

### Task 2.4: Port fun_cmp() (Basic)

**File**: `packages/pg_answer/pg_answer/evaluators/formula_cmp.py` (NEW)

**Implementation**:
```python
def fun_cmp(
    correct_answer: str | Formula,
    var: str | list[str] = "x",
    mode: str = "std",
    numPoints: int = 5,
    tolerance: float = 0.001,
    **options
) -> FormulaEvaluator:
    """
    Create formula answer checker.

    Args:
        correct_answer: Correct formula (string or Formula object)
        var: Variable(s) to use
        mode: Comparison mode
        numPoints: Number of test points
        tolerance: Numerical tolerance
        **options: Additional options

    Returns:
        FormulaEvaluator

    Example:
        ANS(fun_cmp("x^2 + 1", var="x"))
    """
    # Parse if string
    if isinstance(correct_answer, str):
        parser = Parser()
        correct_formula = parser.parse(correct_answer)
    else:
        correct_formula = correct_answer

    return FormulaEvaluator(
        correct_formula=correct_formula,
        variables=var if isinstance(var, list) else [var],
        num_test_points=numPoints,
        tolerance=tolerance,
        **options
    )
```

### Task 2.5: Register Answer Checker Functions

**File**: `packages/pg_macros/pg_macros/core/pg_answer_checkers.py` (NEW)

**Purpose**: Make num_cmp, str_cmp, fun_cmp available in problems

**Implementation**:
```python
"""Answer checker macro functions."""

from pg_answer.evaluators import (
    NumericEvaluator,
    StringEvaluator,
    FormulaEvaluator,
)

def num_cmp(correct_answer, **options):
    """Numeric answer checker - see numeric_cmp.py"""
    from pg_answer.evaluators.numeric_cmp import num_cmp as _num_cmp
    return _num_cmp(correct_answer, **options)

def str_cmp(correct_answer, **options):
    """String answer checker - see string_cmp.py"""
    from pg_answer.evaluators.string_cmp import str_cmp as _str_cmp
    return _str_cmp(correct_answer, **options)

def fun_cmp(correct_answer, **options):
    """Formula answer checker - see formula_cmp.py"""
    from pg_answer.evaluators.formula_cmp import fun_cmp as _fun_cmp
    return _fun_cmp(correct_answer, **options)

def _PGanswermacros_init():
    """Initialize answer checker macros."""
    from pg_translator.sandbox import get_sandbox
    sandbox = get_sandbox()

    sandbox.register_function("num_cmp", num_cmp)
    sandbox.register_function("str_cmp", str_cmp)
    sandbox.register_function("fun_cmp", fun_cmp)
```

---

## PHASE 3: END-TO-END TESTING (Day 3)

### Task 3.1: Create Real Problem Tests

**File**: `packages/pg_translator/tests/problems/simple_numeric.pg` (NEW)

**Test Problem 1**:
```perl
DOCUMENT();
loadMacros("PG.pl", "PGbasicmacros.pl");

TEXT("What is 2 + 2?");
TEXT(BR());
TEXT("Answer: ", ans_rule(20));

ANS(num_cmp(4));

ENDDOCUMENT();
```

**Test Problem 2**:
```perl
DOCUMENT();
loadMacros("PG.pl", "PGbasicmacros.pl");

$a = random(1, 10, 1);
$b = random(1, 10, 1);
$ans = $a + $b;

BEGIN_TEXT
What is \($a + $b\)?
$PAR
Answer: \{ ans_rule(20) \}
END_TEXT

ANS(num_cmp($ans));

ENDDOCUMENT();
```

### Task 3.2: Create Integration Test Suite

**File**: `packages/pg_translator/tests/test_end_to_end.py` (NEW)

**Tests**:
```python
def test_simple_numeric_problem():
    """Test simple numeric problem renders and grades."""
    translator = PGTranslator()
    result = translator.translate(
        "tests/problems/simple_numeric.pg",
        seed=1234
    )

    assert result.errors is None
    assert "What is 2 + 2?" in result.statement_html
    assert 'name="AnSwEr0001"' in result.statement_html
    assert len(result.answer_blanks) == 1

def test_simple_numeric_grading():
    """Test simple numeric problem grades correctly."""
    translator = PGTranslator()

    # Correct answer
    result = translator.translate(
        "tests/problems/simple_numeric.pg",
        seed=1234,
        inputs={"AnSwEr0001": "4"}
    )

    assert result.score == 1.0
    assert result.answer_results["AnSwEr0001"].is_correct

    # Wrong answer
    result = translator.translate(
        "tests/problems/simple_numeric.pg",
        seed=1234,
        inputs={"AnSwEr0001": "5"}
    )

    assert result.score == 0.0
    assert not result.answer_results["AnSwEr0001"].is_correct

def test_random_problem():
    """Test problem with random() function."""
    # Test with multiple seeds to ensure randomization works
    translator = PGTranslator()

    results = []
    for seed in [1, 2, 3, 4, 5]:
        result = translator.translate(
            "tests/problems/random_addition.pg",
            seed=seed
        )
        results.append(result.statement_html)

    # Should have different problems
    unique_problems = len(set(results))
    assert unique_problems > 1, "Random problems should vary"
```

### Task 3.3: Test With Real OPL Problems

**Directory**: `packages/pg_translator/tests/opl_samples/`

**Sample Problems** (copy from OPL):
1. `Library/LoyolaChicago/Precalc/Chap1Sec1/Q02.pg` - Simple arithmetic
2. `Library/Union/setIntegration/an7_3_06.pg` - Basic calculus
3. `Library/Rochester/setAlgebra01RealNumbers/lhp1_3.pg` - Algebra
4. (7 more simple problems)

**Test**:
```python
def test_opl_problems():
    """Test that 10 OPL problems render without errors."""
    translator = PGTranslator()

    opl_dir = Path("tests/opl_samples")
    pg_files = list(opl_dir.glob("*.pg"))[:10]

    successes = 0
    for pg_file in pg_files:
        result = translator.translate(pg_file, seed=1234)
        if result.errors is None or len(result.errors) == 0:
            successes += 1

    # Should render at least 7/10 successfully
    assert successes >= 7, f"Only {successes}/10 OPL problems rendered"
```

---

## IMPLEMENTATION CHECKLIST

### Day 1: Macro Integration
- [ ] Update `sandbox.py` with function registration
- [ ] Update `executor.py` to use pg_core.PGEnvironment
- [ ] Verify `macro_loader.py` calls init functions
- [ ] Create `test_macro_integration.py`
- [ ] All integration tests pass

### Day 2: Answer Evaluators
- [ ] Create `numeric_cmp.py` with num_cmp()
- [ ] Enhance `NumericEvaluator` with tolerance modes
- [ ] Create `string_cmp.py` with str_cmp()
- [ ] Create `formula_cmp.py` with fun_cmp() (basic)
- [ ] Create `pg_answer_checkers.py` with macro functions
- [ ] Unit tests for all answer checkers

### Day 3: End-to-End Testing
- [ ] Create simple test .pg problems
- [ ] Create `test_end_to_end.py`
- [ ] Copy 10 OPL problems to test directory
- [ ] Run full test suite
- [ ] Fix any integration issues
- [ ] Document what works and what doesn't

---

## SUCCESS CRITERIA

### Must Have (Critical)
✅ Simple numeric problems render
✅ Answer blanks appear correctly
✅ Numeric answers check correctly
✅ Random numbers work
✅ At least 5/10 OPL problems render

### Should Have (Important)
✅ String answers work
✅ Formula answers work (basic)
✅ Error messages are helpful
✅ 7/10 OPL problems render

### Nice to Have (Bonus)
✅ 10/10 OPL problems render
✅ Multiple answer types in one problem
✅ Solutions display correctly

---

## RISKS & MITIGATION

### Risk 1: Namespace Conflicts
**Issue**: pg_core.PGEnvironment vs executor.PGEnvironment
**Mitigation**: Use pg_core version as canonical, convert in executor

### Risk 2: Answer Evaluator Serialization
**Issue**: Sandbox returns serialized data, not live objects
**Mitigation**: Keep evaluators in translator, only pass answer names

### Risk 3: Perl-Python Impedance
**Issue**: .pg files are still Perl syntax
**Mitigation**: Focus on problems that use simple syntax, add Perl→Python preprocessor

### Risk 4: Missing Macro Functions
**Issue**: Problems call macros not yet ported
**Mitigation**: Implement stubs that return errors, prioritize commonly-used macros

---

## NEXT STEPS AFTER WEEK 2

### Week 3: PGML Integration
- Complete PGML.pl port
- BEGIN_PGML / END_PGML
- Answer blanks in PGML
- Tables and formatting

### Week 4: More Macros
- PGauxiliaryFunctions.pl
- More answer checkers
- Context system basics

---

## DOCUMENTATION TO UPDATE

After Week 2 complete:
1. Update `PARITY_STATUS.md` with new coverage
2. Create `WEEK2_COMPLETE.md` with results
3. Update `README.md` with usage examples
4. Create migration guide for problem authors

---

**Start Date**: October 5, 2025
**Target Completion**: October 8, 2025 (3 days)
**Status**: Ready to begin Day 1
