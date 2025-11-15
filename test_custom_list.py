import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/ProblemTechniques/CustomAnswerListChecker.pg", seed=1234)

print(f"Answer blanks: {list(result.answer_blanks.keys())}")

for name, info in result.answer_blanks.items():
    evaluator = info['evaluator']['ans_eval']
    print(f"\n{name}:")
    print(f"  Type: {type(evaluator).__name__}")
    print(f"  String: {str(evaluator)[:200]}")

correct_answers = extract_correct_answers(result)
print(f"\nExtracted answers: {correct_answers}")

# Try checking
try:
    check_result = translator.translate(
        "tutorial/sample-problems/ProblemTechniques/CustomAnswerListChecker.pg",
        seed=1234,
        inputs=correct_answers
    )
    print(f"\nCheck score: {check_result.score}")
    if check_result.errors:
        print(f"Errors: {check_result.errors}")
except Exception as e:
    print(f"Error during check: {e}")
    import traceback
    traceback.print_exc()

