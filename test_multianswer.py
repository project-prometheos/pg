import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/Multianswer.pg", seed=1234)

print("First generation:")
print(f"  Answer blanks: {list(result.answer_blanks.keys())}")

correct_answers = extract_correct_answers(result)
print(f"\nExtracted answers: {correct_answers}")

check_result = translator.translate(
    "tutorial/sample-problems/ProblemTechniques/Multianswer.pg",
    seed=1234,
    inputs=correct_answers
)

print(f"\nCheck result:")
print(f"  Score: {check_result.score}")
print(f"  Answer results: {check_result.answer_results}")
print(f"  Answer blanks in check: {list(check_result.answer_blanks.keys())}")

