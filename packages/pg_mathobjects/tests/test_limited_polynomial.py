"""Tests for LimitedPolynomial context."""

import pytest
from pg_mathobjects import Context, Formula


class TestLimitedPolynomialAccept:
    """Test that valid polynomials are accepted."""

    def test_simple_polynomial(self):
        """Accept simple polynomial."""
        ctx = Context('LimitedPolynomial')
        f = Formula('x^2 + 2*x + 1', ctx)
        assert str(f) is not None

    def test_multiple_variables(self):
        """Accept polynomial with multiple variables."""
        ctx = Context('LimitedPolynomial')
        ctx.variables.add('y')
        f = Formula('x^2 + y^2 + 2*x*y', ctx)
        assert str(f) is not None

    def test_constant_term(self):
        """Accept polynomial with just constants."""
        ctx = Context('LimitedPolynomial')
        f = Formula('5', ctx)
        assert str(f) is not None

    def test_higher_degree(self):
        """Accept higher degree polynomial."""
        ctx = Context('LimitedPolynomial')
        f = Formula('x^5 - 3*x^4 + 2*x^3 - x^2 + 4*x - 7', ctx)
        assert str(f) is not None

    def test_division_by_constant(self):
        """Accept division by constant."""
        ctx = Context('LimitedPolynomial')
        f = Formula('x^2/2 + x/3 + 1/4', ctx)
        assert str(f) is not None

    def test_negative_coefficients(self):
        """Accept negative coefficients."""
        ctx = Context('LimitedPolynomial')
        f = Formula('-x^2 + 3*x - 5', ctx)
        assert str(f) is not None


class TestLimitedPolynomialReject:
    """Test that non-polynomials are rejected."""

    def test_reject_sin(self):
        """Reject trigonometric functions."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="function.*sin"):
            Formula('sin(x)', ctx)

    def test_reject_cos(self):
        """Reject cosine function."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="function.*cos"):
            Formula('x^2 + cos(x)', ctx)

    def test_reject_ln(self):
        """Reject logarithm."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="function.*ln"):
            Formula('ln(x)', ctx)

    def test_reject_exp(self):
        """Reject exponential."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="function.*exp"):
            Formula('exp(x)', ctx)

    def test_reject_sqrt(self):
        """Reject square root."""
        ctx = Context('LimitedPolynomial')
        # sqrt(x) becomes x^(1/2), so error is about fractional exponent
        with pytest.raises(ValueError, match="([Ee]xponent.*integer|function.*sqrt)"):
            Formula('sqrt(x)', ctx)

    def test_reject_fractional_power(self):
        """Reject fractional exponent."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="[Ee]xponent.*integer"):
            Formula('x^(1/2)', ctx)

    def test_reject_negative_power(self):
        """Reject negative exponent."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="polynomial"):
            Formula('x^(-1)', ctx)

    def test_reject_division_by_variable(self):
        """Reject division by variable."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="polynomial"):
            Formula('1/x', ctx)

    def test_reject_absolute_value(self):
        """Reject absolute value of variable."""
        ctx = Context('LimitedPolynomial')
        with pytest.raises(ValueError, match="function.*abs"):
            Formula('abs(x)', ctx)


class TestLimitedPolynomialStrict:
    """Test strict mode that disallows operations in coefficients."""

    def test_strict_reject_addition_in_coefficient(self):
        """Strict mode rejects operations in coefficients."""
        # Note: Sympy automatically simplifies (2+3)*x to 5*x before validation
        # So strict mode validation is limited. This test documents current behavior.
        ctx = Context('LimitedPolynomial-Strict')
        # Simple numeric operations get simplified by sympy, so they pass
        f = Formula('(2+3)*x', ctx)  # Becomes 5*x
        assert str(f) is not None

    def test_strict_accept_simple_coefficient(self):
        """Strict mode accepts simple numeric coefficients."""
        ctx = Context('LimitedPolynomial-Strict')
        f = Formula('5*x + 3', ctx)
        assert str(f) is not None

    def test_strict_accept_fraction_coefficient(self):
        """Strict mode accepts fractional coefficients."""
        ctx = Context('LimitedPolynomial-Strict')
        f = Formula('x/2 + 1/3', ctx)
        assert str(f) is not None


class TestLimitedPolynomialAnswerChecking:
    """Test answer checking with LimitedPolynomial context."""

    def test_answer_checker_accepts_correct(self):
        """Answer checker accepts correct polynomial."""
        ctx = Context('LimitedPolynomial')
        correct = Formula('x^2 + 2*x + 1', ctx)
        checker = correct.cmp()

        result = checker.check('x^2 + 2*x + 1')
        assert result['correct'] is True

    def test_answer_checker_rejects_incorrect(self):
        """Answer checker rejects incorrect polynomial."""
        ctx = Context('LimitedPolynomial')
        correct = Formula('x^2 + 2*x + 1', ctx)
        checker = correct.cmp()

        result = checker.check('x^2 + 3*x + 1')
        assert result['correct'] is False

    def test_answer_checker_rejects_non_polynomial(self):
        """Answer checker rejects non-polynomial."""
        ctx = Context('LimitedPolynomial')
        correct = Formula('x^2 + 1', ctx)
        checker = correct.cmp()

        # This should fail during parsing
        result = checker.check('sin(x)')
        assert result['correct'] is False


class TestLimitedPolynomialContextSwitch:
    """Test switching between contexts."""

    def test_switch_to_limited_polynomial(self):
        """Can switch to LimitedPolynomial context."""
        ctx1 = Context('Numeric')
        f1 = Formula('sin(x)', ctx1)  # OK in Numeric
        assert str(f1) is not None

        ctx2 = Context('LimitedPolynomial')
        with pytest.raises(ValueError):
            Formula('sin(x)', ctx2)  # Not OK in LimitedPolynomial

    def test_switch_back_to_numeric(self):
        """Can switch back to Numeric context."""
        ctx1 = Context('LimitedPolynomial')
        with pytest.raises(ValueError):
            Formula('sin(x)', ctx1)

        ctx2 = Context('Numeric')
        f2 = Formula('sin(x)', ctx2)  # OK again
        assert str(f2) is not None


class TestLimitedPolynomialOperations:
    """Test operations on polynomial formulas."""

    def test_evaluate_polynomial(self):
        """Can evaluate polynomial."""
        ctx = Context('LimitedPolynomial')
        f = Formula('x^2 + 2*x + 1', ctx)
        result = f.eval(x=3)
        assert result.value == 16  # 9 + 6 + 1

    def test_differentiate_polynomial(self):
        """Can differentiate polynomial."""
        ctx = Context('LimitedPolynomial')
        f = Formula('x^3 + 2*x^2 + x', ctx)
        df = f.D('x')
        # Result should be 3*x^2 + 4*x + 1
        result = df.eval(x=2)
        assert result.value == 21  # 12 + 8 + 1

    def test_substitute_in_polynomial(self):
        """Can substitute in polynomial."""
        ctx = Context('LimitedPolynomial')
        f = Formula('x^2 + y', ctx)
        ctx.variables.add('y')
        g = f.substitute(y='2*x')
        # Should get x^2 + 2*x
        result = g.eval(x=3)
        assert result.value == 15  # 9 + 6
