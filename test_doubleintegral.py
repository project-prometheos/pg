import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/IntegralCalc/DoubleIntegral.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"MultiAnswer: {multi_eval}")
print(f"correct_answers: {multi_eval.correct_answers}")
print(f"checker: {multi_eval.checker}")

# The extracted answers were: 'x*y', 'd*x', 'd*y'
# But 'd*x' and 'd*y' look wrong - they might be part of the integrand
print(f"\nChecking what the answers actually are:")
for i, ans in enumerate(multi_eval.correct_answers):
    print(f"  [{i}]: {ans} (type: {type(ans).__name__})")

