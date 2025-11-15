import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator
from pg.answer import AnswerResult

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Algebra/ExpandedPolynomial.pg", seed=1234)

evaluator = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
student_answer = "x**2 - 6*x + 4"

print(f"Evaluator: {evaluator}")
print(f"Student answer: {student_answer}")

ans_result = AnswerResult(
    original_student_answer=student_answer,
    ans_label='AnSwEr0001',
    type=f"Value ({type(evaluator).__name__})",
    correct_answer=str(evaluator),
)

print(f"\nBefore _cmp_parse:")
print(f"  student_value: {ans_result.student_value}")
print(f"  correct_value: {ans_result.correct_value}")

ans_result = translator._cmp_parse(evaluator, student_answer, ans_result)

print(f"\nAfter _cmp_parse:")
print(f"  student_value: {ans_result.student_value}")
print(f"  correct_value: {ans_result.correct_value}")
print(f"  student_formula: {ans_result.student_formula}")
print(f"  error_flag: {ans_result.error_flag}")
print(f"  error_message: {ans_result.error_message}")

