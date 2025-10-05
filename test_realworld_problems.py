#!/usr/bin/env python3
"""
Test real-world PG files from tutorial and webwork_ps1_pg.

Tests a sample of problems from different categories to validate
that the pg_translator handles diverse problem types correctly.
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


def test_problem(file_path: Path, seed: int = 1234, verbose: bool = False) -> dict:
    """
    Test a single PG problem file.

    Args:
        file_path: Path to .pg file
        seed: Random seed
        verbose: Print detailed output

    Returns:
        Dict with test results
    """
    result = {
        'file': file_path.name,
        'path': str(file_path),
        'success': False,
        'has_statement': False,
        'has_answers': False,
        'has_solution': False,
        'has_hint': False,
        'error': None,
        'statement_length': 0,
        'answer_count': 0,
    }

    try:
        translator = PGTranslator()
        pg_result = translator.translate(str(file_path), seed=seed)

        # DEBUG
        if 'IndefiniteIntegrals' in str(file_path):
            print(f"  [DEBUG] statement_html: {len(pg_result.statement_html) if pg_result.statement_html else 0} chars")
            print(f"  [DEBUG] answer_blanks: {len(pg_result.answer_blanks) if pg_result.answer_blanks else 0}")
        
        result['success'] = True
        result['has_statement'] = bool(pg_result.statement_html)
        result['has_answers'] = bool(pg_result.answer_blanks)
        result['has_solution'] = bool(pg_result.solution_html)
        result['has_hint'] = bool(pg_result.hint_html)
        result['statement_length'] = len(
            pg_result.statement_html) if pg_result.statement_html else 0
        result['answer_count'] = len(
            pg_result.answer_blanks) if pg_result.answer_blanks else 0

        if verbose:
            print(f"\n{'='*60}")
            print(f"File: {file_path.name}")
            print(f"{'='*60}")
            if pg_result.statement_html:
                print(f"Statement ({len(pg_result.statement_html)} chars):")
                print(f"  {pg_result.statement_html[:200]}...")
            else:
                print(f"Statement: NONE")

            if pg_result.answer_blanks:
                print(f"Answers: {len(pg_result.answer_blanks)} blank(s)")
                for i, blank in enumerate(pg_result.answer_blanks, 1):
                    print(f"  {i}. {blank.get('name', 'unnamed')}")
            else:
                print(f"Answers: NONE")

            if pg_result.solution_html:
                print(f"Solution: {pg_result.solution_html[:100]}...")
            if pg_result.hint_html:
                print(f"Hint: {pg_result.hint_html[:100]}...")

    except Exception as e:
        result['error'] = str(e)
        if verbose:
            print(f"\n{'='*60}")
            print(f"File: {file_path.name}")
            print(f"{'='*60}")
            print(f"ERROR: {e}")

    return result


def main():
    """Test a sample of real-world problems."""

    print("="*70)
    print(" REAL-WORLD PG FILES TEST SUITE")
    print("="*70)

    # Define test problems from different categories
    test_files = [
        # WebWork PS1 problems (Swedish course, PGML)
        "webwork_ps1_pg/ps1-prob01.pg",  # Trigonometry
        "webwork_ps1_pg/ps1-prob02.pg",  # Trigonometry with inequality
        "webwork_ps1_pg/ps1-prob05.pg",  # Square root expression
        "webwork_ps1_pg/ps1-prob10.pg",  # Multiple parts
        "webwork_ps1_pg/ps1-prob15.pg",  # More variety

        # Tutorial: Algebra (PGML)
        "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg",
        "tutorial/sample-problems/Algebra/FractionAnswer.pg",
        "tutorial/sample-problems/Algebra/FactoredPolynomial.pg",
        "tutorial/sample-problems/Algebra/InequalityAnswer.pg",
        "tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg",

        # Tutorial: Differential Calculus (PGML, complex)
        "tutorial/sample-problems/DiffCalc/DifferentiateFunction.pg",
        "tutorial/sample-problems/DiffCalc/LinearApprox.pg",
        "tutorial/sample-problems/DiffCalc/AnswerWithUnits.pg",

        # Tutorial: Integral Calculus (PGML)
        "tutorial/sample-problems/IntegralCalc/IndefiniteIntegrals.pg",
        "tutorial/sample-problems/IntegralCalc/LimitsOfIntegration.pg",
        "tutorial/sample-problems/IntegralCalc/DoubleIntegral.pg",

        # Tutorial: Trigonometry (PGML)
        "tutorial/sample-problems/Trig/SpecialTrigValues.pg",
        "tutorial/sample-problems/Trig/PeriodicAnswers.pg",
        "tutorial/sample-problems/Trig/ProvingTrigIdentities.pg",

        # Tutorial: Sequences (PGML)
        "tutorial/sample-problems/Sequences/RecursiveSequence.pg",
    ]

    results = []
    base_path = Path(__file__).parent

    for file_rel_path in test_files:
        file_path = base_path / file_rel_path

        if not file_path.exists():
            print(f"\n[SKIP] {file_rel_path} - File not found")
            continue

        print(f"\n[TEST] {file_rel_path}")
        result = test_problem(file_path, verbose=False)
        results.append(result)

        if result['success']:
            status = "PASS"
            details = []
            if result['has_statement']:
                details.append(f"{result['statement_length']} chars")
            if result['has_answers']:
                details.append(f"{result['answer_count']} answer(s)")
            if result['has_solution']:
                details.append("solution")
            if result['has_hint']:
                details.append("hint")

            details_str = ", ".join(details) if details else "no content"
            print(f"  [{status}] {details_str}")
        else:
            status = "FAIL"
            print(f"  [{status}] {result['error'][:80]}...")

    # Summary statistics
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)

    total = len(results)
    passed = sum(1 for r in results if r['success'])
    failed = total - passed

    with_statement = sum(1 for r in results if r['has_statement'])
    with_answers = sum(1 for r in results if r['has_answers'])
    with_solution = sum(1 for r in results if r['has_solution'])
    with_hint = sum(1 for r in results if r['has_hint'])

    print(f"\nTotal tested:      {total}")
    print(f"Passed:            {passed} ({100*passed/total:.0f}%)")
    print(f"Failed:            {failed}")
    print(f"\nFeature coverage:")
    print(
        f"  With statement:  {with_statement}/{total} ({100*with_statement/total:.0f}%)")
    print(
        f"  With answers:    {with_answers}/{total} ({100*with_answers/total:.0f}%)")
    print(f"  With solution:   {with_solution}/{total}")
    print(f"  With hint:       {with_hint}/{total}")

    # Category breakdown
    webwork_results = [r for r in results if 'webwork_ps1_pg' in r['path']]
    tutorial_results = [r for r in results if 'tutorial' in r['path']]

    if webwork_results:
        webwork_passed = sum(1 for r in webwork_results if r['success'])
        print(
            f"\nWebWork PS1:       {webwork_passed}/{len(webwork_results)} passed")

    if tutorial_results:
        tutorial_passed = sum(1 for r in tutorial_results if r['success'])
        print(
            f"Tutorial samples:  {tutorial_passed}/{len(tutorial_results)} passed")

    # Detailed failures
    failures = [r for r in results if not r['success']]
    if failures:
        print(f"\n{'='*70}")
        print(" FAILURES")
        print("="*70)
        for r in failures:
            print(f"\n{r['file']}:")
            print(f"  {r['error']}")

    # Success message
    if failed == 0:
        print(f"\n{'='*70}")
        print(" SUCCESS!")
        print(f" All {passed} real-world problems translated successfully!")
        print("="*70)
    else:
        print(f"\n{'='*70}")
        print(f" {failed} problem(s) need attention")
        print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
