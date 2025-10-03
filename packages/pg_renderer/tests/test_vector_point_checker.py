"""Tests for vector and point checkers."""

from pg_renderer.checkers.vector import VectorChecker, PointChecker


def test_vector_checker():
    chk = VectorChecker(tolerance=1e-6)
    ok, _ = chk.check('<1, 2, 3>', '<1, 2, 3>')
    assert ok
    ok, _ = chk.check('<1, 2, 3>', '<1, 2, 4>')
    assert not ok


def test_point_checker():
    chk = PointChecker(tolerance=1e-6)
    ok, _ = chk.check('(3, pi)', '(3, 3.1415926535)')
    assert ok
    ok, _ = chk.check('(0, 0)', '(0, 1)')
    assert not ok
