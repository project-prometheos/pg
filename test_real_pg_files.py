"""
Test real .pg files with pg_translator.
"""

from pg_translator import PGTranslator
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))


def test_pg_file(file_path: str, seed: int = 123):
    """Test a single .pg file."""
    print("=" * 70)
    print(f"Testing: {file_path}")
    print("=" * 70)

    translator = PGTranslator()

    try:
        # Translate the problem
        result = translator.translate(file_path, seed=seed)

        if result.errors:
            print(f"\n[ERROR] Translation failed:")
            for error in result.errors:
                print(f"  {error}")
            return False

        # Display statement
        print("\n[STATEMENT]")
        print(result.statement_html)

        # Display solution
        if result.solution_html:
            print("\n[SOLUTION]")
            print(result.solution_html)

        # Display hint
        if result.hint_html:
            print("\n[HINT]")
            print(result.hint_html)

        # Display answers
        print("\n[ANSWERS]")
        if result.answer_blanks:
            for name, blank_info in result.answer_blanks.items():
                print(f"  {name}: {type(blank_info).__name__}")
                if isinstance(blank_info, dict) and 'evaluator' in blank_info:
                    eval_info = blank_info['evaluator']
                    if isinstance(eval_info, dict) and 'ans_eval' in eval_info:
                        evaluator = eval_info['ans_eval']
                        print(f"    Type: {type(evaluator).__name__}")
                        if hasattr(evaluator, 'correct_answer'):
                            print(f"    Correct: {evaluator.correct_answer}")
        else:
            print("  (none)")

        # Test answer checking
        print("\n[ANSWER CHECK]")
        if result.answer_blanks:
            # Get first answer blank
            first_name = list(result.answer_blanks.keys())[0]
            first_blank = result.answer_blanks[first_name]

            # Extract evaluator
            evaluator = None
            if isinstance(first_blank, dict) and 'evaluator' in first_blank:
                eval_info = first_blank['evaluator']
                if isinstance(eval_info, dict) and 'ans_eval' in eval_info:
                    evaluator = eval_info['ans_eval']

            if evaluator and hasattr(evaluator, 'correct_answer'):
                correct = str(evaluator.correct_answer)
                print(f"  Testing with correct answer: {correct}")

                # Translate again with inputs
                result_with_check = translator.translate(
                    file_path,
                    seed=seed,
                    inputs={first_name: correct}
                )

                if result_with_check.answer_results:
                    for name, ans_result in result_with_check.answer_results.items():
                        print(
                            f"  {name}: {ans_result.correct} (score: {ans_result.score})")
                else:
                    print("  (no results)")

        print("\n[OK] Test passed!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    problems = [
        ("Simple arithmetic", "test_problems/simple_arithmetic.pg"),
        ("Multiple answers", "test_problems/multiple_answers.pg"),
        ("With solution", "test_problems/with_solution.pg"),
    ]

    passed = 0
    failed = 0

    for name, path in problems:
        print(f"\n{'='*70}")
        print(f"TEST: {name}")
        print('='*70)
        if test_pg_file(path):
            passed += 1
        else:
            failed += 1
        print()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(problems)}")
    print(f"Failed: {failed}/{len(problems)}")

    if failed == 0:
        print("\n[OK] All tests passed!")
    else:
        print(f"\n[FAIL] {failed} test(s) failed")
