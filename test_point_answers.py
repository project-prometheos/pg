import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
problem_path = "tutorial/sample-problems/Algebra/PointAnswers.pg"

# Step 1: Generate problem
print("=" * 70)
print("Step 1: Generate problem")
print("=" * 70)
result = translator.translate(problem_path, seed=1234)
print(f"Answer blanks: {list(result.answer_blanks.keys())}")

# Check evaluator types
for name, info in result.answer_blanks.items():
    evaluator = info['evaluator']['ans_eval']
    print(f"\n{name}:")
    print(f"  Type: {type(evaluator).__name__}")
    print(f"  Evaluator: {evaluator}")
    if hasattr(evaluator, 'elements'):
        print(f"  Elements: {evaluator.elements}")

# Step 2: Extract correct answers
print("\n" + "=" * 70)
print("Step 2: Extract correct answers")
print("=" * 70)
correct_answers = extract_correct_answers(result)
print(f"Extracted answers: {correct_answers}")

# Step 3: Check answers
print("\n" + "=" * 70)
print("Step 3: Check answers")
print("=" * 70)
check_result = translator.translate(problem_path, seed=1234, inputs=correct_answers)
print(f"Score: {check_result.score}")

if check_result.answer_results:
    for name, ans_result in check_result.answer_results.items():
        print(f"\n{name}:")
        print(f"  score={ans_result.score}")
        print(f"  correct={ans_result.correct}")
        print(f"  error_flag={ans_result.error_flag}")
        if ans_result.error_flag:
            print(f"  ERROR: {ans_result.error_message}")
        if ans_result.answer_message:
            print(f"  message: {ans_result.answer_message}")
        print(f"  student_value={ans_result.student_value}")
        print(f"  correct_value={ans_result.correct_value}")
        print(f"  typeError={ans_result.typeError}")

