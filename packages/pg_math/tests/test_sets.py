"""Unit tests for set MathValue types."""

import pytest

from pg_math import Infinity, Interval, Real, Set, Union


class TestInterval:
    """Tests for Interval type."""

    def test_create_closed_interval(self):
        """Test creating a closed interval [a, b]."""
        interval = Interval(0, 1, open_left=False, open_right=False)
        assert interval.left.value == 0
        assert interval.right.value == 1
        assert not interval.open_left
        assert not interval.open_right

    def test_create_open_interval(self):
        """Test creating an open interval (a, b)."""
        interval = Interval(0, 1, open_left=True, open_right=True)
        assert interval.open_left
        assert interval.open_right

    def test_create_half_open_interval(self):
        """Test creating half-open intervals."""
        interval1 = Interval(0, 1, open_left=True, open_right=False)
        assert interval1.open_left and not interval1.open_right

        interval2 = Interval(0, 1, open_left=False, open_right=True)
        assert not interval2.open_left and interval2.open_right

    def test_interval_with_infinity(self):
        """Test interval with infinite endpoints."""
        interval = Interval(Infinity(-1), Infinity(1))
        assert isinstance(interval.left, Infinity)
        assert isinstance(interval.right, Infinity)

    def test_interval_contains_closed(self):
        """Test membership in closed interval."""
        interval = Interval(0, 1, open_left=False, open_right=False)
        assert interval.contains(0)  # Left endpoint included
        assert interval.contains(0.5)
        assert interval.contains(1)  # Right endpoint included
        assert not interval.contains(-0.1)
        assert not interval.contains(1.1)

    def test_interval_contains_open(self):
        """Test membership in open interval."""
        interval = Interval(0, 1, open_left=True, open_right=True)
        assert not interval.contains(0)  # Left endpoint excluded
        assert interval.contains(0.5)
        assert not interval.contains(1)  # Right endpoint excluded

    def test_interval_is_empty(self):
        """Test empty interval detection."""
        # a > b
        interval1 = Interval(2, 1)
        assert interval1.is_empty()

        # (a, a)
        interval2 = Interval(1, 1, open_left=True, open_right=False)
        assert interval2.is_empty()

        # [a, a] is not empty (single point)
        interval3 = Interval(1, 1, open_left=False, open_right=False)
        assert not interval3.is_empty()

    def test_interval_length(self):
        """Test interval length calculation."""
        interval = Interval(0, 5)
        length = interval.length()
        assert isinstance(length, Real)
        assert length.value == 5.0

        # Infinite interval
        inf_interval = Interval(0, Infinity(1))
        assert isinstance(inf_interval.length(), Infinity)

    def test_interval_intersection(self):
        """Test interval intersection."""
        # Overlapping intervals
        i1 = Interval(0, 3)
        i2 = Interval(2, 5)
        result = i1.intersect(i2)
        assert result is not None
        assert result.left.value == 2
        assert result.right.value == 3

        # Disjoint intervals
        i3 = Interval(0, 1)
        i4 = Interval(2, 3)
        result2 = i3.intersect(i4)
        assert result2 is None

    def test_interval_union_overlapping(self):
        """Test union of overlapping intervals."""
        i1 = Interval(0, 3)
        i2 = Interval(2, 5)
        union = i1.union(i2)
        assert isinstance(union, Union)
        # Should be merged into single interval [0, 5]
        assert len(union.sets) == 1
        assert union.sets[0].left.value == 0
        assert union.sets[0].right.value == 5

    def test_interval_union_disjoint(self):
        """Test union of disjoint intervals."""
        i1 = Interval(0, 1)
        i2 = Interval(2, 3)
        union = i1.union(i2)
        assert isinstance(union, Union)
        # Should be two separate intervals
        assert len(union.sets) == 2

    def test_interval_comparison(self):
        """Test interval comparison."""
        i1 = Interval(0, 1, open_left=True, open_right=False)
        i2 = Interval(0, 1, open_left=True, open_right=False)
        assert i1.compare(i2)

        i3 = Interval(0, 1, open_left=False, open_right=False)
        assert not i1.compare(i3)  # Different openness

    def test_interval_to_string(self):
        """Test string conversion."""
        assert Interval(0, 1).to_string() == "[0, 1]"
        assert Interval(0, 1, open_left=True, open_right=True).to_string() == "(0, 1)"
        assert Interval(0, 1, open_left=True, open_right=False).to_string() == "(0, 1]"
        assert Interval(0, 1, open_left=False, open_right=True).to_string() == "[0, 1)"

    def test_interval_to_python(self):
        """Test Python conversion."""
        interval = Interval(0, 1, open_left=True, open_right=False)
        result = interval.to_python()
        assert result == (0.0, 1.0, True, False)


class TestSet:
    """Tests for Set type."""

    def test_create_set(self):
        """Test creating a finite set."""
        s = Set([1, 2, 3])
        assert s.cardinality() == 3

    def test_set_removes_duplicates(self):
        """Test that sets automatically remove duplicates."""
        s = Set([1, 2, 2, 3, 3, 3])
        assert s.cardinality() == 3

    def test_empty_set(self):
        """Test empty set."""
        s = Set([])
        assert s.is_empty()
        assert s.cardinality() == 0

    def test_set_contains(self):
        """Test membership checking."""
        s = Set([1, 2, 3])
        assert s.contains(1)
        assert s.contains(2)
        assert not s.contains(4)

    def test_set_intersection(self):
        """Test set intersection."""
        s1 = Set([1, 2, 3])
        s2 = Set([2, 3, 4])
        result = s1.intersect(s2)
        assert isinstance(result, Set)
        assert result.cardinality() == 2
        assert result.contains(2)
        assert result.contains(3)
        assert not result.contains(1)
        assert not result.contains(4)

    def test_set_union(self):
        """Test set union."""
        s1 = Set([1, 2, 3])
        s2 = Set([3, 4, 5])
        result = s1.union(s2)
        assert isinstance(result, Set)
        assert result.cardinality() == 5
        assert result.contains(1)
        assert result.contains(5)

    def test_set_difference(self):
        """Test set difference."""
        s1 = Set([1, 2, 3, 4])
        s2 = Set([3, 4, 5])
        result = s1.difference(s2)
        assert isinstance(result, Set)
        assert result.cardinality() == 2
        assert result.contains(1)
        assert result.contains(2)
        assert not result.contains(3)

    def test_set_subset(self):
        """Test subset checking."""
        s1 = Set([1, 2])
        s2 = Set([1, 2, 3, 4])
        assert s1.is_subset(s2)
        assert not s2.is_subset(s1)

    def test_set_superset(self):
        """Test superset checking."""
        s1 = Set([1, 2, 3, 4])
        s2 = Set([2, 3])
        assert s1.is_superset(s2)
        assert not s2.is_superset(s1)

    def test_set_comparison(self):
        """Test set comparison (order independent)."""
        s1 = Set([1, 2, 3])
        s2 = Set([3, 2, 1])  # Different order
        assert s1.compare(s2)

        s3 = Set([1, 2, 4])
        assert not s1.compare(s3)

    def test_set_to_string(self):
        """Test string conversion."""
        s = Set([1, 2, 3])
        string = s.to_string()
        assert string.startswith("{")
        assert string.endswith("}")
        assert "1" in string
        assert "2" in string
        assert "3" in string

        # Empty set
        empty = Set([])
        assert empty.to_string() == "{}"

    def test_set_to_python(self):
        """Test Python conversion."""
        s = Set([1.0, 2.0, 3.0])
        result = s.to_python()
        assert isinstance(result, list)
        assert len(result) == 3


class TestUnion:
    """Tests for Union type."""

    def test_create_union_of_intervals(self):
        """Test creating a union of intervals."""
        i1 = Interval(0, 1)
        i2 = Interval(2, 3)
        union = Union([i1, i2])
        assert len(union.sets) == 2

    def test_create_union_of_sets(self):
        """Test creating a union of finite sets."""
        s1 = Set([1, 2])
        s2 = Set([3, 4])
        union = Union([s1, s2])
        assert len(union.sets) == 2

    def test_union_simplifies_overlapping_intervals(self):
        """Test that union automatically merges overlapping intervals."""
        i1 = Interval(0, 3)
        i2 = Interval(2, 5)
        union = Union([i1, i2])
        # Should be merged into one interval
        assert len(union.sets) == 1
        assert union.sets[0].left.value == 0
        assert union.sets[0].right.value == 5

    def test_union_contains(self):
        """Test membership in union."""
        i1 = Interval(0, 1)
        i2 = Interval(2, 3)
        union = Union([i1, i2])

        assert union.contains(0.5)  # In first interval
        assert union.contains(2.5)  # In second interval
        assert not union.contains(1.5)  # In neither

    def test_union_comparison(self):
        """Test union comparison."""
        i1 = Interval(0, 1)
        i2 = Interval(2, 3)
        u1 = Union([i1, i2])
        u2 = Union([i1, i2])
        assert u1.compare(u2)

    def test_union_to_string(self):
        """Test string conversion."""
        i1 = Interval(0, 1)
        i2 = Interval(2, 3)
        union = Union([i1, i2])
        string = union.to_string()
        assert "U" in string or "∪" in string  # Union symbol

    def test_union_mixed_types(self):
        """Test union with both intervals and sets."""
        interval = Interval(0, 1)
        s = Set([2, 3, 4])
        union = Union([interval, s])
        assert len(union.sets) == 2
        assert union.contains(0.5)  # In interval
        assert union.contains(3)  # In set
        assert not union.contains(1.5)  # In neither


class TestSetIntegration:
    """Tests for interactions between set types."""

    def test_interval_to_union_to_contains(self):
        """Test complete workflow with intervals and unions."""
        # Create union of two disjoint intervals
        i1 = Interval(0, 1, open_right=True)  # [0, 1)
        i2 = Interval(2, 3, open_left=True)  # (2, 3]
        union = Union([i1, i2])

        # Test membership
        assert union.contains(0)  # In first interval
        assert union.contains(0.5)
        assert not union.contains(1)  # Excluded by open right
        assert not union.contains(1.5)  # Between intervals
        assert not union.contains(2)  # Excluded by open left
        assert union.contains(2.5)
        assert union.contains(3)  # In second interval

    def test_real_numbers_interval(self):
        """Test interval representing all real numbers."""
        all_reals = Interval(Infinity(-1), Infinity(1), open_left=True, open_right=True)
        assert all_reals.contains(0)
        assert all_reals.contains(1000)
        assert all_reals.contains(-1000)

    def test_multiple_interval_merge(self):
        """Test that multiple overlapping intervals merge correctly."""
        i1 = Interval(0, 2)
        i2 = Interval(1, 3)
        i3 = Interval(2, 4)
        union = Union([i1, i2, i3])

        # Should merge into single interval [0, 4]
        assert len(union.sets) == 1
        assert union.sets[0].left.value == 0
        assert union.sets[0].right.value == 4
