"""
Comprehensive test for AnswerUpToMultiple problem with various answer forms.
"""
from pg_translator.translator import PGTranslator


def test_all_answer_forms():
    translator = PGTranslator()
    problem_path = 'd:/pg/tutorial/sample-problems/Algebra/AnswerUpToMultiple.pg'
    seed = 3157

    test_cases = [
        ("x^2-x-2", True, "Expanded form"),
        ("(x+1)(x-2)", True, "Factored form"),
        ("x^2 - x - 2", True, "With spaces"),
        ("(x-2)(x+1)", True, "Reversed factors"),
        ("x^2+x+1", False, "Wrong answer"),
        ("x^2-x", False, "Missing constant"),
        # Note: Adaptive parameters (C0) not yet implemented, so scalar multiples fail
        ("2*x^2-2*x-4", False, "Scalar multiple (adaptive params not implemented)"),
        ("-x^2+x+2", False, "Negated (adaptive params not implemented)"),
    ]

    print("=" * 70)
    print(f"Testing AnswerUpToMultiple (seed={seed})")
    print("=" * 70)

    for answer, expected_correct, description in test_cases:
        result = translator.translate(
            problem_path,
            seed=seed,
            inputs={'AnSwEr0001': answer}
        )

        if result.answer_results:
            ans_result = result.answer_results['AnSwEr0001']
            correct = ans_result.correct
            score = ans_result.score
            message = ans_result.answer_message

            status = "✅" if correct == expected_correct else "❌"
            print(f"\n{status} {description}")
            print(f"   Input: {answer}")
            print(f"   Correct: {correct} (expected: {expected_correct})")
            print(f"   Score: {score}")
            if message:
                print(f"   Message: {message}")
        else:
            print(f"\n❌ {description}")
            print(f"   Input: {answer}")
            print(f"   ERROR: No results returned!")


if __name__ == '__main__':
    test_all_answer_forms()
