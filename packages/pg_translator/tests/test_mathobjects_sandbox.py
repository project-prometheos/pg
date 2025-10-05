"""
Test MathObjects integration with in_process_sandbox.
"""

import pytest
from pg_translator.in_process_sandbox import InProcessSandbox


class TestMathObjectsBasic:
    """Test basic MathObjects functionality in sandbox."""

    def test_context_available(self):
        """Test that Context is available in sandbox."""
        sandbox = InProcessSandbox()
        
        code = """
result = Context is not None
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['result'] is True

    def test_real_creation(self):
        """Test creating Real numbers in sandbox."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Real

r = Real(5)
result = r.value
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['result'] == 5.0

    def test_formula_creation(self):
        """Test creating Formulas in sandbox."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

f = Formula("x+1")
result = str(f)
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert 'x' in result.variables['result']
        assert '1' in result.variables['result']

    def test_compute_constant(self):
        """Test Compute with constant expression."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Compute

c = Compute("2+2")
result = c.value
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['result'] == 4.0

    def test_compute_formula(self):
        """Test Compute with variable expression."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Compute, Formula

f = Compute("x^2 + 1")
is_formula = isinstance(f, Formula)
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['is_formula'] is True


class TestMathObjectsInProblem:
    """Test MathObjects in complete .pg problems."""

    def test_simple_problem_with_formula(self):
        """Test a simple problem using Formula."""
        sandbox = InProcessSandbox()
        
        code = """
DOCUMENT()

from pg_mathobjects import Formula, Real

# Problem setup
a = 2
b = 3
answer = Real(a + b)

# Display
TEXT("What is ", str(a), " + ", str(b), "?")
TEXT(ans_rule())

# Answer
ANS(answer.cmp())

ENDDOCUMENT()
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert len(result.answers) == 1

    def test_problem_with_compute(self):
        """Test problem using Compute."""
        sandbox = InProcessSandbox()
        
        code = """
DOCUMENT()

from pg_mathobjects import Compute

# Compute answer
ans = Compute("3+4")

TEXT("What is 3 + 4?")
TEXT(ans_rule())

ANS(ans.cmp())

ENDDOCUMENT()
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert len(result.answers) == 1

    def test_problem_with_context(self):
        """Test problem using Context."""
        sandbox = InProcessSandbox()
        
        code = """
DOCUMENT()

from pg_mathobjects import Context, Compute

# Set up context
Context("Numeric")
ctx = Context()

# Create formula
f = Compute("x^2")

TEXT("The function is f(x) = x^2")

ENDDOCUMENT()
"""
        result = sandbox.execute(code, seed=123)
        assert result.success


class TestFormulaEvaluation:
    """Test Formula evaluation in sandbox."""

    def test_formula_eval(self):
        """Test evaluating a formula."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

f = Formula("x^2 + 1")
result = f.eval(x=3)
value = result.value
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['value'] == 10.0

    def test_formula_substitute(self):
        """Test formula substitution."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

f = Formula("x^2")
g = f.substitute(x="y+1")
has_y = 'y' in str(g)
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['has_y'] is True

    def test_formula_differentiate(self):
        """Test formula differentiation."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

f = Formula("x^2")
df = f.D('x')
result_at_3 = df.eval(x=3)
value = result_at_3.value
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['value'] == 6.0


class TestMathObjectsAnswerChecking:
    """Test MathObjects answer checking."""

    def test_real_answer_checker(self):
        """Test Real answer checker."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Real

correct = Real(5)
checker = correct.cmp()
result = checker.check("5")
is_correct = result['correct']
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['is_correct'] is True

    def test_formula_answer_checker(self):
        """Test Formula answer checker."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

correct = Formula("x^2 + 1")
checker = correct.cmp()
result = checker.check("x^2 + 1")
is_correct = result['correct']
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['is_correct'] is True

    def test_formula_equivalence_checking(self):
        """Test formula equivalence."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

correct = Formula("x^2 + 2*x + 1")
checker = correct.cmp()
result = checker.check("(x+1)^2")
is_correct = result['correct']
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert result.variables['is_correct'] is True


class TestMathObjectsPGML:
    """Test MathObjects with PGML."""

    def test_pgml_with_compute(self):
        """Test using Compute in PGML."""
        sandbox = InProcessSandbox()
        
        code = """
DOCUMENT()

from pg_mathobjects import Compute

ans = Compute("2+2")

html = PGML('''
What is 2 + 2?

[_____]{ans}
''')

TEXT(html)

ENDDOCUMENT()
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        # Should have one answer from PGML
        assert len(result.answers) >= 1

    def test_pgml_with_formula(self):
        """Test using Formula in PGML."""
        sandbox = InProcessSandbox()
        
        code = """
DOCUMENT()

from pg_mathobjects import Formula

f = Formula("x^2 + 1")

html = PGML('''
Enter the formula: [`f(x) = x^2 + 1`]

[_____]{f}
''')

TEXT(html)

ENDDOCUMENT()
"""
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert len(result.answers) >= 1
