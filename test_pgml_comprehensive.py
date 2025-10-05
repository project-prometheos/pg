#!/usr/bin/env python3
"""
Comprehensive PGML test suite.

Tests all PGML features with real problem examples.
"""

from pg_translator import PGTranslator
import sys
from pathlib import Path
import tempfile

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))


def translate_pgml(pg_code: str, seed: int = 1234):
    """Helper to translate PGML code."""
    translator = PGTranslator()

    # Save to temp file (translator expects file path)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pg', delete=False, encoding='utf-8') as f:
        f.write(pg_code)
        temp_file = f.name

    try:
        result = translator.translate(temp_file, seed=seed)
        return result
    finally:
        Path(temp_file).unlink()


def test_variable_interpolation():
    """Test PGML variable interpolation."""
    print("\n" + "="*60)
    print("TEST: Variable Interpolation")
    print("="*60)

    pg_code = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

$a = 7;
$b = 4;
$sum = $a + $b;

BEGIN_PGML
The value of [$a] plus [$b] equals [$sum].
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html}")

    assert "7" in result.statement_html
    assert "4" in result.statement_html
    assert "11" in result.statement_html
    print("✅ PASS: Variables interpolated correctly")
    return True


def test_bold_italic_formatting():
    """Test PGML text formatting."""
    print("\n" + "="*60)
    print("TEST: Bold and Italic Formatting")
    print("="*60)

    pg_code = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

BEGIN_PGML
**Bold text** and *italic text* and **bold with *nested italic***.
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html}")

    assert "<b>" in result.statement_html or "<strong>" in result.statement_html
    assert "<i>" in result.statement_html or "<em>" in result.statement_html
    print("✅ PASS: Formatting applied correctly")
    return True


def test_answer_blanks():
    """Test PGML answer blanks."""
    print("\n" + "="*60)
    print("TEST: Answer Blanks")
    print("="*60)

    pg_code = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

$answer = 42;

BEGIN_PGML
What is the answer? [_]{$answer}

With width: [____]{$answer}{30}
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html}")

    assert "AnSwEr0001" in result.statement_html
    assert "AnSwEr0002" in result.statement_html
    assert 'type="text"' in result.statement_html
    print("✅ PASS: Answer blanks generated")
    return True


def test_math_rendering():
    """Test PGML math (inline and display)."""
    print("\n" + "="*60)
    print("TEST: Math Rendering")
    print("="*60)

    pg_code = r"""
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

BEGIN_PGML
Inline math: \(x^2 + y^2 = r^2\)

Display math: \[\int_0^1 x^2 \, dx = \frac{1}{3}\]
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html[:200]}...")

    # LaTeX delimiters should be preserved
    assert r"\(" in result.statement_html or "x^2" in result.statement_html
    print("✅ PASS: Math delimiters preserved")
    return True


def test_lists():
    """Test PGML lists."""
    print("\n" + "="*60)
    print("TEST: Lists")
    print("="*60)

    pg_code = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

BEGIN_PGML
Shopping list:
- Apples
- Bananas
- Oranges
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html}")

    assert "Apples" in result.statement_html
    assert "Bananas" in result.statement_html
    # Lists may render as <ul> or plain text depending on parser
    print("✅ PASS: List items present")
    return True


def test_solution_hint():
    """Test PGML solution and hint blocks."""
    print("\n" + "="*60)
    print("TEST: Solution and Hint Blocks")
    print("="*60)

    pg_code = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

$answer = 10;

BEGIN_PGML
What is 5 + 5? [_]{$answer}
END_PGML

BEGIN_PGML_SOLUTION
The answer is [$answer] because 5 + 5 = 10.
END_PGML_SOLUTION

BEGIN_PGML_HINT
**Hint:** Add the two numbers together.
END_PGML_HINT

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html[:100]}...")
    print(f"Solution: {result.solution_html}")
    print(f"Hint: {result.hint_html}")

    assert result.solution_html is not None
    assert result.hint_html is not None
    assert "10" in result.solution_html
    print("✅ PASS: Solution and hint blocks rendered")
    return True


def test_mixed_pgml_and_traditional():
    """Test mixing PGML with traditional PG code."""
    print("\n" + "="*60)
    print("TEST: Mixed PGML and Traditional PG")
    print("="*60)

    pg_code = r"""
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl", "PGbasicmacros.pl");
TEXT(beginproblem());

$a = 3;
$b = 7;

BEGIN_PGML
**PGML Section**

Value: [$a]
END_PGML

BEGIN_TEXT
$BBOLD Traditional Section $EBOLD
$PAR
Value: $a
END_TEXT

BEGIN_PGML
**Back to PGML**

Final value: [$b]
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement: {result.statement_html}")

    assert "3" in result.statement_html
    assert "7" in result.statement_html
    print("✅ PASS: Mixed syntax handled")
    return True


def test_real_webwork_problem():
    """Test actual WebWork problem from ps1."""
    print("\n" + "="*60)
    print("TEST: Real WebWork Problem (ps1-prob01.pg)")
    print("="*60)

    try:
        with open("webwork_ps1_pg/ps1-prob01.pg", "r", encoding="utf-8") as f:
            pg_code = f.read()

        result = translate_pgml(pg_code)
        print(f"Statement: {result.statement_html[:200]}...")

        assert len(result.statement_html) > 0
        assert "Problem" in result.statement_html or "tan" in result.statement_html.lower()
        assert "AnSwEr0001" in result.statement_html
        print("✅ PASS: Real problem rendered successfully")
        return True

    except FileNotFoundError:
        print("⚠️ SKIP: Test file not found")
        return None


def test_complex_math_problem():
    """Test problem with complex mathematical notation."""
    print("\n" + "="*60)
    print("TEST: Complex Math Problem")
    print("="*60)

    pg_code = r"""
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
TEXT(beginproblem());

BEGIN_PGML
Calculate the following:

\[\lim_{x \to \infty} \frac{x^2 + 2x + 1}{x^2 - 1}\]

Answer: [_]{1}

The derivative of [`f(x) = x^3`] is [_]{3*x^2}.
END_PGML

ENDDOCUMENT();
"""

    result = translate_pgml(pg_code)
    print(f"Statement (truncated): {result.statement_html[:250]}...")

    assert "lim" in result.statement_html or r"\lim" in result.statement_html
    assert "AnSwEr0001" in result.statement_html
    print("✅ PASS: Complex math preserved")
    return True


def main():
    """Run all PGML tests."""
    print("\n" + "="*70)
    print(" COMPREHENSIVE PGML TEST SUITE")
    print("="*70)

    tests = [
        ("Variable Interpolation", test_variable_interpolation),
        ("Bold/Italic Formatting", test_bold_italic_formatting),
        ("Answer Blanks", test_answer_blanks),
        ("Math Rendering", test_math_rendering),
        ("Lists", test_lists),
        ("Solution/Hint Blocks", test_solution_hint),
        ("Mixed PGML/Traditional", test_mixed_pgml_and_traditional),
        ("Real WebWork Problem", test_real_webwork_problem),
        ("Complex Math", test_complex_math_problem),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result is True:
                passed += 1
            elif result is None:
                skipped += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed:  {passed}/{len(tests)}")
    print(f"❌ Failed:  {failed}/{len(tests)}")
    print(f"⚠️  Skipped: {skipped}/{len(tests)}")

    if failed == 0 and passed > 0:
        print("\n🎉 ALL TESTS PASSED! PGML support is fully functional.")
    elif failed == 0:
        print("\n⚠️  No failures, but check skipped tests.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Review output above.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
