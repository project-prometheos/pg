import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.translator.tests.answer_extraction import extract_correct_answers

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg", seed=1234)

# Test the checker directly
multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
vector_ans = multi_eval.answers[0]
checker = vector_ans.cmp()

student_answer = '<(4, 0) + t * <-4, 2>>'
print(f"Student answer: {student_answer}")
print(f"Correct vector: {vector_ans}")

result = checker.check(student_answer)
print(f"Check result: {result}")

# Now test full translation
problem_result = translator.translate("tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg", seed=1234)
correct_answers = extract_correct_answers(problem_result)
print(f"\nExtracted answers: {correct_answers}")

check_result = translator.translate(
    "tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg",
    seed=1234,
    inputs=correct_answers
)

print(f"\nFull check result:")
print(f"  Score: {check_result.score}")
if check_result.answer_results:
    for name, ans_result in check_result.answer_results.items():
        print(f"  {name}: score={ans_result.score}, msg={ans_result.answer_message}")

