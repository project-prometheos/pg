"""
Test rendering a real .pg file using PGTranslator.

This tests the complete pipeline from .pg file to HTML with answer evaluation.
"""

from pathlib import Path
from pg_translator import PGTranslator

print("=" * 70)
print("TEST: Rendering Real .pg File")
print("=" * 70)

# Create translator
translator = PGTranslator()

# Translate the problem
pg_file = Path("d:/pg/test_simple.pg")
result = translator.translate(pg_file, seed=123)

print(f"\n✅ Translation complete!")

# Check for errors
if result.errors:
    print(f"\n❌ Errors: {result.errors}")
else:
    print(f"\n✅ No errors")

# Display statement HTML
print(f"\n{'=' * 70}")
print("PROBLEM STATEMENT HTML:")
print("=" * 70)
print(result.statement_html)

# Display answer blanks
print(f"\n{'=' * 70}")
print("ANSWER BLANKS:")
print("=" * 70)
for name, info in result.answer_blanks.items():
    evaluator = info.get('evaluator')
    print(f"\nAnswer name: {name}")
    print(f"  Evaluator: {evaluator}")
    if hasattr(evaluator, 'correct_answer'):
        print(f"  Correct answer: {evaluator.correct_answer}")
    if hasattr(evaluator, 'tolerance'):
        print(f"  Tolerance: {evaluator.tolerance}")

# Test answer checking
print(f"\n{'=' * 70}")
print("TESTING ANSWER CHECKING:")
print("=" * 70)

# Get first answer name
if result.answer_blanks:
    first_answer_name = list(result.answer_blanks.keys())[0]

    # Test with correct answer
    test_inputs = {
        first_answer_name: "5"  # correct answer (2 + 3 = 5)
    }

    result_with_answers = translator.translate(
        pg_file, seed=123, inputs=test_inputs)

    if result_with_answers.answer_results:
        for name, ans_result in result_with_answers.answer_results.items():
            print(f"\nAnswer: {name}")
            print(f"  Student answer: '5'")
            print(f"  Correct: {ans_result.correct}")
            print(f"  Score: {ans_result.score}")
            if hasattr(ans_result, 'message') and ans_result.message:
                print(f"  Message: {ans_result.message}")

        print(f"\n🎉 Overall score: {result_with_answers.score}")
    else:
        print(f"\n⚠️ No answer results")

print(f"\n{'=' * 70}")
print("🎉 Real .pg file test complete!")
print("=" * 70)
