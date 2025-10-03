"""Tests for fraction-related cmp flags parity."""

from pg_renderer.answer_checker import AnswerChecker


def test_students_must_reduce_fractions():
    checker = AnswerChecker(tolerance=1e-6)
    context = {
        'checker': 'standard',
        'options': {
            'studentsMustReduceFractions': True,
            'reduceFractions': True,
            'allowMixedNumbers': True,
        },
    }

    # Unreduced fraction should be rejected
    ok, msg = checker.check('6/4', '3/2', answer_type='formula', context=context)
    assert not ok and 'reduce' in msg.lower()

    # Reduced fraction should be accepted
    ok, msg = checker.check('3/2', '3/2', answer_type='formula', context=context)
    assert ok


def test_disallow_mixed_numbers():
    checker = AnswerChecker(tolerance=1e-6)
    context = {
        'checker': 'standard',
        'options': {
            'allowMixedNumbers': False,
        },
    }

    ok, msg = checker.check('1 1/2', '3/2', answer_type='formula', context=context)
    assert not ok and 'mixed numbers' in msg.lower()

