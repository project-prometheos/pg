"""
Test Week 4 Day 5: Advanced Tutorial Problems

Tests MathObjects with calculus (derivatives, integrals) and advanced algebra problems.
"""

import pytest
from pg_translator.in_process_sandbox import InProcessSandbox


class TestDifferentiation:
    """Test derivative problems from DifferentiateFunction.pg."""

    def test_basic_derivative(self):
        """Test basic derivative with D() method."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Function: k*x^2
f = Formula("k*x^2")

# Derivative: 2*k*x
df = f.D('x')

# Evaluate derivative (conceptually df should be a Formula)
result = df
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('df') is not None

    def test_derivative_with_substitution(self):
        """Test derivative with variable substitution."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Function with parameter
f = Formula("k*x^2")

# Derivative
fx = f.D('x')  # 2*k*x

# Substitute k=3
ans2 = fx.substitute(k=3)  # Should give Formula("2*3*x") or similar

result = {"fx": fx, "ans2": ans2}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['fx'] is not None
        assert result_dict['ans2'] is not None

    def test_derivative_with_evaluation(self):
        """Test derivative evaluation at a point."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# f(x) = 3*x^2
# f'(x) = 6*x
# f'(2) = 12

f = Formula("3*x^2")
df = f.D('x')
val = df.eval(x=2)  # Should be 12

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert val.value == 12

    def test_derivative_power_rule(self):
        """Test power rule for derivatives."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Test various power rule cases
f1 = Formula("x^3")
df1 = f1.D('x')
val1 = df1.eval(x=2)  # 3*x^2 at x=2 = 12

f2 = Formula("x^4")
df2 = f2.D('x')
val2 = df2.eval(x=1)  # 4*x^3 at x=1 = 4

result = {"val1": val1, "val2": val2}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['val1'].value == 12
        assert result_dict['val2'].value == 4


class TestIndefiniteIntegrals:
    """Test indefinite integral problems."""

    def test_antiderivative_creation(self):
        """Test creating antiderivative formulas."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Specific antiderivative (without +C)
# For integral of e^x, answer is e^x
specific = Formula("e^x")

# Verify it can be evaluated
val = specific.eval(x=0)  # e^0 = 1

result = {"specific": specific, "val": val}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['val'].value == pytest.approx(1.0, rel=1e-10)

    def test_polynomial_antiderivative(self):
        """Test polynomial antiderivative."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Integral of 2x is x^2
antider = Formula("x^2")

# Verify: derivative should give back 2x
f = antider.D('x')
val = f.eval(x=3)  # 2*3 = 6

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert val.value == 6

    def test_antiderivative_equivalence(self):
        """Test that antiderivatives differing by constant are equivalent."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Two formulas differing by constant
f1 = Formula("x^2")
f2 = Formula("x^2 + 5")

# Their derivatives should be identical
df1 = f1.D('x')
df2 = f2.D('x')

# Evaluate both at x=3, should both be 6
val1 = df1.eval(x=3)
val2 = df2.eval(x=3)

result = {"val1": val1, "val2": val2, "equal": val1.value == val2.value}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['equal'] == True


class TestTrigFunctions:
    """Test trigonometric functions."""

    def test_sin_cos_formula(self):
        """Test sin and cos in formulas."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula
import math

# f(x) = sin(x)
f = Formula("sin(x)")

# Evaluate at pi/2 (should be 1)
val = f.eval(x=math.pi/2)

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert val.value == pytest.approx(1.0, rel=1e-10)

    def test_trig_derivative(self):
        """Test derivatives of trig functions."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula
import math

# f(x) = sin(x), f'(x) = cos(x)
f = Formula("sin(x)")
df = f.D('x')

# Evaluate cos at 0 (should be 1)
val = df.eval(x=0)

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert val.value == pytest.approx(1.0, rel=1e-10)

    def test_cos_derivative(self):
        """Test derivative of cos(x)."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula
import math

# f(x) = cos(x), f'(x) = -sin(x)
f = Formula("cos(x)")
df = f.D('x')

# Evaluate -sin at 0 (should be 0)
val = df.eval(x=0)

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert abs(val.value) < 1e-10  # Should be very close to 0


class TestPolynomialFactoring:
    """Test polynomial factoring (basic support)."""

    def test_expanded_to_factored(self):
        """Test that factored and expanded forms evaluate the same."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# Expanded: 8x^2 + 28x + 12
expanded = Formula("8*x^2 + 28*x + 12")

# Factored: 4(2x+1)(x+3)
# = 4(2x^2 + 6x + x + 3)
# = 4(2x^2 + 7x + 3)
# = 8x^2 + 28x + 12
factored = Formula("4*(2*x+1)*(x+3)")

# Evaluate both at x=2
val_exp = expanded.eval(x=2)  # 8*4 + 28*2 + 12 = 32 + 56 + 12 = 100
val_fac = factored.eval(x=2)  # 4*(4+1)*(2+3) = 4*5*5 = 100

result = {"val_exp": val_exp, "val_fac": val_fac, "equal": val_exp.value == val_fac.value}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['equal'] == True
        assert result_dict['val_exp'].value == 100

    def test_simple_factoring(self):
        """Test simple factoring pattern."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# x^2 - 1 = (x-1)(x+1)
expanded = Formula("x^2 - 1")
factored = Formula("(x-1)*(x+1)")

# Test at several points
vals = []
for x_val in [0, 2, -1, 3]:
    v1 = expanded.eval(x=x_val)
    v2 = factored.eval(x=x_val)
    vals.append(v1.value == v2.value)

result = all(vals)  # All should be True
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('result') == True


class TestContextFlags:
    """Test context flag usage from tutorial problems."""

    def test_reduce_constants_flag(self):
        """Test reduceConstants context flag."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Context, Formula

# Note: Context flags not fully implemented yet
# But we can test basic usage
Context('Numeric')

# This should work even without full flag support
f = Formula("2*x + 3")
val = f.eval(x=5)  # 2*5 + 3 = 13

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert val.value == 13

    def test_variables_add(self):
        """Test adding variables to context."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Context, Formula

# Add variable k
Context('Numeric')
# Context().variables->add(k => 'Real')  # Perl syntax
# In Python, this would be:
# Context().variables.add('k', 'Real')

# For now, just create formula with k (should work anyway)
f = Formula("k*x^2")
result = f
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('result') is not None


class TestExponentialFunctions:
    """Test exponential and logarithmic functions."""

    def test_exp_function(self):
        """Test e^x in formulas."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula
import math

# f(x) = e^x
f = Formula("exp(x)")

# Evaluate at x=0 (should be 1)
val0 = f.eval(x=0)

# Evaluate at x=1 (should be e ≈ 2.718)
val1 = f.eval(x=1)

result = {"val0": val0, "val1": val1}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['val0'].value == pytest.approx(1.0, rel=1e-10)
        assert result_dict['val1'].value == pytest.approx(
            2.718281828, rel=1e-8)

    def test_exp_derivative(self):
        """Test derivative of e^x is e^x."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# f(x) = e^x, f'(x) = e^x
f = Formula("exp(x)")
df = f.D('x')

# Evaluate both at x=2
val_f = f.eval(x=2)
val_df = df.eval(x=2)

# Should be equal (e^x derivative is e^x)
result = {"val_f": val_f, "val_df": val_df, "equal": abs(val_f.value - val_df.value) < 1e-10}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['equal'] == True

    def test_log_function(self):
        """Test natural logarithm."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula
import math

# f(x) = ln(x)
f = Formula("log(x)")

# ln(1) = 0
val1 = f.eval(x=1)

# ln(e) = 1
val_e = f.eval(x=math.e)

result = {"val1": val1, "val_e": val_e}
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert abs(result_dict['val1'].value) < 1e-10
        assert result_dict['val_e'].value == pytest.approx(1.0, rel=1e-10)


class TestComplexFormulas:
    """Test more complex formula patterns."""

    def test_product_rule_setup(self):
        """Test formula setup for product rule problems."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# f(x) = x * sin(x)
f = Formula("x*sin(x)")

# f'(x) = sin(x) + x*cos(x)  (product rule)
df = f.D('x')

# Evaluate at x=0: sin(0) + 0*cos(0) = 0
val = df.eval(x=0)

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert abs(val.value) < 1e-10

    def test_chain_rule_setup(self):
        """Test formula setup for chain rule problems."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# f(x) = sin(x^2)
f = Formula("sin(x^2)")

# f'(x) = cos(x^2) * 2x  (chain rule)
df = f.D('x')

# Just verify derivative exists
result = df
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('result') is not None

    def test_quotient_formula(self):
        """Test formulas with division."""
        sandbox = InProcessSandbox()

        code = """
from pg_mathobjects import Formula

# f(x) = x^2 / x = x (simplified)
f = Formula("x^2 / x")

# Evaluate at x=5
val = f.eval(x=5)

result = val
"""

        result = sandbox.execute(code, seed=123)
        assert result.success
        val = sandbox.namespace.get('result')
        assert val.value == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
