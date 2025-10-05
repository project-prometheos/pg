# Week 3 Implementation Plan: Advanced Features & PGML

## Overview

**Goal**: Implement advanced answer checkers, PGML support, and test with real OPL problems

**Duration**: 3 days

**Success Criteria**:
- str_cmp() with case sensitivity and options
- fun_cmp() with variable substitution
- PGML parser and renderer (basic)
- 20+ OPL problems working
- Advanced tolerance modes

## Status from Week 2

✅ **Completed**:
- In-process sandbox
- PG→Python translation
- TEXT/ANS/num_cmp working
- BEGIN_TEXT/END_TEXT processing
- SOLUTION/HINT collection
- Real .pg file support
- 100% test pass rate (10/10)

## Week 3 Phases

### Phase 1: Advanced Answer Checkers (Day 1)
- str_cmp() with options
- fun_cmp() with formula comparison
- Tolerance modes (relative, absolute, sigfigs)
- Test suite for each checker

### Phase 2: PGML Support (Day 2)
- PGML parser (markdown-like syntax)
- Variable interpolation in PGML
- Answer blank syntax: [_____]{$ans}
- BEGIN_PGML/END_PGML processing

### Phase 3: OPL Testing & Refinement (Day 3)
- Test with 20+ OPL problems
- Bug fixes and edge cases
- Performance optimization
- Documentation

---

## DAY 1: ADVANCED ANSWER CHECKERS

### Task 1.1: Enhanced str_cmp()

**File**: `packages/pg_answer/pg_answer/evaluators/string_cmp.py`

**Current Status**: Basic implementation exists

**Enhancements Needed**:
```python
def str_cmp(
    correct_answer: str,
    mode: str = "std",
    filters: list[str] | None = None,
    case_sensitive: bool = False,
    trim_whitespace: bool = True,
    **options
) -> StringEvaluator:
    """
    Create string answer checker.
    
    Args:
        correct_answer: Correct string answer
        mode: Comparison mode ("std", "regex", "ordered", etc.)
        filters: Text filters to apply
        case_sensitive: Whether comparison is case-sensitive
        trim_whitespace: Whether to trim leading/trailing whitespace
        **options: Additional options
    
    Returns:
        StringEvaluator
    
    Examples:
        ANS(str_cmp("hello", case_sensitive=False))
        ANS(str_cmp("a*b+c", mode="regex"))
    """
```

**Features to Implement**:
1. Case-insensitive comparison (default)
2. Whitespace trimming
3. Multiple correct answers
4. Regex matching mode
5. Substring matching

**Test Cases**:
```python
def test_str_cmp_case_insensitive():
    """Test case-insensitive string matching."""
    evaluator = str_cmp("Hello")
    assert evaluator.evaluate("hello").correct
    assert evaluator.evaluate("HELLO").correct
    assert evaluator.evaluate("Hello").correct

def test_str_cmp_case_sensitive():
    """Test case-sensitive string matching."""
    evaluator = str_cmp("Hello", case_sensitive=True)
    assert evaluator.evaluate("Hello").correct
    assert not evaluator.evaluate("hello").correct

def test_str_cmp_whitespace():
    """Test whitespace handling."""
    evaluator = str_cmp("hello world")
    assert evaluator.evaluate("  hello world  ").correct
    assert evaluator.evaluate("hello   world").correct  # Extra spaces
```

### Task 1.2: Enhanced fun_cmp()

**File**: `packages/pg_answer/pg_answer/evaluators/formula_cmp.py`

**Current Status**: Basic FormulaEvaluator exists

**Enhancements Needed**:
```python
def fun_cmp(
    correct_answer: str | Formula,
    var: str | list[str] = "x",
    limits: list[tuple[float, float]] | None = None,
    num_points: int = 5,
    tolerance: float = 0.001,
    tolerance_mode: str = "relative",
    **options
) -> FormulaEvaluator:
    """
    Create formula answer checker.
    
    Args:
        correct_answer: Correct formula expression
        var: Variable name(s)
        limits: Test range for each variable [(min, max), ...]
        num_points: Number of random test points
        tolerance: Numerical tolerance
        tolerance_mode: "relative", "absolute", or "sigfigs"
        **options: Additional options
    
    Returns:
        FormulaEvaluator
    
    Examples:
        ANS(fun_cmp("x^2 + 1", var="x"))
        ANS(fun_cmp("sin(x)*cos(y)", var=["x", "y"]))
    """
```

**Features to Implement**:
1. Multi-variable formulas
2. Custom test point ranges
3. Random test point generation
4. Symbolic equivalence checking
5. Domain validation

**Test Cases**:
```python
def test_fun_cmp_single_variable():
    """Test single-variable formula."""
    evaluator = fun_cmp("x^2 + 1", var="x")
    assert evaluator.evaluate("x**2 + 1").correct
    assert evaluator.evaluate("x*x + 1").correct

def test_fun_cmp_multi_variable():
    """Test multi-variable formula."""
    evaluator = fun_cmp("x + y", var=["x", "y"])
    assert evaluator.evaluate("y + x").correct  # Commutative

def test_fun_cmp_trig():
    """Test trigonometric functions."""
    evaluator = fun_cmp("sin(x)", var="x")
    assert evaluator.evaluate("sin(x)").correct
```

### Task 1.3: Tolerance Modes for num_cmp()

**File**: `packages/pg_answer/pg_answer/evaluators/numeric.py`

**Enhancements**:
```python
class NumericEvaluator:
    def __init__(
        self,
        correct_answer: MathValue | float | complex | str,
        tolerance: float = 0.001,
        tolerance_mode: str = ToleranceMode.RELATIVE,
        absolute_tolerance: float | None = None,
        relative_tolerance: float | None = None,
        sigfigs: int | None = None,
        **options
    ):
        """
        Initialize with multiple tolerance modes.
        
        Modes:
        - "relative": |student - correct| / |correct| < tolerance
        - "absolute": |student - correct| < tolerance
        - "sigfigs": Match to N significant figures
        """
```

**Test Cases**:
```python
def test_num_cmp_relative_tolerance():
    """Test relative tolerance (default)."""
    evaluator = num_cmp(100, tolerance=0.01)  # 1% tolerance
    assert evaluator.evaluate("101").correct
    assert evaluator.evaluate("99").correct
    assert not evaluator.evaluate("102").correct

def test_num_cmp_absolute_tolerance():
    """Test absolute tolerance."""
    evaluator = num_cmp(100, tolerance=0.5, tolerance_mode="absolute")
    assert evaluator.evaluate("100.4").correct
    assert not evaluator.evaluate("100.6").correct

def test_num_cmp_sigfigs():
    """Test significant figures."""
    evaluator = num_cmp(123.456, sigfigs=3)
    assert evaluator.evaluate("123").correct
    assert evaluator.evaluate("123.5").correct
```

### Task 1.4: Integration Tests

**File**: `packages/pg_translator/tests/test_advanced_checkers.py` (NEW)

**Test Problems**:
```python
def test_string_answer_problem():
    """Test problem with string answer."""
    pg_code = """
    DOCUMENT()
    TEXT("What is the capital of France?")
    TEXT(ans_rule(20))
    ANS(str_cmp("Paris", case_sensitive=False))
    ENDDOCUMENT()
    """
    # Test rendering and grading

def test_formula_answer_problem():
    """Test problem with formula answer."""
    pg_code = """
    DOCUMENT()
    TEXT("Simplify: x^2 + 2x + 1")
    TEXT(ans_rule(20))
    ANS(fun_cmp("(x+1)^2", var="x"))
    ENDDOCUMENT()
    """
    # Test rendering and grading
```

---

## DAY 2: PGML SUPPORT

### Task 2.1: PGML Parser

**File**: `packages/pg_pgml/pg_pgml/parser.py` (NEW)

**Implementation**:
```python
class PGMLParser:
    """
    Parse PGML (Problem Generation Markup Language).
    
    PGML is a markdown-like syntax for PG problems:
    - Headers: ## Title
    - Bold: **bold**
    - Italic: *italic*
    - Math: [`x^2`] for inline, [``` ... ```] for display
    - Answer blanks: [_____]{$ans}
    - Lists: - item or 1. item
    """
    
    def parse(self, pgml_source: str) -> PGMLDocument:
        """Parse PGML source into document tree."""
        
    def parse_line(self, line: str) -> list[PGMLNode]:
        """Parse a single line into nodes."""
        
    def find_answer_blanks(self, pgml_source: str) -> list[AnswerBlank]:
        """Extract answer blank definitions."""
```

**Features**:
1. Markdown-style formatting
2. LaTeX math in backticks
3. Variable interpolation: [$a] for variables
4. Answer blanks: [_____]{evaluator}
5. Nested structures

### Task 2.2: PGML Renderer

**File**: `packages/pg_pgml/pg_pgml/renderer.py` (NEW)

**Implementation**:
```python
class PGMLRenderer:
    """Render PGML to HTML."""
    
    def render(self, document: PGMLDocument) -> str:
        """Render document to HTML."""
        
    def render_node(self, node: PGMLNode) -> str:
        """Render single node to HTML."""
        
    def render_math(self, latex: str, display: bool = False) -> str:
        """Render LaTeX math."""
        
    def render_answer_blank(self, blank: AnswerBlank) -> str:
        """Render answer input field."""
```

### Task 2.3: BEGIN_PGML Processing

**File**: `packages/pg_translator/pg_translator/preprocessor.py`

**Enhancement**:
```python
def _process_pgml_block(self, content: str) -> str:
    """
    Process BEGIN_PGML...END_PGML block.
    
    Converts to:
    - Parse PGML syntax
    - Extract answer blanks
    - Generate TEXT() and ANS() calls
    """
```

**Example Transformation**:
```perl
# Input:
BEGIN_PGML
What is [$a] + [$b]?

Answer: [_____]{$ans}
END_PGML

# Output:
TEXT(render_pgml(f"What is {a} + {b}?\\n\\nAnswer: ", ans_rule_pgml(ans)))
ANS(ans)
```

### Task 2.4: PGML Integration Tests

**File**: `packages/pg_translator/tests/test_pgml.py` (NEW)

**Tests**:
```python
def test_pgml_basic():
    """Test basic PGML rendering."""
    
def test_pgml_math():
    """Test PGML with math."""
    
def test_pgml_answer_blanks():
    """Test PGML answer blanks."""
```

---

## DAY 3: OPL TESTING & REFINEMENT

### Task 3.1: Select OPL Test Problems

**Directory**: `packages/pg_translator/tests/opl_problems/` (NEW)

**Selection Criteria**:
- Variety of topics (algebra, calculus, trig)
- Different answer types (numeric, formula, string)
- Various difficulty levels
- Mix of old and new syntax

**Target Problems** (20+):
1. Library/Rochester/setAlgebra01Expressions/sw1_2_1.pg
2. Library/Rochester/setAlgebra02LinearEq/sw2_2_5.pg
3. Library/Rochester/setDerivatives1/s1_2_1.pg
4. ... (find more)

### Task 3.2: Create OPL Test Suite

**File**: `packages/pg_translator/tests/test_opl_problems.py` (NEW)

**Implementation**:
```python
import pytest
from pathlib import Path

OPL_PROBLEMS = list(Path("opl_problems").glob("*.pg"))

@pytest.mark.parametrize("problem_file", OPL_PROBLEMS)
def test_opl_problem_renders(problem_file):
    """Test that OPL problem renders without errors."""
    translator = PGTranslator()
    result = translator.translate(problem_file, seed=1234)
    
    assert result.errors is None or len(result.errors) == 0
    assert result.statement_html
    assert len(result.answer_blanks) > 0

@pytest.mark.parametrize("problem_file", OPL_PROBLEMS)
def test_opl_problem_with_multiple_seeds(problem_file):
    """Test problem renders consistently with different seeds."""
    translator = PGTranslator()
    results = []
    
    for seed in [1, 2, 3]:
        result = translator.translate(problem_file, seed=seed)
        results.append(result.statement_html)
    
    # Should produce valid output for each seed
    assert all(results)
```

### Task 3.3: Bug Fixing & Edge Cases

**Focus Areas**:
1. Complex LaTeX expressions
2. Nested function calls
3. Edge cases in variable interpolation
4. Performance with large problems
5. Error message quality

### Task 3.4: Performance Optimization

**Profiling**:
```python
import cProfile
import pstats

def profile_problem(problem_file):
    profiler = cProfile.Profile()
    profiler.enable()
    
    translator = PGTranslator()
    translator.translate(problem_file, seed=1234)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

**Optimization Targets**:
- Preprocessor regex compilation
- Parser caching
- Sandbox initialization
- Answer evaluator creation

### Task 3.5: Documentation

**Files to Create/Update**:
1. `WEEK3_COMPLETE.md` - Completion summary
2. `API.md` - API documentation
3. `EXAMPLES.md` - Usage examples
4. `PERFORMANCE.md` - Performance benchmarks

---

## Success Metrics

### Day 1 Success:
- [ ] str_cmp() with 3+ options working
- [ ] fun_cmp() with formula comparison
- [ ] Tolerance modes tested
- [ ] 90%+ test pass rate

### Day 2 Success:
- [ ] PGML parser functional
- [ ] Basic PGML rendering working
- [ ] Answer blanks in PGML
- [ ] 5+ PGML tests passing

### Day 3 Success:
- [ ] 20+ OPL problems tested
- [ ] 80%+ OPL problems passing
- [ ] Performance < 1s per problem
- [ ] Documentation complete

## Expected Challenges

1. **PGML Complexity** - Full markdown parser is complex
   - **Mitigation**: Start with subset, expand gradually

2. **Formula Equivalence** - Hard to detect symbolically
   - **Mitigation**: Use numerical testing with multiple points

3. **OPL Variety** - Many edge cases in real problems
   - **Mitigation**: Fix incrementally, prioritize common patterns

4. **Performance** - Some problems may be slow
   - **Mitigation**: Profile and optimize hot paths

## Timeline

**Day 1** (6 hours):
- Morning: str_cmp() enhancement (2h)
- Afternoon: fun_cmp() enhancement (2h)
- Evening: Tolerance modes + tests (2h)

**Day 2** (6 hours):
- Morning: PGML parser (3h)
- Afternoon: PGML renderer (2h)
- Evening: Integration tests (1h)

**Day 3** (6 hours):
- Morning: OPL problem selection (1h)
- Midday: OPL testing (3h)
- Afternoon: Bug fixes (1h)
- Evening: Documentation (1h)

## Total Estimate: 18 hours over 3 days

---

**Ready to start Week 3 Day 1!** 🚀
