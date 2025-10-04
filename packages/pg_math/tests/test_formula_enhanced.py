"""
Tests for FormulaEnhanced with adaptive parameters and advanced features.
"""

import pytest
import math
from pg_math.formula_enhanced import FormulaEnhanced, UNDEF_VALUE
from pg_math import Real


def test_create_random_points_basic():
    """Test basic random point generation."""
    formula = FormulaEnhanced(
        "x^2 + y",
        variables=["x", "y"],
        num_test_points=10
    )

    points = formula.create_random_points()

    assert len(points) == 10
    assert all(len(p) == 2 for p in points)


def test_create_random_points_with_limits():
    """Test random points with custom limits."""
    formula = FormulaEnhanced(
        "x^2",
        variables=["x"],
        limits={"x": (-5, 5)},
        num_test_points=5
    )

    points = formula.create_random_points()

    # All points should be in range
    for point in points:
        assert -5 <= point[0] <= 5


def test_create_random_points_with_granularity():
    """Test random points with granularity."""
    formula = FormulaEnhanced(
        "x",
        variables=["x"],
        limits={"x": (0, 10)},
        granularity=100,  # 100 steps
        num_test_points=20
    )

    points = formula.create_random_points()

    # Points should be rounded to granularity
    for point in points:
        x = point[0]
        # Should be close to a multiple of step size (10/100 = 0.1)
        step = 10 / 100
        rounded = round(x / step) * step
        assert abs(x - rounded) < 1e-10


def test_create_random_points_test_at():
    """Test forcing specific test points."""
    formula = FormulaEnhanced(
        "x^2",
        variables=["x"],
        num_test_points=5
    )

    # Force test at x=0 and x=1
    points = formula.create_random_points(test_at={"x": [0, 1]})

    # Should have at least these points
    x_values = [p[0] for p in points]
    assert 0 in x_values or any(abs(x) < 1e-10 for x in x_values)
    assert 1 in x_values or any(abs(x - 1) < 1e-10 for x in x_values)


def test_create_point_values_basic():
    """Test basic point value evaluation."""
    formula = FormulaEnhanced(
        "x^2 + 1",
        variables=["x"],
        num_test_points=5
    )

    points = [[0], [1], [2], [3], [4]]
    values = formula.create_point_values(points)

    assert values is not None
    assert len(values) == 5
    assert abs(float(values[0]) - 1) < 1e-10  # 0^2 + 1 = 1
    assert abs(float(values[1]) - 2) < 1e-10  # 1^2 + 1 = 2
    assert abs(float(values[4]) - 17) < 1e-10  # 4^2 + 1 = 17


def test_create_point_values_with_caching():
    """Test point value caching."""
    formula = FormulaEnhanced(
        "x^2",
        variables=["x"],
        num_test_points=3
    )

    points = [[1], [2], [3]]
    values = formula.create_point_values(points, cache_results=True)

    # Should cache
    assert hasattr(formula, "_test_points")
    assert hasattr(formula, "_test_values")
    assert formula._test_points == points
    assert formula._test_values == values


def test_create_point_values_undefined():
    """Test handling undefined points (domain errors)."""
    formula = FormulaEnhanced(
        "1/x",
        variables=["x"],
        check_undefined_points=True,
        max_undefined=2
    )

    # Include x=0 which is undefined
    points = [[1], [0], [2]]
    values = formula.create_point_values(points, check_undefined=True)

    assert values is not None
    assert len(values) == 3
    assert isinstance(values[1], type(UNDEF_VALUE))  # x=0 is undefined


def test_python_function_generation():
    """Test Python function generation and caching."""
    formula = FormulaEnhanced(
        "x^2 + y^2",
        variables=["x", "y"]
    )

    func = formula.python_function()

    # Should be callable
    assert callable(func)

    # Test evaluation
    result = func(3, 4)
    assert abs(result - 25) < 1e-10  # 3^2 + 4^2 = 25

    # Should cache
    func2 = formula.python_function()
    assert func is func2  # Same object


def test_adapt_parameters_simple():
    """Test adaptive parameter solving - simple case."""
    # Correct answer: C * e^x (with parameter C)
    correct = FormulaEnhanced(
        "C * e^x",
        variables=["x"],
        parameters=["C"]
    )

    # Student answer: 5 * e^x
    student = FormulaEnhanced(
        "5 * e^x",
        variables=["x"]
    )

    # Should solve for C = 5
    result = correct.adapt_parameters(student)

    assert result is True
    assert hasattr(correct, "_parameters_values")
    assert len(correct._parameters_values) == 1
    assert abs(correct._parameters_values[0] - 5) < 1e-6


def test_adapt_parameters_two_params():
    """Test adaptive parameter solving - two parameters."""
    # This test requires numpy for 2x2 system solving
    try:
        import numpy
    except ImportError:
        pytest.skip("numpy not installed")

    # Correct: C1*sin(x) + C2*cos(x)
    correct = FormulaEnhanced(
        "C1*sin(x) + C2*cos(x)",
        variables=["x"],
        parameters=["C1", "C2"]
    )

    # Student: 3*sin(x) + 4*cos(x)
    student = FormulaEnhanced(
        "3*sin(x) + 4*cos(x)",
        variables=["x"]
    )

    result = correct.adapt_parameters(student)

    assert result is True
    assert len(correct._parameters_values) == 2
    assert abs(correct._parameters_values[0] - 3) < 1e-6  # C1
    assert abs(correct._parameters_values[1] - 4) < 1e-6  # C2


def test_adapt_parameters_max_adapt():
    """Test adaptive parameter with max_adapt constraint."""
    # Correct: C * x
    correct = FormulaEnhanced(
        "C * x",
        variables=["x"],
        parameters=["C"]
    )

    # Student: 1e10 * x (huge coefficient)
    student = FormulaEnhanced(
        "1e10 * x",
        variables=["x"]
    )

    # Should fail due to max_adapt limit
    with pytest.raises(ValueError, match="too large"):
        correct.adapt_parameters(student, max_adapt=1e8)


def test_adapt_parameters_no_params():
    """Test adapt_parameters returns False when no parameters."""
    correct = FormulaEnhanced(
        "x^2",
        variables=["x"],
        parameters=[]  # No parameters
    )

    student = FormulaEnhanced(
        "x^2 + 1",
        variables=["x"]
    )

    result = correct.adapt_parameters(student)
    assert result is False


def test_compare_basic():
    """Test basic formula comparison."""
    f1 = FormulaEnhanced("x^2", variables=["x"])
    f2 = FormulaEnhanced("x*x", variables=["x"])

    # Should be equivalent
    assert f1.compare(f2)


def test_compare_with_adaptive():
    """Test comparison with adaptive parameters."""
    # Correct: C * e^x
    correct = FormulaEnhanced(
        "C * e^x",
        variables=["x"],
        parameters=["C"]
    )

    # Student: 7 * e^x
    student = FormulaEnhanced(
        "7 * e^x",
        variables=["x"]
    )

    # Should match with adaptive
    assert correct.compare(student, use_adaptive=True)


def test_compare_without_adaptive():
    """Test that non-adaptive comparison fails when it should."""
    correct = FormulaEnhanced(
        "C * x",
        variables=["x"],
        parameters=["C"]
    )

    student = FormulaEnhanced(
        "5 * x",
        variables=["x"]
    )

    # Without adaptive, should not match (C defaults to 0)
    assert not correct.compare(student, use_adaptive=False)


def test_uses_one_of():
    """Test uses_one_of variable checking."""
    formula = FormulaEnhanced(
        "x + y",
        variables=["x", "y"]
    )

    assert formula.uses_one_of("x")
    assert formula.uses_one_of("y")
    assert formula.uses_one_of("x", "y")
    assert not formula.uses_one_of("z")
    assert formula.uses_one_of("x", "z")  # Has x


def test_solve_linear_system_1x1():
    """Test 1x1 linear system solving."""
    formula = FormulaEnhanced("x", variables=["x"])

    # Solve: 2*a = 6  =>  a = 3
    solution = formula._solve_linear_system([[2]], [6])

    assert solution is not None
    assert len(solution) == 1
    assert abs(solution[0] - 3) < 1e-10


def test_solve_linear_system_2x2():
    """Test 2x2 linear system solving."""
    formula = FormulaEnhanced("x", variables=["x"])

    # Solve: 2*a + 3*b = 8
    #        4*a + 1*b = 10
    # Solution: a=2, b=4/3
    A = [[2, 3], [4, 1]]
    b = [8, 10]

    solution = formula._solve_linear_system(A, b)

    assert solution is not None
    assert len(solution) == 2
    assert abs(solution[0] - 2) < 1e-6
    assert abs(solution[1] - 4/3) < 1e-6


def test_solve_linear_system_singular():
    """Test singular system returns None."""
    formula = FormulaEnhanced("x", variables=["x"])

    # Singular: determinant = 0
    A = [[1, 2], [2, 4]]
    b = [3, 6]

    solution = formula._solve_linear_system(A, b)
    assert solution is None


def test_create_adapted_values():
    """Test creation of adapted values."""
    formula = FormulaEnhanced(
        "C * x^2",
        variables=["x"],
        parameters=["C"]
    )

    # Set adapted parameter value
    formula._parameters_values = [3]  # C = 3

    # Create adapted values
    formula._test_points = [[1], [2], [3]]
    values = formula._create_adapted_values()

    assert len(values) == 3
    assert abs(float(values[0]) - 3) < 1e-10   # 3 * 1^2 = 3
    assert abs(float(values[1]) - 12) < 1e-10  # 3 * 2^2 = 12
    assert abs(float(values[2]) - 27) < 1e-10  # 3 * 3^2 = 27


def test_tolerance_transfer():
    """Test that tolerance flags are transferred to values."""
    formula = FormulaEnhanced(
        "x^2",
        variables=["x"]
    )

    # Set tolerance
    formula.tolerance = 0.01
    formula.tolType = "relative"

    values = formula.create_point_values([[1], [2]])

    # Check flags transferred
    for value in values:
        assert hasattr(value, "tolerance")
        assert value.tolerance == 0.01
        assert hasattr(value, "tolType")
        assert value.tolType == "relative"


def test_integration_adaptive_workflow():
    """Test complete adaptive workflow from problem authoring perspective."""
    # This is how a problem author would use adaptive parameters

    # Define correct answer with parameter for constant of integration
    correct_answer = FormulaEnhanced(
        "x^2 + C0",  # C0 is constant of integration
        variables=["x"],
        parameters=["C0"]
    )

    # Student submits: x^2 + 7
    student_answer = FormulaEnhanced(
        "x^2 + 7",
        variables=["x"]
    )

    # Check if they match (should solve C0 = 7)
    is_correct = correct_answer.compare(student_answer, use_adaptive=True)

    assert is_correct
    assert abs(correct_answer._parameters_dict["C0"] - 7) < 1e-6


def test_multi_variable_adaptive():
    """Test adaptive parameters with multiple variables."""
    # Correct: C * x * y
    correct = FormulaEnhanced(
        "C * x * y",
        variables=["x", "y"],
        parameters=["C"]
    )

    # Student: 2.5 * x * y
    student = FormulaEnhanced(
        "2.5 * x * y",
        variables=["x", "y"]
    )

    result = correct.adapt_parameters(student)

    assert result is True
    assert abs(correct._parameters_values[0] - 2.5) < 1e-6
