"""
Test Formula class implementation.
"""

import pytest
import math
from pg_mathobjects import Context, Formula, Compute, Real


class TestFormulaCreation:
    """Test Formula creation and parsing."""
    
    def test_create_simple_formula(self):
        """Test creating a simple formula."""
        f = Formula("x+1")
        assert str(f) == "x + 1"
    
    def test_create_polynomial(self):
        """Test creating a polynomial formula."""
        f = Formula("x^2 + 2*x + 1")
        assert "x" in str(f)
    
    def test_create_with_multiple_variables(self):
        """Test formula with multiple variables."""
        f = Formula("x + y")
        assert "x" in str(f) and "y" in str(f)
    
    def test_create_with_functions(self):
        """Test formula with functions."""
        f = Formula("sin(x)")
        assert "sin" in str(f).lower()
    
    def test_formula_with_constants(self):
        """Test formula with constants."""
        f = Formula("pi*x")
        assert "pi" in str(f).lower()


class TestFormulaEvaluation:
    """Test Formula evaluation."""
    
    def test_eval_simple(self):
        """Test evaluating simple formula."""
        f = Formula("x+1")
        result = f.eval(x=5)
        assert isinstance(result, Real)
        assert result.value == 6
    
    def test_eval_polynomial(self):
        """Test evaluating polynomial."""
        f = Formula("x^2 + 2*x + 1")
        result = f.eval(x=3)
        assert isinstance(result, Real)
        assert result.value == 16  # 9 + 6 + 1
    
    def test_eval_with_multiple_variables(self):
        """Test evaluating with multiple variables."""
        f = Formula("x*y + 2")
        result = f.eval(x=3, y=4)
        assert isinstance(result, Real)
        assert result.value == 14
    
    def test_eval_with_function(self):
        """Test evaluating with functions."""
        f = Formula("sin(x)")
        result = f.eval(x=0)
        assert isinstance(result, Real)
        assert abs(result.value - 0) < 0.01
    
    def test_eval_with_pi(self):
        """Test evaluating with pi."""
        f = Formula("pi*x")
        result = f.eval(x=2)
        assert isinstance(result, Real)
        assert abs(result.value - 2*math.pi) < 0.01
    
    def test_eval_partial(self):
        """Test partial evaluation (still has variables)."""
        f = Formula("x*y + z")
        result = f.eval(x=2, y=3)
        # Should still be a Formula since z is unassigned
        assert isinstance(result, Formula)


class TestFormulaSubstitution:
    """Test Formula substitution."""
    
    def test_substitute_number(self):
        """Test substituting a number."""
        f = Formula("x+1")
        g = f.substitute(x=5)
        assert isinstance(g, Formula)
        result = g.eval()
        assert result.value == 6
    
    def test_substitute_expression(self):
        """Test substituting an expression."""
        f = Formula("x^2 + 1")
        g = f.substitute(x="y+1")
        assert "y" in str(g)
    
    def test_substitute_multiple(self):
        """Test multiple substitutions."""
        f = Formula("x*y")
        g = f.substitute(x=2, y=3)
        result = g.eval()
        assert result.value == 6


class TestFormulaReduction:
    """Test Formula reduction/simplification."""
    
    def test_reduce_simple(self):
        """Test reducing simple expression."""
        f = Formula("x + x")
        g = f.reduce()
        # Should simplify to 2*x
        assert "2" in str(g)
    
    def test_reduce_polynomial(self):
        """Test reducing polynomial."""
        f = Formula("(x+1)^2")
        g = f.reduce()
        # Should expand and simplify
        assert "x" in str(g)
    
    def test_reduce_fraction(self):
        """Test reducing fractions."""
        f = Formula("(x^2 - 1)/(x - 1)")
        g = f.reduce()
        # Should simplify (x+1 for x != 1)
        result = g.eval(x=2)
        assert abs(result.value - 3) < 0.01


class TestFormulaDifferentiation:
    """Test Formula differentiation."""
    
    def test_differentiate_simple(self):
        """Test differentiating simple formula."""
        f = Formula("x^2")
        df = f.D('x')
        assert isinstance(df, Formula)
        result = df.eval(x=3)
        assert result.value == 6  # 2*x at x=3
    
    def test_differentiate_polynomial(self):
        """Test differentiating polynomial."""
        f = Formula("x^3 + 2*x^2 + x + 1")
        df = f.D('x')
        result = df.eval(x=1)
        assert result.value == 8  # 3 + 4 + 1
    
    def test_differentiate_trig(self):
        """Test differentiating trig function."""
        f = Formula("sin(x)")
        df = f.D('x')
        result = df.eval(x=0)
        assert abs(result.value - 1) < 0.01  # cos(0) = 1


class TestFormulaArithmetic:
    """Test Formula arithmetic operations."""
    
    def test_add_formulas(self):
        """Test adding two formulas."""
        f1 = Formula("x")
        f2 = Formula("1")
        f3 = f1 + f2
        assert isinstance(f3, Formula)
        result = f3.eval(x=5)
        assert result.value == 6
    
    def test_subtract_formulas(self):
        """Test subtracting two formulas."""
        f1 = Formula("x")
        f2 = Formula("1")
        f3 = f1 - f2
        assert isinstance(f3, Formula)
        result = f3.eval(x=5)
        assert result.value == 4
    
    def test_multiply_formulas(self):
        """Test multiplying two formulas."""
        f1 = Formula("x")
        f2 = Formula("2")
        f3 = f1 * f2
        assert isinstance(f3, Formula)
        result = f3.eval(x=5)
        assert result.value == 10
    
    def test_divide_formulas(self):
        """Test dividing two formulas."""
        f1 = Formula("x")
        f2 = Formula("2")
        f3 = f1 / f2
        assert isinstance(f3, Formula)
        result = f3.eval(x=10)
        assert result.value == 5
    
    def test_power_formula(self):
        """Test raising formula to power."""
        f = Formula("x")
        f2 = f ** 2
        assert isinstance(f2, Formula)
        result = f2.eval(x=3)
        assert result.value == 9
    
    def test_negate_formula(self):
        """Test negating formula."""
        f = Formula("x")
        nf = -f
        assert isinstance(nf, Formula)
        result = nf.eval(x=5)
        assert result.value == -5


class TestFormulaTeX:
    """Test Formula TeX output."""
    
    def test_tex_simple(self):
        """Test TeX for simple formula."""
        f = Formula("x+1")
        tex = f.TeX()
        assert "x" in tex
    
    def test_tex_fraction(self):
        """Test TeX for fraction."""
        f = Formula("x/2")
        tex = f.TeX()
        assert "frac" in tex or "/" in tex


class TestComputeWithFormula:
    """Test Compute() function with formulas."""
    
    def test_compute_variable_returns_formula(self):
        """Test that Compute with variable returns Formula."""
        result = Compute("x")
        assert isinstance(result, Formula)
    
    def test_compute_expression_returns_formula(self):
        """Test that Compute with expression returns Formula."""
        result = Compute("x^2 + 1")
        assert isinstance(result, Formula)
    
    def test_compute_constant_returns_real(self):
        """Test that Compute with constant returns Real."""
        result = Compute("2 + 2")
        assert isinstance(result, Real)
        assert result.value == 4


class TestFormulaAnswerChecker:
    """Test Formula answer checking."""
    
    def test_formula_checker_correct(self):
        """Test formula checker with correct answer."""
        f = Formula("x^2 + 1")
        checker = f.cmp()
        result = checker.check("x^2 + 1")
        assert result['correct']
        assert result['score'] == 1.0
    
    def test_formula_checker_equivalent(self):
        """Test formula checker with equivalent answer."""
        f = Formula("x^2 + 2*x + 1")
        checker = f.cmp()
        result = checker.check("(x+1)^2")
        assert result['correct']
    
    def test_formula_checker_incorrect(self):
        """Test formula checker with incorrect answer."""
        f = Formula("x^2")
        checker = f.cmp()
        result = checker.check("x^3")
        assert not result['correct']
        assert result['score'] == 0.0
    
    def test_formula_checker_wrong_variables(self):
        """Test formula checker with wrong variables."""
        f = Formula("x^2")
        checker = f.cmp()
        result = checker.check("y^2")
        assert not result['correct']
