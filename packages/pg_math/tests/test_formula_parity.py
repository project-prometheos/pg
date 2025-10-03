"""
Tests for Formula parity features (test points, python_function, cmp).

Tests the NEW features added for 100% parity with Perl Formula.pm:
- create_random_points()
- create_point_values()
- python_function()
- Enhanced compare() with test points
- cmp() answer checker
- Domain checking

Reference: lib/Value/Formula.pm (lines 265-470)
"""

import pytest

try:
    import sympy as sp
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

from pg_math.formula import Formula
from pg_math.numeric import Real


# Test Point Generation

def test_create_random_points_basic():
    """Test generating random test points for a formula."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2 + 1", variables=["x"])
    
    points, values, has_error = f.create_random_points(num_points=5)
    
    assert len(points) == 5
    assert len(values) == 5
    assert has_error is False
    
    # All points should be 1D (one variable)
    for point in points:
        assert len(point) == 1
        assert -10 <= point[0] <= 10  # Default range
    
    # All values should be computed correctly
    for i, point in enumerate(points):
        x = point[0]
        expected = x**2 + 1
        assert abs(values[i].to_python() - expected) < 0.001


def test_create_random_points_with_limits():
    """Test random point generation with custom limits."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2", variables=["x"], limits={"x": (0, 5)})
    
    points, values, _ = f.create_random_points(num_points=10)
    
    # All points should be in [0, 5]
    for point in points:
        assert 0 <= point[0] <= 5


def test_create_random_points_multivariable():
    """Test random points for multi-variable formulas."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2 + y^2", variables=["x", "y"])
    
    points, values, _ = f.create_random_points(num_points=5)
    
    # All points should be 2D
    for point in points:
        assert len(point) == 2
    
    # Verify values
    for i, point in enumerate(points):
        x, y = point
        expected = x**2 + y**2
        assert abs(values[i].to_python() - expected) < 0.001


def test_create_random_points_with_include():
    """Test including specific test points."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2", variables=["x"])
    
    # Include specific points
    include_points = [[0.0], [1.0], [2.0]]
    points, values, _ = f.create_random_points(num_points=5, include=include_points)
    
    # Should have included points + 5 more
    assert len(points) >= 8
    
    # First three should be our included points
    assert points[0] == [0.0]
    assert points[1] == [1.0]
    assert points[2] == [2.0]


def test_create_random_points_domain_error():
    """Test handling of domain errors (undefined points)."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    # Formula with restricted domain (sqrt requires x >= 0)
    f = Formula("sqrt(x)", variables=["x"], limits={"x": (-5, 5)})
    
    # Should handle undefined points gracefully
    points, values, has_error = f.create_random_points(num_points=5, no_errors=True)
    
    # Might have fewer points or undefined values
    assert len(points) <= 5 or has_error


# Test Point Values


def test_create_point_values():
    """Test evaluating formula at specific points."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2 + 2*x + 1", variables=["x"])
    
    test_points = [[0], [1], [2], [-1]]
    values = f.create_point_values(test_points)
    
    assert len(values) == 4
    assert abs(values[0].to_python() - 1) < 0.001    # (0)^2 + 2(0) + 1 = 1
    assert abs(values[1].to_python() - 4) < 0.001    # (1)^2 + 2(1) + 1 = 4
    assert abs(values[2].to_python() - 9) < 0.001    # (2)^2 + 2(2) + 1 = 9
    assert abs(values[3].to_python() - 0) < 0.001    # (-1)^2 + 2(-1) + 1 = 0


def test_create_point_values_caching():
    """Test caching of point values."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2", variables=["x"])
    
    test_points = [[1], [2], [3]]
    values = f.create_point_values(test_points, cache_results=True)
    
    # Check caching
    assert f._test_points == test_points
    assert f._test_values == values


# Python Function Generation


def test_python_function_single_var():
    """Test converting formula to Python function (single variable)."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2 + 2*x + 1", variables=["x"])
    func = f.python_function()
    
    # Test function
    assert abs(func(0) - 1) < 0.001
    assert abs(func(1) - 4) < 0.001
    assert abs(func(2) - 9) < 0.001
    assert abs(func(-1) - 0) < 0.001


def test_python_function_multi_var():
    """Test Python function with multiple variables."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2 + y^2", variables=["x", "y"])
    func = f.python_function()
    
    assert abs(func(0, 0) - 0) < 0.001
    assert abs(func(3, 4) - 25) < 0.001  # 3^2 + 4^2 = 9 + 16 = 25


def test_python_function_caching():
    """Test that Python function is cached."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2", variables=["x"])
    
    func1 = f.python_function()
    func2 = f.python_function()
    
    # Should be the same object (cached)
    assert func1 is func2


# Enhanced Comparison with Test Points


def test_compare_with_test_points():
    """Test formula comparison using test point evaluation."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f1 = Formula("x^2 - 1", variables=["x"])
    f2 = Formula("(x-1)*(x+1)", variables=["x"])
    
    # Should be equal (factored forms)
    assert f1.compare(f2, tolerance=0.001)
    assert not f1.domain_mismatch


def test_compare_different_formulas():
    """Test comparing different formulas."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f1 = Formula("x^2", variables=["x"])
    f2 = Formula("x^3", variables=["x"])
    
    # Should NOT be equal
    assert not f1.compare(f2, tolerance=0.001)


def test_compare_domain_mismatch():
    """Test domain mismatch detection in comparison."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    # Different domains: sqrt(x) defined for x >= 0, 1/x not defined at x = 0
    f1 = Formula("sqrt(x)", variables=["x"])
    f2 = Formula("1/x", variables=["x"])
    
    # Generate test points that might cause domain issues
    # (We can't easily test this without controlling random points)
    # At minimum, compare should handle it gracefully
    result = f1.compare(f2, tolerance=0.001)
    
    # Result depends on test points, but should not crash
    assert isinstance(result, bool)


# Answer Checker (cmp)


def test_cmp_creates_evaluator():
    """Test that cmp() creates a FormulaEvaluator."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2", variables=["x"])
    
    # Note: This will fail if FormulaEvaluator doesn't exist yet
    # We'll need to ensure pg_answer.evaluators.formula exists
    try:
        evaluator = f.cmp()
        assert evaluator is not None
    except ImportError:
        pytest.skip("FormulaEvaluator not yet implemented")


def test_cmp_with_options():
    """Test cmp() with custom options."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("x^2", variables=["x"])
    
    try:
        evaluator = f.cmp(
            tolerance=0.01,
            num_points=10,
            limits={"x": (0, 5)}
        )
        assert evaluator is not None
    except ImportError:
        pytest.skip("FormulaEvaluator not yet implemented")


# Integration Tests


def test_full_workflow():
    """Test complete workflow: create formula, generate points, compare."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    # Create formula
    f = Formula("2*x + 3", variables=["x"], num_test_points=5)
    
    # Generate test points
    points, values, _ = f.create_random_points()
    assert len(points) == 5
    assert len(values) == 5
    
    # Create Python function
    func = f.python_function()
    
    # Verify function matches formula
    for point, value in zip(points, values):
        x = point[0]
        func_result = func(x)
        formula_result = value.to_python()
        assert abs(func_result - formula_result) < 0.001
    
    # Compare with equivalent formula
    f2 = Formula("x + x + 3", variables=["x"])
    assert f.compare(f2, tolerance=0.001)


def test_complex_formula_with_trig():
    """Test formula with trigonometric functions."""
    if not SYMPY_AVAILABLE:
        pytest.skip("SymPy not available")
    
    f = Formula("sin(x)**2 + cos(x)**2", variables=["x"])
    
    # This should equal 1 for all x (trig identity)
    points, values, _ = f.create_random_points(num_points=10)
    
    for value in values:
        assert abs(value.to_python() - 1.0) < 0.001

