import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "packages"))

from pg.translator import PGTranslator

translator = PGTranslator()
result = translator.translate("tutorial/sample-problems/Algebra/PointAnswers.pg", seed=1234)

list_eval = result.answer_blanks['AnSwEr0001']['evaluator']['ans_eval']
print(f"List evaluator type: {type(list_eval).__name__}")
print(f"\nDirect methods:")
print(f"  has .cmp(): {hasattr(list_eval, 'cmp')}")
print(f"  has .check(): {hasattr(list_eval, 'check')}")
print(f"  has .evaluate(): {hasattr(list_eval, 'evaluate')}")

print(f"\nTrying .cmp():")
checker = list_eval.cmp()
print(f"  checker type: {type(checker).__name__}")
print(f"  checker is same object: {checker is list_eval}")
print(f"  checker has .check(): {hasattr(checker, 'check')}")
print(f"  checker has .evaluate(): {hasattr(checker, 'evaluate')}")

print(f"\nAll methods on checker:")
methods = [m for m in dir(checker) if not m.startswith('_')]
for m in methods:
    attr = getattr(checker, m)
    if callable(attr):
        print(f"  {m}()")

