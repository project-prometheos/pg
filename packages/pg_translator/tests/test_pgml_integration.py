"""
Tests for PGML integration with PGTranslator.

Tests BEGIN_PGML...END_PGML blocks with full rendering and grading.
"""

import pytest

from pg_translator import PGTranslator
from pg_translator.executor import PGExecutor
from pg_translator.in_process_sandbox import InProcessSandbox


class TestPGMLIntegration:
    """Test PGML integration with translator."""

    def test_simple_pgml_problem(self):
        """Test simple PGML problem rendering."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

$a = 5
$b = 3
$ans = $a + $b

BEGIN_PGML
Add the numbers: [$a] + [$b] = [_]{$ans}
END_PGML

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        result = translator.translate_source(pg_code, seed=1234)

        # Check rendering
        assert result.errors is None or len(result.errors) == 0
        assert result.statement_html is not None
        assert "5" in result.statement_html  # Variable $a
        assert "3" in result.statement_html  # Variable $b
        assert "___ANSWER_BLANK_" in result.statement_html  # Answer blank placeholder
        assert "AnSwEr0001" in result.statement_html

    def test_pgml_with_math(self):
        """Test PGML with inline math."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

$ans = 42

BEGIN_PGML
Calculate [`x^2`] when [`x = [$ans]`].

Answer: [_]{$ans}
END_PGML

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        result = translator.translate_source(pg_code, seed=1234)

        assert result.errors is None or len(result.errors) == 0
        # Math content should be present
        assert "x^2" in result.statement_html
        assert "___ANSWER_BLANK_" in result.statement_html

    def test_pgml_with_formatting(self):
        """Test PGML with bold and lists."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

$ans = 10

BEGIN_PGML
**Problem 1.** Choose the correct value:

+ Option A: [_]{$ans}
+ Option B: [_]{$ans}

The answer is [$ans].
END_PGML

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        result = translator.translate_source(pg_code, seed=1234)

        assert result.errors is None or len(result.errors) == 0
        assert "Problem 1." in result.statement_html  # Check content not HTML tags
        assert "Option A" in result.statement_html
        assert "Option B" in result.statement_html
        assert "10" in result.statement_html  # Variable interpolation

    @pytest.mark.skip(reason="Answer grading requires evaluator execution - not yet implemented")
    def test_pgml_grading(self):
        """Test PGML problem with grading."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

answer = 42

BEGIN_PGML
What is the meaning of life? [_]{num_cmp(answer)}
END_PGML

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        # Render
        result = translator.translate_source(pg_code, seed=1234)
        assert result.errors is None or len(result.errors) == 0
        assert len(result.answer_blanks) == 1

        # Grade correct answer
        graded = translator.translate_source(
            pg_code, seed=1234, inputs={"AnSwEr0001": "42"}
        )
        assert graded.answer_results is not None
        first_result = list(graded.answer_results.values())[0]
        assert first_result.correct
        assert graded.score == 1.0

        # Grade incorrect answer
        graded = translator.translate_source(
            pg_code, seed=1234, inputs={"AnSwEr0001": "0"}
        )
        assert graded.answer_results is not None
        first_result = list(graded.answer_results.values())[0]
        assert not first_result.correct
        assert graded.score == 0.0

    def test_pgml_solution(self):
        """Test PGML with solution."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

$ans = 7

BEGIN_PGML
What is 3 + 4? [_]{$ans}
END_PGML

BEGIN_PGML_SOLUTION
The answer is [$ans] because 3 + 4 = 7.
END_PGML_SOLUTION

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        result = translator.translate_source(pg_code, seed=1234)

        assert result.errors is None or len(result.errors) == 0
        assert result.solution_html is not None
        assert "7" in result.solution_html
        assert "3 + 4 = 7" in result.solution_html

    def test_pgml_hint(self):
        """Test PGML with hint."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

$ans = 12

BEGIN_PGML
What is 6 × 2? [_]{$ans}
END_PGML

BEGIN_PGML_HINT
Try multiplying 6 by 2.
END_PGML_HINT

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        result = translator.translate_source(pg_code, seed=1234)

        assert result.errors is None or len(result.errors) == 0
        assert result.hint_html is not None
        assert "multiplying" in result.hint_html
        assert "6 by 2" in result.hint_html

    def test_real_problem_from_file(self):
        """Test real PGML problem from ps1-prob01.pg."""
        # Simplified version of the actual file
        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl", "PGML.pl")

ans = -math.sqrt(3)/3

BEGIN_PGML
**Problem 1.** Calculate [`\\tan\\!\\left(\\frac{23\\pi}{6}\\right)`].

[_]{num_cmp(ans)}
END_PGML

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        result = translator.translate_source(pg_code, seed=1234)

        assert result.errors is None or len(result.errors) == 0
        assert "Problem 1." in result.statement_html  # Check content not HTML tags
        assert "tan" in result.statement_html
        assert "___ANSWER_BLANK_" in result.statement_html


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
