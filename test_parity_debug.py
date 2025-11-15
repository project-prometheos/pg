import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()

# Test a problem that was passing before
problem = "tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg"

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
            print(f"  {name}:")
            print(f"    score={ans_result.score}")
            print(f"    correct={ans_result.correct}")
            print(f"    error_flag={ans_result.error_flag}")
            print(f"    error_message={ans_result.error_message}")
            print(f"    answer_message={ans_result.answer_message}")
            print(f"    student_value={ans_result.student_value}")
            print(f"    correct_value={ans_result.correct_value}")
    if check_result.errors:
        print(f"Errors: {check_result.errors}")

