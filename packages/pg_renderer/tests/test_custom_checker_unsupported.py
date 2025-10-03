"""Ensure custom checkers via ->cmp(checker => sub {...}) are detected and rejected (unsupported)."""

from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker


def test_custom_checker_rejected():
    pg = r'''
DOCUMENT();
loadMacros('PGstandard.pl','PGML.pl');

$ans = Compute('x');

BEGIN_PGML
[_]{$ans->cmp(checker => sub { return 1; })}
END_PGML

ENDDOCUMENT();
'''

    renderer = PGRenderer()
    r = renderer.render(pg)
    answers = r['answers']
    assert answers
    meta = list(answers.values())[0]
    assert meta['checker'] == 'custom'
    ctx = {k: meta.get(k) for k in ['checker', 'variables']}
    ctx['options'] = meta.get('options', {})
    chk = AnswerChecker()
    ok, msg = chk.check('anything', meta['correct_value'], 'formula', ctx)
    assert not ok and 'Custom checker' in msg

