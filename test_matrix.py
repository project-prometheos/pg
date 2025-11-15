import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test MatrixAnswer2
print("=" * 60)
print("Testing MatrixAnswer2")
print("=" * 60)

result = translator.translate("tutorial/sample-problems/LinearAlgebra/MatrixAnswer2.pg", seed=1234)

print(f"Answer blanks: {list(result.answer_blanks.keys())}")

for name, info in result.answer_blanks.items():
    evaluator = info['evaluator']['ans_eval']
    print(f"\n{name}:")
    print(f"  Type: {type(evaluator).__name__}")
    print(f"  Has .compare(): {hasattr(evaluator, 'compare')}")
    print(f"  Has .check(): {hasattr(evaluator, 'check')}")
    print(f"  Has .cmp(): {hasattr(evaluator, 'cmp')}")
    print(f"  Has .evaluate(): {hasattr(evaluator, 'evaluate')}")
    print(f"  String: {str(evaluator)}")

correct_answers = extract_correct_answers(result)
print(f"\nExtracted answers: {correct_answers}")

if correct_answers:
    check_result = translator.translate(
        "tutorial/sample-problems/LinearAlgebra/MatrixAnswer2.pg",
        seed=1234,
        inputs=correct_answers
    )
    print(f"\nCheck result:")
    print(f"  Score: {check_result.score}")
    if check_result.answer_results:
        for name, ans_result in check_result.answer_results.items():
            print(f"  {name}: score={ans_result.score}, msg={ans_result.answer_message}")

