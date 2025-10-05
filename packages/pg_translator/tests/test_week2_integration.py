"""
End-to-end integration tests for Week 2.

Tests the complete pipeline with macro support.
"""

import pytest
from pathlib import Path

from pg_translator.translator import PGTranslator
from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.executor import PGExecutor


def test_simple_numeric_problem_renders():
    """Test that a simple numeric problem renders correctly."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("What is 2 + 2?")
TEXT(BR())
TEXT("Answer: ", ans_rule(20))

ANS(num_cmp(4))

ENDDOCUMENT()
"""

    # Create translator with macro-enabled sandbox
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate problem
    result = translator.translate_source(pg_code, seed=1234)

    # Verify rendering
    assert result.errors is None or len(
        result.errors) == 0, f"Errors: {result.errors}"
    assert "What is 2 + 2?" in result.statement_html
    assert 'name="AnSwEr' in result.statement_html or 'input' in result.statement_html.lower()
    assert len(result.answer_blanks) >= 1


def test_simple_numeric_grading_correct():
    """Test that correct numeric answer grades as correct."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("What is 2 + 2?")
TEXT(ans_rule(20))

ANS(num_cmp(4))

ENDDOCUMENT()
"""

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate with correct answer
    result = translator.translate_source(
        pg_code,
        seed=1234,
        inputs={"AnSwEr0001": "4"}
    )

    # Verify grading
    assert result.answer_results is not None
    assert len(result.answer_results) > 0

    # Check first answer
    first_answer_name = list(result.answer_results.keys())[0]
    first_result = result.answer_results[first_answer_name]

    assert first_result.is_correct, "Answer should be marked correct"
    assert first_result.score == 1.0, "Score should be 1.0"


def test_simple_numeric_grading_incorrect():
    """Test that incorrect numeric answer grades as incorrect."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("What is 2 + 2?")
TEXT(ans_rule(20))

ANS(num_cmp(4))

ENDDOCUMENT()
"""

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate with incorrect answer
    result = translator.translate_source(
        pg_code,
        seed=1234,
        inputs={"AnSwEr0001": "5"}
    )

    # Verify grading
    assert result.answer_results is not None
    assert len(result.answer_results) > 0

    # Check first answer
    first_answer_name = list(result.answer_results.keys())[0]
    first_result = result.answer_results[first_answer_name]

    assert not first_result.correct, "Answer should be marked incorrect"
    assert first_result.score == 0.0, "Score should be 0.0"


def test_random_problem():
    """Test problem with random() function."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

$a = random(1, 10, 1)
$b = random(1, 10, 1)
$ans = $a + $b

TEXT("What is ", $a, " + ", $b, "?")
TEXT(ans_rule(20))

ANS(num_cmp($ans))

ENDDOCUMENT()
"""

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Test with different seeds
    results = []
    for seed in [1, 2, 3, 4, 5]:
        result = translator.translate_source(pg_code, seed=seed)
        assert result.errors is None or len(result.errors) == 0
        print(f"Seed {seed}: {result.statement_html}")
        results.append(result.statement_html)

    # Should have at least 2 different problems
    unique_problems = len(set(results))
    print(f"Unique problems: {unique_problems}")
    assert unique_problems >= 2, f"Expected at least 2 unique problems, got {unique_problems}"


def test_multiple_answer_blanks():
    """Test problem with multiple answer blanks."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("Answer 1: ", ans_rule(10))
TEXT(BR())
TEXT("Answer 2: ", ans_rule(10))

ANS(num_cmp(10))
ANS(num_cmp(20))

ENDDOCUMENT()
"""

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate
    result = translator.translate_source(pg_code, seed=1234)

    # Verify two answer blanks
    assert len(result.answer_blanks) >= 2, "Should have at least 2 answer blanks"

    # Test grading both answers
    result = translator.translate_source(
        pg_code,
        seed=1234,
        inputs={"AnSwEr0001": "10", "AnSwEr0002": "20"}
    )

    assert result.score == 1.0, "Both answers correct should give score 1.0"


def test_problem_from_file():
    """Test loading problem from .pg file."""
    # Find test problem file
    test_dir = Path(__file__).parent
    problem_file = test_dir / "problems" / "simple_numeric.pg"

    if not problem_file.exists():
        pytest.skip(f"Test problem not found: {problem_file}")

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate
    result = translator.translate(problem_file, seed=1234)

    # Verify
    assert result.errors is None or len(result.errors) == 0
    assert "What is 2 + 2?" in result.statement_html


def test_named_answer_blanks():
    """Test problem with named answer blanks."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("First: ", NAMED_ANS_RULE("first", 10))
TEXT(BR())
TEXT("Second: ", NAMED_ANS_RULE("second", 10))

NAMED_ANS("first", num_cmp(100))
NAMED_ANS("second", num_cmp(200))

ENDDOCUMENT()
"""

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate
    result = translator.translate_source(pg_code, seed=1234)

    # Verify named answer blanks
    assert 'name="first"' in result.statement_html or len(
        result.answer_blanks) >= 2
    assert 'name="second"' in result.statement_html or len(
        result.answer_blanks) >= 2

    # Test grading
    result = translator.translate_source(
        pg_code,
        seed=1234,
        inputs={"first": "100", "second": "200"}
    )

    assert result.score == 1.0, "Named answers should grade correctly"


def test_solution_and_hint():
    """Test problem with solution and hint."""
    pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("What is 2 + 2?")
TEXT(ans_rule(20))

ANS(num_cmp(4))

SOLUTION("The answer is 4 because 2 + 2 = 4.")
HINT("Think about basic addition.")

ENDDOCUMENT()
"""

    # Create translator
    sandbox = InProcessSandbox(timeout=10)
    sandbox.load_macros("PG.pl", "PGbasicmacros.pl")

    executor = PGExecutor()
    executor.sandbox = sandbox

    translator = PGTranslator(executor=executor)

    # Translate
    result = translator.translate_source(pg_code, seed=1234)

    # Verify solution and hint
    assert result.solution_html is not None, "Solution should be present"
    assert "answer is 4" in result.solution_html.lower()

    assert result.hint_html is not None, "Hint should be present"
    assert "addition" in result.hint_html.lower()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
