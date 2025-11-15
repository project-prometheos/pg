import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/VectorCalc/VectorLineSegment1.pg", seed=1234)

multi_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"MultiAnswer type: {type(multi_eval).__name__}")
print(f"Has correct_answers: {hasattr(multi_eval, 'correct_answers')}")
if hasattr(multi_eval, 'correct_answers'):
    print(f"correct_answers: {multi_eval.correct_answers}")
    for i, ans in enumerate(multi_eval.correct_answers):
        print(f"  [{i}]: {ans} (type: {type(ans).__name__})")

print(f"\nAll attributes:")
attrs = [a for a in dir(multi_eval) if not a.startswith('_')]
for attr in attrs:
    try:
        value = getattr(multi_eval, attr)
        if not callable(value):
            print(f"  {attr}: {value}")
    except:
        pass

