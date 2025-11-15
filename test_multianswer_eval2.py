import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Parametric/ParametricEquationAnswers.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"MultiAnswer: {multi_eval}")
print(f"correct_answers: {multi_eval.correct_answers}")
print(f"checker: {multi_eval.checker}")

# Get the evaluator
evaluator = multi_eval.cmp()
print(f"\nEvaluator: {evaluator}")
print(f"Has .evaluate(): {hasattr(evaluator, 'evaluate')}")
print(f"Has .check(): {hasattr(evaluator, 'check')}")

# Test evaluate
student_answers = ['cos(t)', 'sin(t)', '0', '1.0471975511965976']
print(f"\nStudent answers: {student_answers}")

eval_result = evaluator.evaluate(*student_answers)
print(f"Evaluate result: {eval_result}")

# The issue: when checker is None, it does string comparison
# But Formula objects need proper checking
print(f"\nTesting string comparison:")
for correct, student in zip(multi_eval.correct_answers, student_answers):
    print(f"  {correct} == {student}: {str(correct) == str(student)}")
    print(f"    str(correct): {str(correct)}")
    print(f"    str(student): {str(student)}")

