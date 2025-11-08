"""Tests for newly ported macros."""

from pg_macros import load_macros


def test_pgstandard_exports_document_and_ans():
    exports = load_macros('PGstandard.pl')
    assert 'DOCUMENT' in exports
    assert 'ANS' in exports


def test_answer_format_help_topics():
    exports = load_macros('AnswerFormatHelp.pl')
    helper = exports['AnswerFormatHelp']
    html = helper('formulas')
    assert 'Formulas' in html or 'formulas' in html.lower()
    link = exports['helpLink']('numbers')
    assert 'data-topic' in link


def test_context_fraction_flags():
    exports = load_macros('contextFraction.pl')
    ctx = exports['contextLimitedProperFraction']()
    assert ctx.flags['strictFractions'] is True
    assert ctx.flags['allowMixedNumbers'] is True


def test_multi_answer_combines_scores():
    exports = load_macros('parserMultiAnswer.pl')
    multi = exports['MultiAnswer']

    from pg_answer.evaluators.string import StringEvaluator

    ma = multi(StringEvaluator('a'), StringEvaluator('b'))
    evaluator = ma.cmp()
    result = evaluator.evaluate('a,b')
    assert result.score == 1.0
    assert result.correct is True


def test_graph_metadata_structure():
    exports = load_macros('PGgraphmacros.pl')
    init_graph = exports['init_graph']
    add_functions = exports['add_functions']
    graph_to_html = exports['graph_to_html']

    graph = init_graph(-1, -1, 1, 1, size=(100, 100))
    add_functions(graph, ('x', 'red', 'solid', 2))
    html = graph_to_html(graph)
    assert 'pg-graph' in html
