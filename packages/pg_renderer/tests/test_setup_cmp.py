"""Integration-style test for setup-side ->cmp(...) parity.

This ensures `$ans = Formula('...')->cmp(upToConstant => 1)` in setup
produces an answer spec with checker 'up_to_additive_constant'.
"""

from pg_renderer import PGRenderer


def test_setup_side_cmp_up_to_constant():
    pg = r'''
DOCUMENT();

loadMacros('PGstandard.pl','PGML.pl');

$specific = Formula('e^x');
$cmp = $specific->cmp(upToConstant => 1);

BEGIN_PGML
[_]{$cmp}
END_PGML

ENDDOCUMENT();
'''

    renderer = PGRenderer()
    result = renderer.render(pg)

    assert result['answers'], 'Should produce at least one answer blank'
    ans_meta = list(result['answers'].values())[0]
    assert ans_meta['type'] == 'formula'
    assert ans_meta.get('checker') == 'up_to_additive_constant'
