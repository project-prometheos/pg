"""Tests for inequality checker using sampling equivalence."""

from pg_renderer.checkers.inequality import InequalityChecker


def test_simple_inequality_equivalence():
    chk = InequalityChecker()
    ok, _ = chk.check('x >= 4', 'x - 4 >= 0', context={'variables': ['x']})
    assert ok


def test_inequality_non_equivalence():
    chk = InequalityChecker()
    ok, _ = chk.check('x > 0', 'x >= 0', context={'variables': ['x']})
    assert not ok
