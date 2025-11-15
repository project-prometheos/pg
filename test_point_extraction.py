import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Algebra/PointAnswers.pg", seed=1234)

correct_answers = extract_correct_answers(result)
print("Extracted answers:")
for blank_name, answer in correct_answers.items():
    print(f"  {blank_name}: {answer}")

# Now test submission
check_result = translator.translate(
    "tutorial/sample-problems/Algebra/PointAnswers.pg",
    seed=1234,
    inputs=correct_answers
)

print(f"\nCheck result:")
print(f"  Score: {check_result.score}")
if check_result.answer_results:
    for blank_name, ans_result in check_result.answer_results.items():
        print(f"  {blank_name}: score={ans_result.score}")
else:
    print(f"  Answer results: (empty)")

