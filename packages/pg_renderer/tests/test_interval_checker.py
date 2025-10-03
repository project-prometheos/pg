"""Tests for interval checker based on SymPy sets."""

from pg_renderer.checkers.interval import IntervalChecker


def test_basic_interval_closed_open():
    chk = IntervalChecker()
    ok, _ = chk.check('[1, 3)', '[1, 3)')
    assert ok
    ok, _ = chk.check('(-inf, 2]', '(-infty, 2]')
    assert ok


def test_union_intervals():
    chk = IntervalChecker()
    ok, _ = chk.check('(-inf, -1] U [1, inf)', '(-oo, -1] ∪ [1, oo)')
    assert ok
