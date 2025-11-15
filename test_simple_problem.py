import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test a simple problem
problem = "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg"

print(f"Testing {problem}")
result = translator.translate(problem, seed=1234)
print(f"Answer blanks: {list(result.answer_blanks.keys())}")

correct_answers = extract_correct_answers(result)
print(f"Extracted answers: {correct_answers}")

if correct_answers:
    check_result = translator.translate(problem, seed=1234, inputs=correct_answers)
    print(f"Check score: {check_result.score}")
    if check_result.answer_results:
        for name, ans_result in check_result.answer_results.items():
            print(f"  {name}: score={ans_result.score}, correct={ans_result.correct}")
            if ans_result.error_flag:
                print(f"    ERROR: {ans_result.error_message}")
            if ans_result.student_value is None:
                print(f"    WARNING: student_value is None")
            if ans_result.correct_value is None:
                print(f"    WARNING: correct_value is None")

