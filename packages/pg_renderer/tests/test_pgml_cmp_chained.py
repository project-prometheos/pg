"""Ensure PGML parses $var->cmp(...)->withPostFilter(...) correctly."""

from pg_renderer import PGRenderer


def test_pgml_cmp_with_postfilter_chain():
    pg = r'''
DOCUMENT();

loadMacros('PGstandard.pl','PGML.pl');

$answer = Compute('3/2');

BEGIN_PGML
[_]{$answer->cmp(studentsMustReduceFractions => 1)->withPostFilter(AnswerHints())}
END_PGML

ENDDOCUMENT();
'''

    renderer = PGRenderer()
    result = renderer.render(pg)
    assert result['answers'], 'Should produce at least one answer blank'
    ans_meta = list(result['answers'].values())[0]
    assert ans_meta['type'] == 'formula'
    # Options should be present and include the flag
    assert ans_meta.get('options', {}).get('studentsMustReduceFractions') is True
