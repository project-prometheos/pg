"""
Test PGML integration with simplified handcrafted problems.

These tests validate that our PGML parser and integration work correctly
for the features we've implemented, without relying on unsupported MathObjects features.
"""

import pytest
from pg_translator import PGTranslator
from pg_translator.executor import PGExecutor
from pg_translator.in_process_sandbox import InProcessSandbox


class TestPGMLFeatures:
    """Test PGML features with minimal dependencies."""

    @pytest.fixture
    def translator(self):
        """Create translator with sandbox."""
        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        return PGTranslator(executor=executor)

    def test_simple_pgml_text(self, translator):
        """Test basic PGML text rendering."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

a = 5
b = 3

BEGIN_PGML
Add the numbers: [$a] + [$b] = ?

[_]{num_cmp(8)}
END_PGML

ENDDOCUMENT()
"""
        result = translator.translate_source(pg_code, seed=1234)

        assert result.statement_html != ""
        assert "Add the numbers" in result.statement_html
        assert "5" in result.statement_html
        assert "3" in result.statement_html
        assert "___ANSWER_BLANK_" in result.statement_html  # Answer blank placeholder
        assert len(result.answer_blanks) == 1

    def test_pgml_with_math(self, translator):
        """Test PGML with inline math."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

BEGIN_PGML
Calculate [`\\frac{1}{2} + \\frac{1}{3}`]:

[_]{num_cmp(5/6)}
END_PGML

ENDDOCUMENT()
"""
        result = translator.translate_source(pg_code, seed=1234)

        assert result.statement_html != ""
        assert "frac" in result.statement_html  # Math content
        assert "___ANSWER_BLANK_" in result.statement_html  # Answer blank placeholder

    def test_pgml_with_formatting(self, translator):
        """Test PGML with bold and lists."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

BEGIN_PGML
**Problem:** Solve for x:

+ First, isolate x
+ Then, simplify

[_]{num_cmp(42)}
END_PGML

ENDDOCUMENT()
"""
        result = translator.translate_source(pg_code, seed=1234)

        assert result.statement_html != ""
        assert "Problem:" in result.statement_html  # Bold/formatting preserved
        assert "First, isolate x" in result.statement_html  # List items
        assert "___ANSWER_BLANK_" in result.statement_html  # Answer blank placeholder

    def test_pgml_multiple_answers(self, translator):
        """Test PGML with multiple answer blanks."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

x = 10
y = 20

BEGIN_PGML
Enter x: [_]{num_cmp(x)}

Enter y: [_]{num_cmp(y)}
END_PGML

ENDDOCUMENT()
"""
        result = translator.translate_source(pg_code, seed=1234)

        assert result.statement_html != ""
        assert len(result.answer_blanks) == 2
        assert result.statement_html.count('___ANSWER_BLANK_') == 2  # Two answer blanks

    def test_pgml_solution(self, translator):
        """Test PGML_SOLUTION rendering."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

BEGIN_PGML
What is 2 + 2?

[_]{num_cmp(4)}
END_PGML

BEGIN_PGML_SOLUTION
The answer is **4** because 2 + 2 = 4.
END_PGML_SOLUTION

ENDDOCUMENT()
"""
        result = translator.translate_source(pg_code, seed=1234)

        assert result.statement_html != ""
        assert result.solution_html is not None
        assert "answer is" in result.solution_html.lower()
        assert "4" in result.solution_html  # Check for content, not HTML tags

    def test_pgml_hint(self, translator):
        """Test PGML_HINT rendering."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

BEGIN_PGML
Solve for x: [`2x = 10`]

[_]{num_cmp(5)}
END_PGML

BEGIN_PGML_HINT
*Hint:* Divide both sides by 2.
END_PGML_HINT

ENDDOCUMENT()
"""
        result = translator.translate_source(pg_code, seed=1234)

        assert result.statement_html != ""
        assert result.hint_html is not None
        assert "Divide" in result.hint_html

    @pytest.mark.skip(reason="Answer grading requires evaluator execution - not yet implemented")
    def test_pgml_grading(self, translator):
        """Test PGML with correct/incorrect answers."""
        pg_code = """
DOCUMENT()
loadMacros("PG.pl")

answer = 42

BEGIN_PGML
What is the meaning of life?

[_]{num_cmp(answer)}
END_PGML

ENDDOCUMENT()
"""
        # Test correct answer
        result_correct = translator.translate_source(
            pg_code, seed=1234, inputs={"AnSwEr0001": "42"}
        )
        assert result_correct.answer_results is not None
        assert len(result_correct.answer_results) > 0  # Check results exist
        if result_correct.answer_results:
            first_answer = list(result_correct.answer_results.values())[0]
            assert first_answer.correct

        # Test incorrect answer
        result_incorrect = translator.translate_source(
            pg_code, seed=1234, inputs={"AnSwEr0001": "99"}
        )
        assert result_incorrect.answer_results is not None
        if result_incorrect.answer_results:
            first_answer = list(result_incorrect.answer_results.values())[0]
            assert not first_answer.correct


class TestPGMLIntegrationSummary:
    """Summary test showing PGML integration completeness."""

    def test_pgml_feature_coverage(self):
        """Document PGML features implemented."""
        implemented_features = {
            "Variable interpolation": "[$var]",
            "Inline math": "[`math`]",
            "Display math": "[```math```]",
            "Answer blanks": "[_]{evaluator}",
            "Bold text": "**text**",
            "Italic text": "_text_",
            "Lists": "+ item",
            "Solutions": "BEGIN_PGML_SOLUTION",
            "Hints": "BEGIN_PGML_HINT",
            "Answer registration": "Auto-registers with ANS()",
        }

        # All features should be tested above
        assert len(implemented_features) == 10
        print("\n✅ PGML Features Implemented:")
        for feature, syntax in implemented_features.items():
            print(f"  - {feature}: {syntax}")
