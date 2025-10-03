"""
Tests for Formula type (MathObjects).

Tests deferred evaluation, differentiation, simplification, and symbolic math.
Reference: t/value/Formula.t in legacy Perl codebase
"""

import pytest

try:
    import sympy as sp

    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

from pg_math.formula import Formula
from pg_math.numeric import Real, Complex
from pg_math.value import ToleranceMode


# Formula Creation and String Representation


def test_formula_from_string():
    """Test creating formula from string."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x^2 + 1", variables=["x"])
    assert "x" in f.to_string()
    assert f.variables == ["x"]


def test_formula_to_string():
    """Test formula string conversion."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("2*x + 3", variables=["x"])
    s = f.to_string()
    assert "x" in s


def test_formula_to_tex():
    """Test formula LaTeX conversion."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x^2", variables=["x"])
    tex = f.to_tex()
    assert "x" in tex
    assert "2" in tex  # Exponent


# Formula Evaluation


def test_formula_eval_simple():
    """Test evaluating formula with simple expression."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x + 1", variables=["x"])
    result = f.eval(x=5)

    assert isinstance(result, Real)
    assert result.compare(Real(6))


def test_formula_eval_polynomial():
    """Test evaluating polynomial formula."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x**2 + 2*x + 1", variables=["x"])
    result = f.eval(x=3)

    assert isinstance(result, Real)
    assert result.compare(Real(16))  # 9 + 6 + 1 = 16


def test_formula_eval_multiple_vars():
    """Test evaluating formula with multiple variables."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x*y + z", variables=["x", "y", "z"])
    result = f.eval(x=2, y=3, z=4)

    assert isinstance(result, Real)
    assert result.compare(Real(10))  # 2*3 + 4 = 10


def test_formula_eval_trig():
    """Test evaluating formula with trig functions."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    import math

    f = Formula("sin(x)", variables=["x"])
    result = f.eval(x=0)

    assert isinstance(result, Real)
    assert result.compare(Real(0), tolerance=0.0001)


def test_formula_eval_with_math_values():
    """Test evaluating formula with MathValue arguments."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x^2", variables=["x"])
    result = f.eval(x=Real(3))

    assert isinstance(result, Real)
    assert result.compare(Real(9))


# Differentiation


def test_formula_diff_simple():
    """Test differentiating simple formula."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x^2", variables=["x"])
    df = f.diff("x")

    assert isinstance(df, Formula)
    # d/dx(x^2) = 2*x
    assert df.eval(x=3).compare(Real(6))
    assert df.eval(x=5).compare(Real(10))


def test_formula_diff_polynomial():
    """Test differentiating polynomial."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x**3 + 2*x**2 + 3*x + 4", variables=["x"])
    df = f.diff("x")

    # d/dx(x^3 + 2x^2 + 3x + 4) = 3x^2 + 4x + 3
    assert df.eval(x=0).compare(Real(3))
    assert df.eval(x=1).compare(Real(10))  # 3 + 4 + 3 = 10
    assert df.eval(x=2).compare(Real(23))  # 12 + 8 + 3 = 23


def test_formula_diff_product():
    """Test differentiating product."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x**2 * sin(x)", variables=["x"])
    df = f.diff("x")

    # Product rule: d/dx(x^2 * sin(x)) = 2x*sin(x) + x^2*cos(x)
    import math

    result = df.eval(x=0)
    assert result.compare(Real(0), tolerance=0.0001)


def test_formula_diff_chain_rule():
    """Test differentiating with chain rule."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("sin(x**2)", variables=["x"])
    df = f.diff("x")

    # Chain rule: d/dx(sin(x^2)) = cos(x^2) * 2x
    # At x=0: cos(0) * 0 = 0
    assert df.eval(x=0).compare(Real(0), tolerance=0.0001)


# Integration


def test_formula_integrate_simple():
    """Test integrating simple formula."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("2*x", variables=["x"])
    F = f.integrate("x")

    assert isinstance(F, Formula)
    # ∫2x dx = x^2 + C (we ignore constant)
    # Verify: d/dx(result) = original
    assert F.diff("x").eval(x=5).compare(f.eval(x=5))


def test_formula_integrate_polynomial():
    """Test integrating polynomial."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("3*x**2 + 2*x", variables=["x"])
    F = f.integrate("x")

    # ∫(3x^2 + 2x) dx = x^3 + x^2 + C
    # Verify by differentiation
    assert F.diff("x").eval(x=3).compare(f.eval(x=3))


# Simplification


def test_formula_reduce_simple():
    """Test simplifying formula."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x + x", variables=["x"])
    reduced = f.reduce()

    assert isinstance(reduced, Formula)
    # x + x should simplify to 2*x
    assert reduced.eval(x=5).compare(Real(10))


def test_formula_reduce_expand():
    """Test simplification of expanded expression."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("(x + 1) * (x - 1)", variables=["x"])
    reduced = f.reduce()

    # (x+1)(x-1) = x^2 - 1
    assert reduced.eval(x=3).compare(Real(8))
    assert reduced.eval(x=5).compare(Real(24))


# Substitution


def test_formula_substitute_number():
    """Test substituting variable with number."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x^2 + y", variables=["x", "y"])
    g = f.substitute("x", 3)

    assert isinstance(g, Formula)
    assert "x" not in g.variables
    assert "y" in g.variables

    # After substituting x=3: 9 + y
    assert g.eval(y=1).compare(Real(10))
    assert g.eval(y=5).compare(Real(14))


def test_formula_substitute_math_value():
    """Test substituting variable with MathValue."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x + y", variables=["x", "y"])
    g = f.substitute("x", Real(5))

    # After substituting x=5: 5 + y
    assert g.eval(y=3).compare(Real(8))


# Comparison


def test_formula_compare_identical():
    """Test comparing identical formulas."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("x^2", variables=["x"])
    f2 = Formula("x^2", variables=["x"])

    assert f1.compare(f2)


def test_formula_compare_equivalent():
    """Test comparing equivalent formulas."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("x + x", variables=["x"])
    f2 = Formula("2*x", variables=["x"])

    assert f1.compare(f2)


def test_formula_compare_expanded():
    """Test comparing expanded vs factored."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("(x + 1) * (x - 1)", variables=["x"])
    f2 = Formula("x^2 - 1", variables=["x"])

    assert f1.compare(f2)


def test_formula_compare_different():
    """Test comparing different formulas."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("x^2", variables=["x"])
    f2 = Formula("x^3", variables=["x"])

    assert not f1.compare(f2)


def test_formula_compare_constant():
    """Test comparing formula with constant."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("5", variables=[])
    assert f.compare(Real(5))


# Arithmetic Operations


def test_formula_add():
    """Test formula addition."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("x", variables=["x"])
    f2 = Formula("2*x", variables=["x"])
    result = f1 + f2

    assert isinstance(result, Formula)
    assert result.eval(x=3).compare(Real(9))  # x + 2x = 3x, at x=3: 9


def test_formula_sub():
    """Test formula subtraction."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("3*x", variables=["x"])
    f2 = Formula("x", variables=["x"])
    result = f1 - f2

    assert isinstance(result, Formula)
    assert result.eval(x=5).compare(Real(10))  # 3x - x = 2x, at x=5: 10


def test_formula_mul():
    """Test formula multiplication."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("x", variables=["x"])
    f2 = Formula("x + 1", variables=["x"])
    result = f1 * f2

    assert isinstance(result, Formula)
    assert result.eval(x=3).compare(Real(12))  # x * (x+1), at x=3: 3 * 4 = 12


def test_formula_div():
    """Test formula division."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f1 = Formula("x^2", variables=["x"])
    f2 = Formula("x", variables=["x"])
    result = f1 / f2

    assert isinstance(result, Formula)
    assert result.eval(x=5).compare(Real(5))  # x^2 / x = x


def test_formula_pow():
    """Test formula exponentiation."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x", variables=["x"])
    result = f ** 3

    assert isinstance(result, Formula)
    assert result.eval(x=2).compare(Real(8))  # x^3, at x=2: 8


def test_formula_neg():
    """Test formula negation."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x", variables=["x"])
    result = -f

    assert isinstance(result, Formula)
    assert result.eval(x=5).compare(Real(-5))


def test_formula_add_number():
    """Test formula + number."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x", variables=["x"])
    result = f + 5

    assert isinstance(result, Formula)
    assert result.eval(x=3).compare(Real(8))


def test_formula_mul_number():
    """Test formula * number."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x", variables=["x"])
    result = f * 3

    assert isinstance(result, Formula)
    assert result.eval(x=4).compare(Real(12))


# Edge Cases


def test_formula_no_variables():
    """Test formula with no variables (constant)."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("2 + 3", variables=[])
    result = f.eval()

    assert isinstance(result, Real)
    assert result.compare(Real(5))


def test_formula_complex_expression():
    """Test complex mathematical expression."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    import math

    f = Formula("exp(x) * sin(x)", variables=["x"])
    result = f.eval(x=0)

    # exp(0) * sin(0) = 1 * 0 = 0
    assert result.compare(Real(0), tolerance=0.0001)


def test_formula_to_python():
    """Test converting formula to Python value."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("2 + 3", variables=[])
    python_val = f.to_python()

    # Should evaluate to 5
    assert python_val == 5.0 or python_val == 5


def test_formula_from_sympy():
    """Test creating formula from SymPy expression."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    x = sp.Symbol("x")
    expr = x**2 + 2 * x + 1

    f = Formula(expr, variables=["x"])
    assert f.eval(x=3).compare(Real(16))


# Type Promotion


def test_formula_type_precedence():
    """Test that Formula has highest type precedence."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    from pg_math.value import TypePrecedence

    assert Formula.type_precedence == TypePrecedence.FORMULA


def test_formula_promote():
    """Test that Formula doesn't need promotion."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")

    f = Formula("x", variables=["x"])
    r = Real(5)

    promoted = f.promote(r)
    assert promoted is f  # No promotion needed
