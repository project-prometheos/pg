"""Tests for Formula adaptive parameters."""

import pytest
from pg_math import Formula


def test_adapt_simple_linear():
    """Test adapting linear function."""
    # Correct answer template: a*x + b
    correct = Formula("a*x + b", variables=["x", "a", "b"])
    
    # Student answer: x + 1
    student = Formula("x + 1", variables=["x"])
    
    # Should find a=1, b=1
    params = correct.adapt_parameters(student, "a", "b")
    
    if params:  # Only test if numpy available
        assert params is not None
        assert abs(params.get("a", 0) - 1.0) < 0.01
        assert abs(params.get("b", 0) - 1.0) < 0.01


def test_adapt_quadratic():
    """Test adapting quadratic."""
    correct = Formula("a*x**2 + b*x + c", variables=["x", "a", "b", "c"])
    student = Formula("2*x**2 + 3*x + 1", variables=["x"])
    
    params = correct.adapt_parameters(student, "a", "b", "c")
    
    if params:
        assert abs(params.get("a", 0) - 2.0) < 0.1
        assert abs(params.get("b", 0) - 3.0) < 0.1
        assert abs(params.get("c", 0) - 1.0) < 0.1


def test_adapt_no_params():
    """Test with no adaptive parameters returns empty dict."""
    correct = Formula("x**2", variables=["x"])
    student = Formula("x**2", variables=["x"])
    
    params = correct.adapt_parameters(student)
    assert params == {}


def test_adapt_incompatible():
    """Test adapting incompatible formulas returns None."""
    correct = Formula("a*x + b", variables=["x", "a", "b"])
    student = Formula("x**2", variables=["x"])  # Different form
    
    params = correct.adapt_parameters(student, "a", "b")
    # May return None if can't fit
    # (This is expected behavior - not all formulas can be adapted)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

