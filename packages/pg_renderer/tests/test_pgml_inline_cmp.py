"""Ensure PGML parses inline Compute(...)->cmp(...) correctly."""

from pg_renderer import PGRenderer


def test_pgml_inline_compute_cmp():
    pg = r'''
DOCUMENT();

loadMacros('PGstandard.pl','PGML.pl');

BEGIN_PGML
[_]{ Compute('3/2')->cmp(studentsMustReduceFractions => 1) }
END_PGML

ENDDOCUMENT();
'''

    renderer = PGRenderer()
    result = renderer.render(pg)
    assert result['answers'], 'Should produce at least one answer blank'
    ans_meta = list(result['answers'].values())[0]
    assert ans_meta['type'] == 'formula'
    assert ans_meta['correct_value'] == '3/2'
    assert ans_meta.get('options', {}).get('studentsMustReduceFractions') is True
