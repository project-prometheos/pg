# Week 4 Plan: MathObjects Foundation

## Overview

Week 4 will implement the core MathObjects framework, which is the foundation for modern WeBWorK problem authoring. This is required to support the tutorial OPL problems we attempted to test in Week 3.

## Current Status

**Week 3 Complete**: 45/45 PGML tests passing (100%)

**Blocking Issue**: Tutorial OPL problems require MathObjects:
- `IndefiniteIntegrals.pg`: Uses `Formula()`, `FormulaUpToConstant()`, `->cmp()` methods
- `ExpandedPolynomial.pg`: Uses `Context()`, `Compute()`, `contextLimitedPolynomial`
- `UnitConversion.pg`: Uses `Context('Units')`, `->toUnits()` methods

## MathObjects Architecture

### Core Components

1. **Context System** - Defines what operations, variables, and constants are available
2. **Value Classes** - Real, Complex, Point, Vector, Interval, etc.
3. **Formula Class** - Stores and manipulates symbolic expressions
4. **Parser** - Converts strings to MathObject AST
5. **Evaluator** - Computes values from formulas
6. **Comparator** - Implements `->cmp()` method for answer checking

### Key Features

- Type system: Real, Complex, Point, Vector, Interval, String, List
- Context switching: `Context('Numeric')`, `Context('Complex')`, etc.
- Formula parsing: `Formula("x^2 + 1")` creates symbolic expression
- Compute evaluation: `Compute("2+2")` returns `Real(4)`
- Answer checking: `$ans->cmp()` returns answer checker
- Method chaining: `Formula("x^2")->substitute(x=>5)->reduce`

## Week 4 Goals

### Day 1: Context System Foundation ✓
**Goal**: Implement basic Context class and Numeric context

**Deliverables**:
- `packages/pg_mathobjects/` package structure
- `pg_mathobjects/context.py` - Context class
- `pg_mathobjects/numeric_context.py` - Numeric context with standard operations
- Tests: Context creation, switching, variable/constant management

**Success Criteria**:
```python
Context('Numeric')
Context().variables.add('t', 'Real')
Context().constants.set('pi', 3.14159...)
```

### Day 2: Value Classes (Real, Formula) ✓
**Goal**: Implement Real and Formula classes

**Deliverables**:
- `pg_mathobjects/value.py` - Base Value class
- `pg_mathobjects/real.py` - Real number class
- `pg_mathobjects/formula.py` - Formula class (symbolic)
- Tests: Value creation, arithmetic, comparison

**Success Criteria**:
```python
r = Real(5)
r + 3  # Real(8)
r.value  # 5

f = Formula("x^2 + 1")
f.eval(x=2)  # Real(5)
```

### Day 3: Compute() and Parser Integration ✓
**Goal**: Implement Compute() function and integrate parser

**Deliverables**:
- `pg_mathobjects/compute.py` - Compute() function
- `pg_mathobjects/parser.py` - Expression parser
- Integration with existing pg_translator sandbox
- Tests: Parsing expressions, constant folding, evaluation

**Success Criteria**:
```python
Compute("2+2")  # Real(4)
Compute("x^2")  # Formula("x^2")
Compute("sin(pi)")  # Real(0)
```

### Day 4: Answer Checking (cmp method) ✓
**Goal**: Implement ->cmp() method for answer checking

**Deliverables**:
- `pg_mathobjects/answer_checker.py` - Answer checker implementation
- Integration with existing evaluator system
- Tests: Numeric comparison with tolerance, formula comparison

**Success Criteria**:
```python
ans = Compute("42")
checker = ans.cmp(tolerance=0.01)
checker.check("42")  # correct
checker.check("42.005")  # correct
checker.check("43")  # incorrect
```

### Day 5: OPL Problem Validation ✓
**Goal**: Validate with real tutorial problems

**Deliverables**:
- Update `test_opl_problems.py` to use MathObjects
- Test `IndefiniteIntegrals.pg` with basic MathObjects
- Document unsupported features for future weeks

**Success Criteria**:
- At least 1 tutorial problem produces non-empty HTML
- MathObjects integration with PGML working
- Clear list of remaining features needed

## Implementation Strategy

### Phase 1: Minimal Viable Context (Day 1)

```python
# packages/pg_mathobjects/pg_mathobjects/context.py

class Context:
    """Context controls parser behavior and available operations."""

    def __init__(self, name='Numeric'):
        self.name = name
        self.variables = VariableManager()
        self.constants = ConstantManager()
        self.functions = FunctionManager()
        self.operators = OperatorManager()
        self.flags = ContextFlags()

    def copy(self, name=None):
        """Create a copy of this context."""
        pass

# Global context registry
_contexts = {}
_current_context = None

def Context(name=None):
    """Get or set current context."""
    global _current_context
    if name is None:
        return _current_context
    if name not in _contexts:
        _contexts[name] = create_context(name)
    _current_context = _contexts[name]
    return _current_context
```

### Phase 2: Real Numbers (Day 2)

```python
# packages/pg_mathobjects/pg_mathobjects/real.py

class Real(Value):
    """Real number MathObject."""

    def __init__(self, value, context=None):
        super().__init__(context)
        self.value = float(value)

    def __add__(self, other):
        return Real(self.value + other.value)

    def __eq__(self, other):
        return abs(self.value - other.value) < self.context.tolerance

    def cmp(self, **options):
        """Return answer checker."""
        return RealAnswerChecker(self, **options)
```

### Phase 3: Formula Class (Day 2-3)

```python
# packages/pg_mathobjects/pg_mathobjects/formula.py

class Formula(Value):
    """Symbolic formula MathObject."""

    def __init__(self, expression, context=None):
        super().__init__(context)
        self.expression = expression
        self.tree = self.context.parser.parse(expression)

    def eval(self, **vars):
        """Evaluate formula with given variables."""
        return self.tree.eval(vars, self.context)

    def substitute(self, **vars):
        """Substitute variables, return new Formula."""
        new_tree = self.tree.substitute(vars)
        return Formula(new_tree.to_string(), self.context)

    def reduce(self):
        """Simplify formula."""
        simplified = self.tree.reduce(self.context)
        return Formula(simplified.to_string(), self.context)

    def cmp(self, **options):
        """Return answer checker."""
        return FormulaAnswerChecker(self, **options)
```

### Phase 4: Compute() Function (Day 3)

```python
# packages/pg_mathobjects/pg_mathobjects/compute.py

def Compute(expression, context=None):
    """
    Parse and evaluate expression.

    Returns Real for constant expressions,
    Formula for symbolic expressions.
    """
    if context is None:
        context = Context()

    # Parse expression
    tree = context.parser.parse(expression)

    # Try to evaluate as constant
    if tree.is_constant():
        result = tree.eval({}, context)
        return Real(result, context)

    # Return as Formula
    return Formula(expression, context)
```

### Phase 5: Integration (Day 4-5)

```python
# packages/pg_translator/pg_translator/in_process_sandbox.py

def _load_pg_core():
    """Load PG core functions including MathObjects."""
    from pg_mathobjects import Context, Real, Formula, Compute

    # ... existing code ...

    pg_core = type('PGCore', (), {
        # ... existing functions ...
        'Context': Context,
        'Real': Real,
        'Formula': Formula,
        'Compute': Compute,
    })()

    return pg_core
```

## Test Plan

### Day 1 Tests: Context System (10 tests)
```python
# test_context.py
def test_context_creation()
def test_context_switching()
def test_variables_add()
def test_variables_remove()
def test_constants_add()
def test_functions_add()
def test_context_copy()
def test_context_flags()
def test_multiple_contexts()
def test_context_persistence()
```

### Day 2 Tests: Value Classes (15 tests)
```python
# test_real.py
def test_real_creation()
def test_real_arithmetic()
def test_real_comparison()
def test_real_methods()

# test_formula.py
def test_formula_creation()
def test_formula_eval()
def test_formula_substitute()
def test_formula_reduce()
def test_formula_variables()
```

### Day 3 Tests: Compute (12 tests)
```python
# test_compute.py
def test_compute_constant()
def test_compute_expression()
def test_compute_with_variables()
def test_compute_with_functions()
def test_compute_errors()
```

### Day 4 Tests: Answer Checking (10 tests)
```python
# test_cmp.py
def test_real_cmp()
def test_real_cmp_tolerance()
def test_formula_cmp()
def test_formula_cmp_variables()
def test_cmp_with_options()
```

### Day 5 Tests: Integration (3+ tests)
```python
# test_mathobjects_integration.py
def test_simple_problem_with_compute()
def test_formula_problem()
def test_tutorial_problem_basic()
```

**Total Week 4 Tests: ~50 new tests**

## Dependencies

### New Package: pg_mathobjects
```
packages/
  pg_mathobjects/
    setup.py
    pg_mathobjects/
      __init__.py
      context.py          # Context system
      value.py            # Base Value class
      real.py             # Real numbers
      formula.py          # Symbolic formulas
      compute.py          # Compute() function
      parser.py           # Expression parser
      answer_checker.py   # ->cmp() implementation
      numeric_context.py  # Numeric context definition
```

### Updated Packages
- `pg_translator`: Import and expose MathObjects in sandbox
- `pg_macros`: May need updates for MathObjects integration

## Success Metrics

### Minimum Success (Week 4 MVP)
- ✅ Context system working
- ✅ Real numbers with arithmetic
- ✅ Formula creation and evaluation
- ✅ Compute() function working
- ✅ Basic ->cmp() method
- ✅ 40+ tests passing

### Stretch Goals
- Formula simplification (reduce)
- Complex numbers
- Point/Vector classes
- List class
- 1+ tutorial problem fully working

## Known Limitations (Deferred to Week 5+)

### Advanced Contexts
- `contextLimitedPolynomial.pl` - Restricted operations
- `contextUnits.pl` - Physical units
- `contextFraction.pl` - Fraction arithmetic
- `contextComplex.pl` - Complex numbers

### Advanced Features
- `FormulaUpToConstant` - Antiderivatives
- `->toUnits()` - Unit conversion
- Matrix operations
- Vector operations
- Interval arithmetic

### Parser Features
- Full operator precedence
- Function definitions
- Custom operators
- Bizarro arithmetic (for form checking)

## Risk Mitigation

### Risk 1: Parser Complexity
**Mitigation**: Start with simple expression parser, defer complex features.
Use existing Python AST parsing if needed.

### Risk 2: Perl/Python Semantic Differences
**Mitigation**: Focus on behavior, not implementation. Document differences.

### Risk 3: Integration with Existing Code
**Mitigation**: Incremental integration, maintain backward compatibility.

## Documentation

### User Documentation
- `MATHOBJECTS_QUICK_START.md` - Getting started guide
- `MATHOBJECTS_CONTEXTS.md` - Available contexts
- `MATHOBJECTS_API.md` - API reference

### Developer Documentation
- `MATHOBJECTS_ARCHITECTURE.md` - Design decisions
- `MATHOBJECTS_TESTING.md` - Testing strategy
- `MATHOBJECTS_EXTENDING.md` - Adding new contexts/types

## Timeline

- **Day 1** (4-6 hours): Context system
- **Day 2** (6-8 hours): Value classes (Real, Formula basics)
- **Day 3** (6-8 hours): Compute() and parser
- **Day 4** (4-6 hours): Answer checking (cmp)
- **Day 5** (2-4 hours): Integration and validation

**Total Estimated Effort**: 22-32 hours

## Next Steps

After Week 4 completion:

**Week 5**: Advanced MathObjects
- Complex numbers
- Points and Vectors
- Lists and Sets
- Intervals

**Week 6**: Specialized Contexts
- LimitedPolynomial
- Units
- Fractions
- FormulaUpToConstant

**Week 7**: Full OPL Tutorial Support
- Test all tutorial problems
- Document coverage
- Performance optimization

---

**Status**: 📋 **PLANNING COMPLETE - READY TO START**
**Date**: 2025-01-08
**Prerequisites**: Week 3 complete (PGML 45/45 tests passing)
