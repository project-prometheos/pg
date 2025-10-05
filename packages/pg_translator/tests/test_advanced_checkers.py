"""
Tests for advanced answer checkers (str_cmp, fun_cmp, enhanced num_cmp).

Tests Week 3 Day 1 functionality.
"""

import pytest

from pg_answer import fun_cmp, num_cmp, str_cmp


class TestStrCmp:
    """Test str_cmp() string answer checker."""

    def test_str_cmp_case_insensitive_default(self):
        """Test case-insensitive matching (default)."""
        evaluator = str_cmp("Hello")

        # Should match regardless of case
        assert evaluator.evaluate("hello").correct
        assert evaluator.evaluate("HELLO").correct
        assert evaluator.evaluate("Hello").correct
        assert evaluator.evaluate("HeLLo").correct

    def test_str_cmp_case_sensitive(self):
        """Test case-sensitive matching."""
        evaluator = str_cmp("Hello", case_sensitive=True)

        # Only exact match should work
        assert evaluator.evaluate("Hello").correct
        assert not evaluator.evaluate("hello").correct
        assert not evaluator.evaluate("HELLO").correct

    def test_str_cmp_whitespace_trimming(self):
        """Test whitespace trimming (default)."""
        evaluator = str_cmp("hello world")

        # Leading/trailing whitespace should be trimmed
        assert evaluator.evaluate("  hello world  ").correct
        assert evaluator.evaluate("hello world   ").correct
        assert evaluator.evaluate("   hello world").correct

        # Internal whitespace preserved
        assert not evaluator.evaluate("hello   world").correct

    def test_str_cmp_no_whitespace_trimming(self):
        """Test without whitespace trimming."""
        evaluator = str_cmp("hello", trim_whitespace=False)

        # Must match exactly including whitespace
        assert evaluator.evaluate("hello").correct
        assert not evaluator.evaluate(" hello").correct
        assert not evaluator.evaluate("hello ").correct

    def test_str_cmp_regex_matching(self):
        """Test regex pattern matching."""
        # Simple pattern
        evaluator = str_cmp(r"\d+", regex_match=True)
        assert evaluator.evaluate("123").correct
        assert evaluator.evaluate("0").correct
        assert not evaluator.evaluate("abc").correct

        # More complex pattern - case sensitive
        evaluator = str_cmp(r"[A-Z][a-z]+", regex_match=True, case_sensitive=True)
        assert evaluator.evaluate("Hello").correct
        assert evaluator.evaluate("World").correct
        assert not evaluator.evaluate("hello").correct  # Case-sensitive now

    def test_str_cmp_regex_case_insensitive(self):
        """Test regex with case-insensitive flag."""
        evaluator = str_cmp(r"hello", regex_match=True, case_sensitive=False)
        assert evaluator.evaluate("hello").correct
        assert evaluator.evaluate("HELLO").correct
        assert evaluator.evaluate("Hello").correct

    def test_str_cmp_empty_string(self):
        """Test empty string matching."""
        evaluator = str_cmp("")
        assert evaluator.evaluate("").correct
        assert not evaluator.evaluate("something").correct

    def test_str_cmp_special_characters(self):
        """Test strings with special characters."""
        evaluator = str_cmp("a+b=c")
        assert evaluator.evaluate("a+b=c").correct
        assert evaluator.evaluate("A+B=C").correct  # Case-insensitive default

        evaluator = str_cmp("$100.00", case_sensitive=True)
        assert evaluator.evaluate("$100.00").correct


class TestNumCmp:
    """Test num_cmp() numeric answer checker."""

    def test_num_cmp_exact_match(self):
        """Test exact number matching."""
        evaluator = num_cmp(42)
        assert evaluator.evaluate("42").correct
        assert evaluator.evaluate("42.0").correct

    def test_num_cmp_relative_tolerance(self):
        """Test relative tolerance (default mode)."""
        # 0.001 = 0.1% tolerance
        evaluator = num_cmp(100, tolerance=0.01)  # 1% tolerance

        assert evaluator.evaluate("100").correct
        assert evaluator.evaluate("101").correct  # Within 1%
        assert evaluator.evaluate("99").correct  # Within 1%
        assert not evaluator.evaluate("102").correct  # Outside 1%
        assert not evaluator.evaluate("98").correct  # Outside 1%

    def test_num_cmp_absolute_tolerance(self):
        """Test absolute tolerance mode."""
        evaluator = num_cmp(100, tolerance=0.5, tolerance_mode="absolute")

        assert evaluator.evaluate("100").correct
        assert evaluator.evaluate("100.4").correct
        assert evaluator.evaluate("99.6").correct
        assert not evaluator.evaluate("100.6").correct
        assert not evaluator.evaluate("99.4").correct

    def test_num_cmp_small_numbers(self):
        """Test small numbers near zero."""
        evaluator = num_cmp(0.001, tolerance=0.1)  # 10% tolerance
        assert evaluator.evaluate("0.001").correct
        assert evaluator.evaluate("0.0011").correct
        assert evaluator.evaluate("0.0009").correct

    def test_num_cmp_negative_numbers(self):
        """Test negative numbers."""
        evaluator = num_cmp(-50, tolerance=0.02)  # 2% tolerance
        assert evaluator.evaluate("-50").correct
        assert evaluator.evaluate("-51").correct
        assert evaluator.evaluate("-49").correct

    def test_num_cmp_decimal_input(self):
        """Test decimal inputs."""
        evaluator = num_cmp(3.14159, tolerance=0.001)
        assert evaluator.evaluate("3.14159").correct
        assert evaluator.evaluate("3.14").correct  # Within tolerance
        assert evaluator.evaluate("3.142").correct

    def test_num_cmp_scientific_notation(self):
        """Test scientific notation."""
        evaluator = num_cmp(1.23e-5, tolerance=0.01)
        assert evaluator.evaluate("1.23e-5").correct
        assert evaluator.evaluate("0.0000123").correct


class TestFunCmp:
    """Test fun_cmp() formula answer checker."""

    def test_fun_cmp_simple_formula(self):
        """Test simple formula matching."""
        evaluator = fun_cmp("x^2 + 1", var="x")

        # Equivalent forms
        assert evaluator.evaluate("x**2 + 1").correct
        assert evaluator.evaluate("x*x + 1").correct
        assert evaluator.evaluate("1 + x^2").correct  # Commutative

    def test_fun_cmp_polynomial(self):
        """Test polynomial expressions."""
        evaluator = fun_cmp("x^2 + 2*x + 1", var="x")

        # Different forms of (x+1)^2
        assert evaluator.evaluate("x^2 + 2*x + 1").correct
        assert evaluator.evaluate("(x+1)^2").correct
        assert evaluator.evaluate("(x+1)*(x+1)").correct

    def test_fun_cmp_trig_functions(self):
        """Test trigonometric functions."""
        evaluator = fun_cmp("sin(x)", var="x")
        assert evaluator.evaluate("sin(x)").correct

        evaluator = fun_cmp("cos(x)^2 + sin(x)^2", var="x")
        assert evaluator.evaluate("1").correct  # Trig identity

    def test_fun_cmp_multi_variable(self):
        """Test multi-variable formulas."""
        evaluator = fun_cmp("x + y", var=["x", "y"])
        assert evaluator.evaluate("y + x").correct  # Commutative
        assert evaluator.evaluate("x + y").correct

    def test_fun_cmp_with_limits(self):
        """Test formula with custom test limits."""
        evaluator = fun_cmp("x^2", var="x", limits=[(-10, 10)])
        assert evaluator.evaluate("x*x").correct

    def test_fun_cmp_with_tolerance(self):
        """Test formula with custom tolerance."""
        evaluator = fun_cmp("x", var="x", tolerance=0.1)
        assert evaluator.evaluate("x").correct

    def test_fun_cmp_constant_formula(self):
        """Test constant (no variables)."""
        evaluator = fun_cmp("5", var="x")
        assert evaluator.evaluate("5").correct
        assert evaluator.evaluate("2+3").correct


class TestIntegration:
    """Integration tests with full problem examples."""

    def test_problem_with_string_answer(self):
        """Test complete problem with string answer."""
        from pg_translator import PGTranslator
        from pg_translator.executor import PGExecutor
        from pg_translator.in_process_sandbox import InProcessSandbox

        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("What is the capital of France?")
TEXT(ans_rule(20))

ANS(str_cmp("Paris", case_sensitive=False))

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        # Translate and render
        result = translator.translate_source(pg_code, seed=1234)
        assert result.errors is None or len(result.errors) == 0
        assert "What is the capital of France?" in result.statement_html
        assert len(result.answer_blanks) == 1

        # Grade correct answers (case variations)
        for answer in ["Paris", "paris", "PARIS"]:
            graded = translator.translate_source(
                pg_code, seed=1234, inputs={"AnSwEr0001": answer}
            )
            assert graded.answer_results is not None
            first_result = list(graded.answer_results.values())[0]
            assert first_result.correct, f"'{answer}' should be correct"
            assert graded.score == 1.0

        # Grade incorrect answer
        graded = translator.translate_source(
            pg_code, seed=1234, inputs={"AnSwEr0001": "London"}
        )
        assert graded.answer_results is not None
        first_result = list(graded.answer_results.values())[0]
        assert not first_result.correct
        assert graded.score == 0.0

    def test_problem_with_formula_answer(self):
        """Test complete problem with formula answer."""
        from pg_translator import PGTranslator
        from pg_translator.executor import PGExecutor
        from pg_translator.in_process_sandbox import InProcessSandbox

        pg_code = """
DOCUMENT()
loadMacros("PG.pl", "PGbasicmacros.pl")

TEXT("Simplify: (x+1)^2")
TEXT(ans_rule(20))

ANS(fun_cmp("x^2 + 2*x + 1", var="x"))

ENDDOCUMENT()
"""

        sandbox = InProcessSandbox(timeout=10)
        executor = PGExecutor()
        executor.sandbox = sandbox
        translator = PGTranslator(executor=executor)

        # Translate and render
        result = translator.translate_source(pg_code, seed=1234)
        assert result.errors is None or len(result.errors) == 0
        assert "Simplify" in result.statement_html

        # Grade equivalent forms
        for answer in ["x^2 + 2*x + 1", "(x+1)^2", "x*x + 2*x + 1"]:
            graded = translator.translate_source(
                pg_code, seed=1234, inputs={"AnSwEr0001": answer}
            )
            if graded.answer_results:
                first_result = list(graded.answer_results.values())[0]
                assert first_result.correct, f"'{answer}' should be correct"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
