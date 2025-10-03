"""Integration tests for MultiAnswer group evaluation."""

from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker


PG_MULTI = r'''
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

PG_MULTI_NO_PARTIAL = r'''
DOCUMENT();
loadMacros('PGstandard.pl','PGML.pl');

$a = Compute('1');
$b = Compute('2');
$ma = MultiAnswer($a, $b)->with(partialCredit => 0);

BEGIN_PGML
First: [_]{ $ma->ans_rule(10) }
Second: [_]{ $ma->ans_rule(10) }
END_PGML

ENDDOCUMENT();
'''


def _build_group_items(rendered, student_inputs):
    answers = rendered['answers']
    group_id = None
    entries = []
    for ans_id, meta in answers.items():
        if meta.get('type') == 'multi':
            group_id = meta.get('group')
            entries.append((meta.get('group_index', 0), ans_id, meta))
    assert group_id is not None, 'Expected a MultiAnswer group'
    entries.sort(key=lambda item: item[0])
    items = [
        {
            'answer_id': ans_id,
            'meta': meta,
            'student_answer': student_inputs.get(ans_id, ''),
        }
        for _, ans_id, meta in entries
    ]
    return group_id, items


def test_multianswer_group_all_correct():
    renderer = PGRenderer()
    rendered = renderer.render(PG_MULTI)
    checker = AnswerChecker()

    student_inputs = {}
    for ans_id, meta in rendered['answers'].items():
        if meta.get('type') == 'multi':
            student_inputs[ans_id] = meta.get('correct_value', '')

    group_id, items = _build_group_items(rendered, student_inputs)
    result = checker.check_multi_group(group_id, items)

    assert result['group_correct'] is True
    assert all(item['correct'] for item in result['items'])


def test_multianswer_partial_credit_default():
    renderer = PGRenderer()
    rendered = renderer.render(PG_MULTI)
    checker = AnswerChecker()

    student_inputs = {}
    group_entries = sorted(
        [
            (meta.get('group_index', 0), ans_id, meta)
            for ans_id, meta in rendered['answers'].items()
            if meta.get('type') == 'multi'
        ],
        key=lambda item: item[0],
    )
    first_id = group_entries[0][1]
    second_id = group_entries[1][1]
    first_meta = group_entries[0][2]

    student_inputs[first_id] = first_meta.get('correct_value', '')
    student_inputs[second_id] = '999'

    group_id, items = _build_group_items(rendered, student_inputs)
    result = checker.check_multi_group(group_id, items)

    assert result['group_correct'] is False
    outcomes = {item['answer_id']: item for item in result['items']}
    assert outcomes[first_id]['correct'] is True
    assert outcomes[second_id]['correct'] is False
    assert result['partial_credit'] is True


def test_multianswer_no_partial_credit_enforces_all_or_nothing():
    renderer = PGRenderer()
    rendered = renderer.render(PG_MULTI_NO_PARTIAL)
    checker = AnswerChecker()

    group_entries = sorted(
        [
            (meta.get('group_index', 0), ans_id, meta)
            for ans_id, meta in rendered['answers'].items()
            if meta.get('type') == 'multi'
        ],
        key=lambda item: item[0],
    )
    first_id = group_entries[0][1]
    second_id = group_entries[1][1]
    first_meta = group_entries[0][2]

    student_inputs = {
        first_id: first_meta.get('correct_value', ''),
        second_id: '999',
    }

    group_id, items = _build_group_items(rendered, student_inputs)
    result = checker.check_multi_group(group_id, items)

    assert result['partial_credit'] is False
    assert result['group_correct'] is False

    outcomes = {item['answer_id']: item for item in result['items']}
    assert outcomes[first_id]['raw_correct'] is True
    assert outcomes[first_id]['correct'] is False
    assert outcomes[first_id]['message'] == 'MultiAnswer group requires all blanks to be correct.'
    assert outcomes[second_id]['correct'] is False
