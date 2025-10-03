"""Basic MultiAnswer parsing: setup and PGML ans_rule mapping to blanks."""

from pg_renderer import PGRenderer


def test_multianswer_two_blanks_mapping():
    pg = r'''
DOCUMENT();
loadMacros('PGstandard.pl','PGML.pl');

$a = Compute('1');
$b = Compute('2');
$ma = MultiAnswer($a, $b);

BEGIN_PGML
First: [_]{ $ma->ans_rule(10) }
Second: [_]{ $ma->ans_rule(10) }
END_PGML

ENDDOCUMENT();
'''

    r = PGRenderer().render(pg)
    ans = r['answers']
    assert len(ans) == 2
    metas = list(ans.values())
    # Order preserves the sequence of ans_rule calls
    assert metas[0]['correct_value'] == '1'
    assert metas[1]['correct_value'] == '2'
    assert metas[0].get('group') == metas[1].get('group')
