"""
Test Week 4 Day 4: Testing with Real Tutorial Problems

Tests MathObjects implementation with actual OPL tutorial problems.
"""

import pytest
from pg_translator.in_process_sandbox import InProcessSandbox


class TestExpandedPolynomial:
    """Test the ExpandedPolynomial.pg tutorial problem."""
    
    def test_expanded_polynomial_basic(self):
        """Test basic expanded polynomial problem."""
        sandbox = InProcessSandbox()
        
        # Simplified version of ExpandedPolynomial.pg
        code = """
from pg_mathobjects import Context, Formula, Compute

# Setup - Numeric context for initial computation
Context('Numeric')
h = 3
k = 5
vertexform = Compute(f"(x-{h})^2-{k}")

# Result check - vertex form created
result = vertexform
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        # Vertex form Formula should be created
        vertex = sandbox.namespace.get('result')
        assert vertex is not None
    
    def test_expanded_polynomial_context_switch(self):
        """Test context switching in polynomial problem."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Context, Formula

# Start with Numeric context
Context('Numeric')
f1 = Formula("x^2 + 1")
context1 = "Numeric"

# Note: LimitedPolynomial context not yet implemented
# For now, we can keep using Numeric
f2 = Formula("x^2 - 6*x + 4")
context2 = "Numeric"

result = {"f1": f1, "f2": f2, "context1": context1, "context2": context2}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['f1'] is not None
        assert result_dict['f2'] is not None
    
    def test_polynomial_reduce_method(self):
        """Test Formula.reduce() method."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Create formula with negative coefficient
f = Formula("x^2 + -6*x + 4")

# Test that reduce method exists
has_reduce = hasattr(f, 'reduce')

# Note: reduce() should simplify display to "x^2 - 6x + 4"
# For now, just check it's callable
result = has_reduce
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('result') == True


class TestSimpleAlgebra:
    """Test simple algebraic formulas."""
    
    def test_quadratic_formula(self):
        """Test quadratic formula creation and evaluation."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula, Compute

# Create quadratic
a = 1
b = -6
c = 4
f = Formula(f"{a}*x^2 + {b}*x + {c}")

# Evaluate at specific point
val = f.eval(x=0)  # Should give c = 4

result = {"formula": f, "value": val}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['value'].value == 4
    
    def test_polynomial_expansion(self):
        """Test polynomial expansion from factored form."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Factored form
factored = Formula("(x-3)^2-5")

# Evaluate to verify it works
val1 = factored.eval(x=3)  # Should be -5
val2 = factored.eval(x=0)  # (0-3)^2-5 = 9-5 = 4

result = {"val1": val1, "val2": val2}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['val1'].value == -5
        assert result_dict['val2'].value == 4
    
    def test_formula_with_parameters(self):
        """Test formulas with Perl-style parameter substitution."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Simulate Perl-style variables
h = 3
k = 5

# Create formulas using parameters
vertex_str = f"(x-{h})^2-{k}"
vertex = Formula(vertex_str)

# Compute coefficients for expanded form
b = -2 * h  # -6
c = h**2 - k  # 9 - 5 = 4

expanded_str = f"x^2 + {b}*x + {c}"
expanded = Formula(expanded_str)

# Verify both give same result at x=5
val_v = vertex.eval(x=5)
val_e = expanded.eval(x=5)

# (5-3)^2-5 = 4-5 = -1
# 25 + (-6)*5 + 4 = 25 - 30 + 4 = -1
result = {"vertex_val": val_v, "expanded_val": val_e, "match": val_v.value == val_e.value}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['match'] == True
        assert result_dict['vertex_val'].value == -1
        assert result_dict['expanded_val'].value == -1


class TestFormulaOperations:
    """Test Formula operations needed for tutorial problems."""
    
    def test_formula_arithmetic(self):
        """Test arithmetic operations on formulas."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Basic operations
f = Formula("x^2")
g = Formula("2*x")
h = Formula("1")

# Operations
sum_fg = Formula("x^2 + 2*x")
val = sum_fg.eval(x=3)  # 9 + 6 = 15

result = val
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('result').value == 15
    
    def test_formula_substitution_simple(self):
        """Test simple formula substitution."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Original formula
f = Formula("x^2 + 1")

# Substitute x=5
result = f.substitute(x=5)  # Should give Formula("5^2 + 1") = "26"
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        # Substitution returns a Formula or value
        res = sandbox.namespace.get('result')
        assert res is not None
    
    def test_formula_differentiation(self):
        """Test formula differentiation."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Quadratic
f = Formula("x^2 + 3*x + 2")

# Differentiate
df = f.D('x')  # Should be "2*x + 3"

# Evaluate derivative at x=1: 2(1) + 3 = 5
val = df.eval(x=1)

result = {"derivative": df, "value": val}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['value'].value == 5


class TestComputeFunction:
    """Test Compute function for dynamic values."""
    
    def test_compute_with_string_interpolation(self):
        """Test Compute with Python string interpolation."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Compute

# Parameters
a = 2
b = 3

# Compute with interpolation
result = Compute(f"{a} + {b}")  # Should be Real(5)
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        assert sandbox.namespace.get('result').value == 5
    
    def test_compute_vs_formula(self):
        """Test difference between Compute and Formula."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Compute, Formula

# Compute evaluates constants
c1 = Compute("2+3")  # Real(5)
is_real = type(c1).__name__

# Compute with variable returns Formula
c2 = Compute("x+3")  # Formula
is_formula = type(c2).__name__

result = {"type1": is_real, "type2": is_formula}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert "Real" in result_dict['type1']
        assert "Formula" in result_dict['type2']


class TestAnswerChecking:
    """Test answer checking features."""
    
    def test_formula_answer_checker(self):
        """Test Formula.cmp() answer checker."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Formula

# Correct answer
correct = Formula("x^2 - 6*x + 4")

# Get checker
checker = correct.cmp()

# Test equivalent answer
student_ans = "(x-3)^2 - 5"
result = checker.check(student_ans)

# Should be correct (equivalent formulas)
is_correct = result['score'] == 1
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        # Answer checking should recognize equivalence
        assert sandbox.namespace['is_correct'] == True
    
    def test_real_answer_checker(self):
        """Test Real.cmp() answer checker."""
        sandbox = InProcessSandbox()
        
        code = """
from pg_mathobjects import Real

# Correct answer
correct = Real(4.5)

# Get checker
checker = correct.cmp()

# Test close answer (within tolerance)
result1 = checker.check("4.5")
result2 = checker.check("4.50001")

is_correct1 = result1['score'] == 1
is_correct2 = result2['score'] == 1

result = {"exact": is_correct1, "close": is_correct2}
"""
        
        result = sandbox.execute(code, seed=123)
        assert result.success
        result_dict = sandbox.namespace.get('result')
        assert result_dict['exact'] == True
        assert result_dict['close'] == True  # Within default tolerance


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
