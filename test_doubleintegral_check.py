import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/IntegralCalc/DoubleIntegral.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
evaluator = multi_eval.cmp()

# Test with correct answers
student_answers = ['x*y', 'd*x', 'd*y', '1', '2', '4', '5']
print(f"Student answers: {student_answers}")

eval_result = evaluator.evaluate(*student_answers)
print(f"Evaluate result: {eval_result}")

# Test individual Formula checking
print(f"\nTesting Formula checking:")
formula = multi_eval.correct_answers[0]  # x*y
print(f"Formula: {formula}")
print(f"Has .cmp(): {hasattr(formula, 'cmp')}")

if hasattr(formula, 'cmp'):
    checker = formula.cmp()
    print(f"Checker: {type(checker).__name__}")
    if hasattr(checker, 'check'):
        result = checker.check('x*y')
        print(f"Check 'x*y': {result}")

