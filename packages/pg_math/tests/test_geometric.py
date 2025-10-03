"""Unit tests for geometric MathValue types."""

import math

import numpy as np
import pytest

from pg_math import Matrix, Point, Real, Vector


class TestPoint:
    """Tests for Point type."""

    def test_create_point(self):
        """Test creating a point."""
        p = Point([1.0, 2.0, 3.0])
        assert len(p) == 3
        assert p[0].value == 1.0
        assert p[1].value == 2.0
        assert p[2].value == 3.0

    def test_point_from_floats(self):
        """Test creating point from Python floats."""
        p = Point([1.0, 2.0])
        assert isinstance(p[0], Real)
        assert p[0].value == 1.0

    def test_point_addition(self):
        """Test point + vector = point."""
        p1 = Point([1.0, 2.0])
        v = Vector([3.0, 4.0])
        result = p1 + v
        assert isinstance(result, Point)
        assert result[0].value == 4.0
        assert result[1].value == 6.0

    def test_point_subtraction_gives_vector(self):
        """Test point - point = vector."""
        p1 = Point([5.0, 7.0])
        p2 = Point([2.0, 3.0])
        result = p1 - p2
        assert isinstance(result, Vector)
        assert result[0].value == 3.0
        assert result[1].value == 4.0

    def test_point_distance(self):
        """Test distance calculation."""
        p1 = Point([0.0, 0.0])
        p2 = Point([3.0, 4.0])
        dist = p1.distance(p2)
        assert isinstance(dist, Real)
        assert dist.value == 5.0  # 3-4-5 triangle

    def test_point_magnitude(self):
        """Test point magnitude (distance from origin)."""
        p = Point([3.0, 4.0])
        mag = abs(p)
        assert isinstance(mag, Real)
        assert mag.value == 5.0

    def test_point_negation(self):
        """Test point negation."""
        p = Point([1.0, 2.0])
        result = -p
        assert isinstance(result, Point)
        assert result[0].value == -1.0
        assert result[1].value == -2.0

    def test_point_comparison(self):
        """Test point fuzzy comparison."""
        p1 = Point([1.0, 2.0])
        p2 = Point([1.001, 2.001])
        assert p1.compare(p2, tolerance=0.01)
        assert not p1.compare(p2, tolerance=0.0001)

    def test_point_to_string(self):
        """Test string conversion."""
        p = Point([1.0, 2.0, 3.0])
        assert p.to_string() == "(1, 2, 3)"

    def test_point_to_python(self):
        """Test Python conversion."""
        p = Point([1.0, 2.0])
        result = p.to_python()
        assert result == (1.0, 2.0)
        assert isinstance(result, tuple)


class TestVector:
    """Tests for Vector type."""

    def test_create_vector(self):
        """Test creating a vector."""
        v = Vector([1.0, 2.0, 3.0])
        assert len(v) == 3
        assert v[0].value == 1.0

    def test_vector_addition(self):
        """Test vector addition."""
        v1 = Vector([1.0, 2.0])
        v2 = Vector([3.0, 4.0])
        result = v1 + v2
        assert isinstance(result, Vector)
        assert result[0].value == 4.0
        assert result[1].value == 6.0

    def test_vector_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector([5.0, 7.0])
        v2 = Vector([2.0, 3.0])
        result = v1 - v2
        assert isinstance(result, Vector)
        assert result[0].value == 3.0
        assert result[1].value == 4.0

    def test_scalar_multiplication(self):
        """Test scalar multiplication."""
        v = Vector([1.0, 2.0, 3.0])
        result = v * 2
        assert isinstance(result, Vector)
        assert result[0].value == 2.0
        assert result[1].value == 4.0
        assert result[2].value == 6.0

        # Right multiplication
        result2 = 3 * v
        assert result2[0].value == 3.0

    def test_scalar_division(self):
        """Test scalar division."""
        v = Vector([2.0, 4.0, 6.0])
        result = v / 2
        assert isinstance(result, Vector)
        assert result[0].value == 1.0
        assert result[1].value == 2.0
        assert result[2].value == 3.0

    def test_vector_norm(self):
        """Test vector norm (magnitude)."""
        v = Vector([3.0, 4.0])
        norm = v.norm()
        assert isinstance(norm, Real)
        assert norm.value == 5.0

    def test_vector_unit(self):
        """Test unit vector."""
        v = Vector([3.0, 4.0])
        unit = v.unit()
        assert isinstance(unit, Vector)
        assert abs(unit.norm().value - 1.0) < 1e-10

    def test_dot_product(self):
        """Test dot product."""
        v1 = Vector([1.0, 2.0, 3.0])
        v2 = Vector([4.0, 5.0, 6.0])
        result = v1.dot(v2)
        assert isinstance(result, Real)
        assert result.value == 32.0  # 1*4 + 2*5 + 3*6 = 32

        # Also test with * operator
        result2 = v1 * v2
        assert result2.value == 32.0

    def test_cross_product(self):
        """Test cross product (3D only)."""
        v1 = Vector([1.0, 0.0, 0.0])
        v2 = Vector([0.0, 1.0, 0.0])
        result = v1.cross(v2)
        assert isinstance(result, Vector)
        assert result[0].value == 0.0
        assert result[1].value == 0.0
        assert result[2].value == 1.0  # i × j = k

    def test_is_parallel(self):
        """Test parallel vector detection."""
        v1 = Vector([1.0, 2.0, 3.0])
        v2 = Vector([2.0, 4.0, 6.0])  # 2 * v1
        assert v1.is_parallel(v2)

        v3 = Vector([1.0, 0.0, 0.0])
        assert not v1.is_parallel(v3)

    def test_is_orthogonal(self):
        """Test orthogonal (perpendicular) vector detection."""
        v1 = Vector([1.0, 0.0, 0.0])
        v2 = Vector([0.0, 1.0, 0.0])
        assert v1.is_orthogonal(v2)

        v3 = Vector([1.0, 1.0, 0.0])
        assert not v1.is_orthogonal(v3)

    def test_vector_negation(self):
        """Test vector negation."""
        v = Vector([1.0, 2.0])
        result = -v
        assert isinstance(result, Vector)
        assert result[0].value == -1.0
        assert result[1].value == -2.0

    def test_vector_to_string(self):
        """Test string conversion."""
        v = Vector([1.0, 2.0, 3.0])
        assert v.to_string() == "<1, 2, 3>"

    def test_vector_to_numpy(self):
        """Test NumPy conversion."""
        v = Vector([1.0, 2.0, 3.0])
        arr = v.to_numpy()
        assert isinstance(arr, np.ndarray)
        assert arr.tolist() == [1.0, 2.0, 3.0]


class TestMatrix:
    """Tests for Matrix type."""

    def test_create_matrix(self):
        """Test creating a matrix."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        assert m.shape == (2, 2)
        assert m[0, 0].value == 1.0
        assert m[1, 1].value == 4.0

    def test_matrix_addition(self):
        """Test matrix addition."""
        m1 = Matrix([[1.0, 2.0], [3.0, 4.0]])
        m2 = Matrix([[5.0, 6.0], [7.0, 8.0]])
        result = m1 + m2
        assert isinstance(result, Matrix)
        assert result[0, 0].value == 6.0
        assert result[1, 1].value == 12.0

    def test_matrix_subtraction(self):
        """Test matrix subtraction."""
        m1 = Matrix([[5.0, 6.0], [7.0, 8.0]])
        m2 = Matrix([[1.0, 2.0], [3.0, 4.0]])
        result = m1 - m2
        assert isinstance(result, Matrix)
        assert result[0, 0].value == 4.0
        assert result[1, 1].value == 4.0

    def test_scalar_multiplication(self):
        """Test scalar multiplication."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        result = m * 2
        assert isinstance(result, Matrix)
        assert result[0, 0].value == 2.0
        assert result[1, 1].value == 8.0

        # Right multiplication
        result2 = 3 * m
        assert result2[0, 0].value == 3.0

    def test_matrix_multiplication(self):
        """Test matrix multiplication."""
        m1 = Matrix([[1.0, 2.0], [3.0, 4.0]])
        m2 = Matrix([[5.0, 6.0], [7.0, 8.0]])
        result = m1 * m2
        assert isinstance(result, Matrix)
        # [[1*5+2*7, 1*6+2*8], [3*5+4*7, 3*6+4*8]]
        # = [[19, 22], [43, 50]]
        assert result[0, 0].value == 19.0
        assert result[0, 1].value == 22.0
        assert result[1, 0].value == 43.0
        assert result[1, 1].value == 50.0

    def test_matrix_vector_multiplication(self):
        """Test matrix * vector = vector."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        v = Vector([5.0, 6.0])
        result = m * v
        assert isinstance(result, Vector)
        # [1*5+2*6, 3*5+4*6] = [17, 39]
        assert result[0].value == 17.0
        assert result[1].value == 39.0

    def test_matrix_transpose(self):
        """Test matrix transpose."""
        m = Matrix([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        result = m.transpose()
        assert result.shape == (3, 2)
        assert result[0, 0].value == 1.0
        assert result[0, 1].value == 4.0
        assert result[2, 1].value == 6.0

    def test_matrix_determinant(self):
        """Test matrix determinant."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        det = m.determinant()
        assert isinstance(det, Real)
        assert abs(det.value - (-2.0)) < 1e-10  # 1*4 - 2*3 = -2

    def test_matrix_inverse(self):
        """Test matrix inverse."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        inv = m.inverse()
        assert isinstance(inv, Matrix)

        # m * inv should be identity
        identity = m * inv
        assert abs(identity[0, 0].value - 1.0) < 1e-10
        assert abs(identity[0, 1].value) < 1e-10
        assert abs(identity[1, 0].value) < 1e-10
        assert abs(identity[1, 1].value - 1.0) < 1e-10

    def test_matrix_trace(self):
        """Test matrix trace."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        trace = m.trace()
        assert isinstance(trace, Real)
        assert trace.value == 5.0  # 1 + 4

    def test_matrix_power(self):
        """Test matrix exponentiation."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])

        # m^0 = identity
        m0 = m**0
        assert m0[0, 0].value == 1.0
        assert m0[0, 1].value == 0.0
        assert m0[1, 1].value == 1.0

        # m^1 = m
        m1 = m**1
        assert m1[0, 0].value == 1.0

        # m^2 = m * m
        m2 = m**2
        expected = m * m
        assert abs(m2[0, 0].value - expected[0, 0].value) < 1e-10

    def test_matrix_negation(self):
        """Test matrix negation."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        result = -m
        assert isinstance(result, Matrix)
        assert result[0, 0].value == -1.0
        assert result[1, 1].value == -4.0

    def test_matrix_to_string(self):
        """Test string conversion."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        s = m.to_string()
        assert "[1, 2]" in s
        assert "[3, 4]" in s

    def test_matrix_to_numpy(self):
        """Test NumPy conversion."""
        m = Matrix([[1.0, 2.0], [3.0, 4.0]])
        arr = m.to_numpy()
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (2, 2)
        assert arr[0, 0] == 1.0
        assert arr[1, 1] == 4.0


class TestGeometricIntegration:
    """Tests for interactions between geometric types."""

    def test_vector_from_points(self):
        """Test creating vector from two points."""
        p1 = Point([1.0, 2.0])
        p2 = Point([4.0, 6.0])
        v = p2 - p1  # Should be Vector([3, 4])
        assert isinstance(v, Vector)
        assert v[0].value == 3.0
        assert v[1].value == 4.0

    def test_matrix_times_vector_equals_linear_combination(self):
        """Test that matrix-vector multiplication works as expected."""
        # Simple 2x2 rotation matrix (90 degrees)
        cos90, sin90 = 0.0, 1.0
        m = Matrix([[cos90, -sin90], [sin90, cos90]])
        v = Vector([1.0, 0.0])

        result = m * v
        assert isinstance(result, Vector)
        # [0, 1] rotated 90° = [-0, 1] ≈ [0, 1]
        assert abs(result[0].value) < 1e-10
        assert abs(result[1].value - 1.0) < 1e-10

    def test_identity_matrix_multiplication(self):
        """Test identity matrix times vector = vector."""
        identity = Matrix([[1.0, 0.0], [0.0, 1.0]])
        v = Vector([3.0, 4.0])
        result = identity * v
        assert result[0].value == 3.0
        assert result[1].value == 4.0
