import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

# Monkey-patch the _evaluate_answers method to add debug output
original_evaluate = PGTranslator._evaluate_answers

def debug_evaluate(self, environment, raw_inputs):
    print(f"\n=== _evaluate_answers called ===")
    print(f"raw_inputs: {raw_inputs}")
    print(f"environment.answers keys: {list(environment.answers.keys())}")
    print(f"environment.answers values: {list(environment.answers.values())}")
    result = original_evaluate(self, environment, raw_inputs)
    print(f"answer_results: {result}")
    return result

PGTranslator._evaluate_answers = debug_evaluate

translator = PGTranslator()

# First call - generate problem
result = translator.translate("tutorial/sample-problems/Algebra/PointAnswers.pg", seed=1234)
print("First generation:")
print(f"  answer_blanks keys: {list(result.answer_blanks.keys())}")

# Extract answers
correct_answers = extract_correct_answers(result)
print(f"\nExtracted answers: {correct_answers}")

# Second call - check answers
print("\n=== Starting answer check ===")
check_result = translator.translate(
    "tutorial/sample-problems/Algebra/PointAnswers.pg",
    seed=1234,
    inputs=correct_answers
)

print(f"\nFinal result:")
print(f"  Score: {check_result.score}")
print(f"  answer_results: {check_result.answer_results}")

